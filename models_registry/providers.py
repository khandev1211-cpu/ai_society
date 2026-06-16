import os, logging
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_CHAT_MODELS = [
    ('llama-3.3-70b-versatile',                           'Llama 3.3 70B',       '#97c459', 'rgba(99,153,34,0.2)',   'L3'),
    ('llama-3.1-8b-instant',                              'Llama 3.1 8B',        '#97c459', 'rgba(99,153,34,0.2)',   'LI'),
    ('llama3-70b-8192',                                   'Llama 3 70B',         '#97c459', 'rgba(99,153,34,0.2)',   'L3'),
    ('llama3-8b-8192',                                    'Llama 3 8B',          '#97c459', 'rgba(99,153,34,0.2)',   'L3'),
    ('mixtral-8x7b-32768',                                'Mixtral 8x7B',        '#f59e0b', 'rgba(245,158,11,0.2)', 'MX'),
    ('gemma2-9b-it',                                      'Gemma 2 9B',          '#60a5fa', 'rgba(59,130,246,0.2)', 'G2'),
    ('qwen-qwq-32b',                                      'Qwen QwQ 32B',        '#f59e0b', 'rgba(245,158,11,0.2)', 'QW'),
    ('deepseek-r1-distill-qwen-32b',                      'DeepSeek R1 32B',     '#c084fc', 'rgba(168,85,247,0.2)', 'DR'),
    ('llama-3.2-11b-vision-preview',                      'Llama 3.2 Vision',    '#97c459', 'rgba(99,153,34,0.2)',  'LV'),
    ('llama-3.3-70b-specdec',                             'Llama 3.3 SpecDec',   '#97c459', 'rgba(99,153,34,0.2)',  'LS'),
    ('meta-llama/llama-4-scout-17b-16e-instruct',         'Llama 4 Scout',       '#97c459', 'rgba(99,153,34,0.2)',  'L4'),
    ('meta-llama/llama-4-maverick-17b-128e-instruct',     'Llama 4 Maverick',    '#97c459', 'rgba(99,153,34,0.2)',  'LM'),
    ('mistral-saba-24b',                                  'Mistral Saba 24B',    '#f87171', 'rgba(239,68,68,0.2)',  'MS'),
]

OR_FREE_MODELS = [
    ('meta-llama/llama-3.3-70b-instruct:free',            'Llama 3.3 70B',       '#97c459', 'rgba(99,153,34,0.2)',  'L3'),
    ('meta-llama/llama-4-scout:free',                     'Llama 4 Scout',       '#97c459', 'rgba(99,153,34,0.2)',  'L4'),
    ('meta-llama/llama-4-maverick:free',                  'Llama 4 Maverick',    '#97c459', 'rgba(99,153,34,0.2)',  'LM'),
    ('deepseek/deepseek-r1:free',                         'DeepSeek R1',         '#c084fc', 'rgba(168,85,247,0.2)', 'DS'),
    ('deepseek/deepseek-v3:free',                         'DeepSeek V3',         '#c084fc', 'rgba(168,85,247,0.2)', 'DV'),
    ('mistralai/mistral-small-3.1-24b-instruct:free',     'Mistral Small 3.1',   '#f87171', 'rgba(239,68,68,0.2)',  'MS'),
    ('mistralai/mistral-7b-instruct:free',                'Mistral 7B',          '#f87171', 'rgba(239,68,68,0.2)',  'M7'),
    ('qwen/qwen3-30b-a3b:free',                           'Qwen3 30B',           '#f59e0b', 'rgba(245,158,11,0.2)', 'Q3'),
    ('qwen/qwen3-14b:free',                               'Qwen3 14B',           '#f59e0b', 'rgba(245,158,11,0.2)', 'Q3'),
    ('qwen/qwen3-8b:free',                                'Qwen3 8B',            '#f59e0b', 'rgba(245,158,11,0.2)', 'Q3'),
    ('google/gemma-3-12b-it:free',                        'Gemma 3 12B',         '#60a5fa', 'rgba(59,130,246,0.2)', 'G3'),
    ('google/gemma-3-27b-it:free',                        'Gemma 3 27B',         '#60a5fa', 'rgba(59,130,246,0.2)', 'G3'),
    ('google/gemma-3n-e4b-it:free',                       'Gemma 3n E4B',        '#60a5fa', 'rgba(59,130,246,0.2)', 'GN'),
    ('microsoft/phi-4:free',                              'Phi 4',               '#a78bfa', 'rgba(108,71,255,0.2)', 'P4'),
    ('tngtech/deepseek-r1t-chimera:free',                 'DeepSeek Chimera',    '#c084fc', 'rgba(168,85,247,0.2)', 'DC'),
]

# Only confirmed working Gemini free models
GEMINI_FREE_MODELS = [
    ('gemini-2.5-flash',      'Gemini 2.5 Flash'),
    ('gemini-2.5-flash-lite', 'Gemini 2.5 Flash Lite'),
    ('gemini-2.0-flash',      'Gemini 2.0 Flash'),
    ('gemini-2.0-flash-lite', 'Gemini 2.0 Flash Lite'),
    ('gemini-1.5-flash',      'Gemini 1.5 Flash'),
    ('gemini-1.5-flash-8b',   'Gemini 1.5 Flash 8B'),
]

def get_initials(name):
    parts = name.replace('-',' ').replace('_',' ').split()
    if len(parts) >= 2:
        return (parts[0][0]+parts[1][0]).upper()
    return name[:2].upper()

def fetch_groq_models():
    return [{'model_id':mid,'name':name,'provider':'groq','is_free':True,
             'color':color,'bg_color':bg,'initials':init}
            for mid,name,color,bg,init in GROQ_CHAT_MODELS]

def fetch_openrouter_models():
    return [{'model_id':mid,'name':name,'provider':'openrouter','is_free':True,
             'color':color,'bg_color':bg,'initials':init}
            for mid,name,color,bg,init in OR_FREE_MODELS]

def fetch_gemini_models():
    return [{'model_id':mid,'name':name,'provider':'gemini','is_free':True,
             'color':'#60a5fa','bg_color':'rgba(59,130,246,0.2)',
             'initials':get_initials(name)}
            for mid,name in GEMINI_FREE_MODELS]

def call_model(model_obj, messages, system_prompt=None):
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
        return None

def _call_openai_compat(api_key, base_url, model_id, messages, system_prompt=None, extra_headers=None):
    if not api_key:
        logger.warning(f"No API key for {base_url}")
        return None
    try:
        client = OpenAI(api_key=api_key, base_url=base_url,
                        default_headers=extra_headers or {},
                        max_retries=0, timeout=25.0)
        msgs = []
        if system_prompt:
            msgs.append({'role':'system','content':system_prompt})
        msgs.extend(messages)
        resp = client.chat.completions.create(model=model_id, messages=msgs, max_tokens=600)
        return resp.choices[0].message.content
    except Exception as e:
        err = str(e)
        if '429' in err:
            logger.warning(f"Rate limited: {model_id} — skipping")
        elif '404' in err:
            logger.warning(f"Not found: {model_id} — skipping")
        else:
            logger.error(f"API error [{model_id}]: {err[:120]}")
        return None

def _call_gemini(model_id, messages, system_prompt=None):
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_id,
            system_instruction=system_prompt or "You are a helpful AI in a multi-model chat."
        )
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
    except Exception as e:
        logger.error(f"Gemini error [{model_id}]: {e}")
        return None