import os, json, logging
from openai import OpenAI
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_COLORS = {
    'llama': ('#97c459', 'rgba(99,153,34,0.2)'),
    'mixtral': ('#f59e0b', 'rgba(245,158,11,0.2)'),
    'gemma': ('#60a5fa', 'rgba(59,130,246,0.2)'),
    'qwen': ('#f59e0b', 'rgba(245,158,11,0.2)'),
    'deepseek': ('#c084fc', 'rgba(168,85,247,0.2)'),
    'default': ('#a78bfa', 'rgba(108,71,255,0.2)'),
}

OR_COLORS = {
    'llama': ('#97c459', 'rgba(99,153,34,0.2)'),
    'mistral': ('#f87171', 'rgba(239,68,68,0.2)'),
    'deepseek': ('#c084fc', 'rgba(168,85,247,0.2)'),
    'qwen': ('#f59e0b', 'rgba(245,158,11,0.2)'),
    'phi': ('#60a5fa', 'rgba(59,130,246,0.2)'),
    'gemma': ('#4ade80', 'rgba(34,197,94,0.2)'),
    'default': ('#a78bfa', 'rgba(108,71,255,0.2)'),
}

def get_color(name, color_map):
    n = name.lower()
    for key, val in color_map.items():
        if key in n:
            return val
    return color_map['default']

def get_initials(name):
    parts = name.replace('-', ' ').replace('_', ' ').split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()

def fetch_groq_models():
    if not settings.GROQ_API_KEY:
        return _default_groq_models()
    try:
        client = OpenAI(api_key=settings.GROQ_API_KEY, base_url='https://api.groq.com/openai/v1')
        models = client.models.list()
        result = []
        for m in models.data:
            color, bg = get_color(m.id, GROQ_COLORS)
            result.append({
                'model_id': m.id, 'name': m.id, 'provider': 'groq',
                'is_free': True, 'color': color, 'bg_color': bg,
                'initials': get_initials(m.id)
            })
        return result
    except Exception as e:
        logger.error(f"Groq fetch error: {e}")
        return _default_groq_models()

def fetch_openrouter_models():
    if not settings.OPENROUTER_API_KEY:
        return _default_or_models()
    try:
        import requests
        r = requests.get('https://openrouter.ai/api/v1/models',
            headers={'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}'}, timeout=10)
        data = r.json()
        result = []
        for m in data.get('data', []):
            mid = m.get('id','')
            pricing = m.get('pricing', {})
            prompt_cost = float(pricing.get('prompt', 1) or 1)
            is_free = prompt_cost == 0 or mid.endswith(':free')
            if not is_free:
                continue
            color, bg = get_color(mid, OR_COLORS)
            free_id = mid if mid.endswith(':free') else mid + ':free'
            result.append({
                'model_id': free_id, 'name': mid.split('/')[-1], 'provider': 'openrouter',
                'is_free': True, 'color': color, 'bg_color': bg,
                'initials': get_initials(mid.split('/')[-1])
            })
        return result[:30]
    except Exception as e:
        logger.error(f"OpenRouter fetch error: {e}")
        return _default_or_models()

def fetch_gemini_models():
    if not settings.GEMINI_API_KEY:
        return _default_gemini_models()
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        result = []
        for m in genai.list_models():
            if 'generateContent' not in m.supported_generation_methods:
                continue
            name = m.name.replace('models/', '')
            is_free = 'flash' in name.lower() or 'lite' in name.lower()
            result.append({
                'model_id': name, 'name': name, 'provider': 'gemini',
                'is_free': is_free, 'color': '#60a5fa', 'bg_color': 'rgba(59,130,246,0.2)',
                'initials': get_initials(name)
            })
        return result
    except Exception as e:
        logger.error(f"Gemini fetch error: {e}")
        return _default_gemini_models()

def _default_groq_models():
    models = [
        'llama-3.3-70b-versatile','llama-3.1-8b-instant','llama3-70b-8192',
        'mixtral-8x7b-32768','gemma2-9b-it','qwen-qwq-32b',
        'deepseek-r1-distill-llama-70b','llama-3.2-90b-vision-preview',
    ]
    return [{'model_id':m,'name':m,'provider':'groq','is_free':True,
             'color':get_color(m,GROQ_COLORS)[0],'bg_color':get_color(m,GROQ_COLORS)[1],
             'initials':get_initials(m)} for m in models]

def _default_or_models():
    models = [
        ('meta-llama/llama-3.3-70b-instruct:free','llama-3.3-70b'),
        ('deepseek/deepseek-r1:free','deepseek-r1'),
        ('mistralai/mistral-small-3.1-24b-instruct:free','mistral-small'),
        ('qwen/qwen3-235b-a22b:free','qwen3-235b'),
        ('google/gemma-3-12b-it:free','gemma-3-12b'),
        ('microsoft/phi-4-reasoning-plus:free','phi-4-reasoning'),
    ]
    return [{'model_id':mid,'name':name,'provider':'openrouter','is_free':True,
             'color':get_color(mid,OR_COLORS)[0],'bg_color':get_color(mid,OR_COLORS)[1],
             'initials':get_initials(name)} for mid,name in models]

def _default_gemini_models():
    models = [
        ('gemini-2.5-flash','gemini-2.5-flash'),
        ('gemini-2.5-flash-lite','gemini-2.5-flash-lite'),
        ('gemini-2.0-flash','gemini-2.0-flash'),
        ('gemini-1.5-flash','gemini-1.5-flash'),
    ]
    return [{'model_id':mid,'name':name,'provider':'gemini','is_free':True,
             'color':'#60a5fa','bg_color':'rgba(59,130,246,0.2)',
             'initials':get_initials(name)} for mid,name in models]

def call_model(model_obj, messages, system_prompt=None):
    """Call any model regardless of provider. Returns response text."""
    try:
        if model_obj.provider == 'groq':
            return _call_openai_compat(
                settings.GROQ_API_KEY,
                'https://api.groq.com/openai/v1',
                model_obj.model_id, messages, system_prompt
            )
        elif model_obj.provider == 'openrouter':
            return _call_openai_compat(
                settings.OPENROUTER_API_KEY,
                'https://openrouter.ai/api/v1',
                model_obj.model_id, messages, system_prompt,
                extra_headers={'HTTP-Referer':'https://ai-society.app','X-Title':'AI Society'}
            )
        elif model_obj.provider == 'gemini':
            return _call_gemini(model_obj.model_id, messages, system_prompt)
    except Exception as e:
        logger.error(f"Model call error [{model_obj.name}]: {e}")
        return f"[{model_obj.name} is temporarily unavailable]"

def _call_openai_compat(api_key, base_url, model_id, messages, system_prompt=None, extra_headers=None):
    if not api_key:
        return f"[API key not configured for {model_id}]"
    client = OpenAI(api_key=api_key, base_url=base_url,
                    default_headers=extra_headers or {})
    msgs = []
    if system_prompt:
        msgs.append({'role':'system','content':system_prompt})
    msgs.extend(messages)
    resp = client.chat.completions.create(model=model_id, messages=msgs, max_tokens=800)
    return resp.choices[0].message.content

def _call_gemini(model_id, messages, system_prompt=None):
    if not settings.GEMINI_API_KEY:
        return "[Gemini API key not configured]"
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_id,
        system_instruction=system_prompt or "You are a helpful AI in a multi-model chat."
    )
    # Convert messages to Gemini format
    history = []
    last_user = ""
    for m in messages:
        if m['role'] == 'user':
            last_user = m['content']
        elif m['role'] == 'assistant':
            history.append({'role':'model','parts':[m['content']]})
    chat = model.start_chat(history=history)
    resp = chat.send_message(last_user or "Hello")
    return resp.text
