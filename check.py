"""
AI Society — Model Health Checker
Tests all models from Groq, OpenRouter, and Gemini
and reports which ones actually work.

Usage:
    python check_models.py

Output:
    ✅ working models saved to: working_models.txt
    ❌ dead models saved to: dead_models.txt
"""

import os, time, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY       = os.getenv('GROQ_API_KEY', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
GEMINI_API_KEY     = os.getenv('GEMINI_API_KEY', '')

TEST_PROMPT = "Say exactly: I am working fine."

# ── All models to test ──────────────────────────────────────────────

GROQ_CHAT_MODELS = [
    ('llama-3.3-70b-versatile', 'llama-3.3-70b-versatile', '#97c459', 'rgba(99,153,34,0.2)', 'L3'),
    ('llama-3.1-8b-instant', 'llama-3.1-8b-instant', '#97c459', 'rgba(99,153,34,0.2)', 'L3'),
    ('meta-llama/llama-4-scout-17b-16e-instruct', 'llama-4-scout-17b-16e-instruct', '#97c459', 'rgba(99,153,34,0.2)', 'L3'),
    ('compound-beta', 'compound-beta', '#97c459', 'rgba(99,153,34,0.2)', 'L3'),
    ('gpt-oss120b', 'gpt-oss120b', '#f87171', 'rgba(239,68,68,0.2)', 'GPT-OSS'),
]

GEMINI_FREE_MODELS = [
    ('gemini-2.5-flash', 'gemini-2.5-flash'),
    ('gemini-2.5-flash-lite', 'gemini-2.5-flash-lite'),
    ('gemini-1.5-flash', 'gemini-1.5-flash'),
]

# ── Colors ──────────────────────────────────────────────────────────

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

# ── Test functions ───────────────────────────────────────────────────

def test_groq(model_id):
    if not GROQ_API_KEY:
        return False, 'No GROQ_API_KEY'
    try:
        client = OpenAI(api_key=GROQ_API_KEY,
                        base_url='https://api.groq.com/openai/v1',
                        max_retries=0, timeout=15.0)
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{'role':'user','content':TEST_PROMPT}],
            max_tokens=30
        )
        text = resp.choices[0].message.content
        return True, text[:60]
    except Exception as e:
        err = str(e)
        if '400' in err and 'decommissioned' in err:
            return False, 'DECOMMISSIONED'
        if '429' in err:
            return False, 'RATE_LIMITED'
        if '404' in err:
            return False, 'NOT_FOUND'
        return False, err[:80]

def test_openrouter(model_id):
    if not OPENROUTER_API_KEY:
        return False, 'No OPENROUTER_API_KEY'
    try:
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url='https://openrouter.ai/api/v1',
            default_headers={'HTTP-Referer':'https://ai-society.app','X-Title':'AI Society'},
            max_retries=0, timeout=20.0
        )
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{'role':'user','content':TEST_PROMPT}],
            max_tokens=30
        )
        text = resp.choices[0].message.content
        return True, text[:60]
    except Exception as e:
        err = str(e)
        if '429' in err:
            return False, 'RATE_LIMITED'
        if '404' in err:
            return False, 'NOT_FOUND'
        if '402' in err:
            return False, 'PAID_ONLY'
        return False, err[:80]

def test_gemini(model_id):
    if not GEMINI_API_KEY:
        return False, 'No GEMINI_API_KEY'
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_id)
        resp = model.generate_content(TEST_PROMPT)
        return True, resp.text[:60]
    except Exception as e:
        err = str(e)
        if '429' in err:
            return False, 'RATE_LIMITED (quota exceeded)'
        if '404' in err:
            return False, 'NOT_FOUND'
        if '400' in err:
            return False, 'BAD_REQUEST'
        return False, err[:80]

# ── Main ─────────────────────────────────────────────────────────────

def run():
    working = []
    dead    = []

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  AI Society — Model Health Checker{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    # ── GROQ ──
    if GROQ_API_KEY:
        print(f"{BOLD}{BLUE}▶ Testing Groq ({len(GROQ_MODELS)} models){RESET}")
        for model in GROQ_MODELS:
            print(f"  {YELLOW}Testing{RESET} {model} ...", end=' ', flush=True)
            ok, msg = test_groq(model)
            if ok:
                print(f"{GREEN}✅ WORKING{RESET}  →  {msg}")
                working.append({'provider':'groq','model_id':model,'response':msg})
            else:
                print(f"{RED}❌ {msg}{RESET}")
                dead.append({'provider':'groq','model_id':model,'reason':msg})
            time.sleep(0.5)
    else:
        print(f"{RED}⚠ Skipping Groq — GROQ_API_KEY not set{RESET}")

    print()

    # ── OPENROUTER ──
    if OPENROUTER_API_KEY:
        print(f"{BOLD}{BLUE}▶ Testing OpenRouter ({len(OPENROUTER_MODELS)} models){RESET}")
        for model in OPENROUTER_MODELS:
            print(f"  {YELLOW}Testing{RESET} {model} ...", end=' ', flush=True)
            ok, msg = test_openrouter(model)
            if ok:
                print(f"{GREEN}✅ WORKING{RESET}  →  {msg}")
                working.append({'provider':'openrouter','model_id':model,'response':msg})
            else:
                print(f"{RED}❌ {msg}{RESET}")
                dead.append({'provider':'openrouter','model_id':model,'reason':msg})
            time.sleep(1.0)  # OpenRouter needs a bit more spacing
    else:
        print(f"{RED}⚠ Skipping OpenRouter — OPENROUTER_API_KEY not set{RESET}")

    print()

    # ── GEMINI ──
    if GEMINI_API_KEY:
        print(f"{BOLD}{BLUE}▶ Testing Gemini ({len(GEMINI_MODELS)} models){RESET}")
        for model in GEMINI_MODELS:
            print(f"  {YELLOW}Testing{RESET} {model} ...", end=' ', flush=True)
            ok, msg = test_gemini(model)
            if ok:
                print(f"{GREEN}✅ WORKING{RESET}  →  {msg}")
                working.append({'provider':'gemini','model_id':model,'response':msg})
            else:
                print(f"{RED}❌ {msg}{RESET}")
                dead.append({'provider':'gemini','model_id':model,'reason':msg})
            time.sleep(1.5)  # Gemini free tier is strict on RPM
    else:
        print(f"{RED}⚠ Skipping Gemini — GEMINI_API_KEY not set{RESET}")

    # ── Summary ──
    total = len(working) + len(dead)
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Results: {GREEN}{len(working)} working{RESET} / {RED}{len(dead)} dead{RESET} / {total} tested{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    print(f"{GREEN}{BOLD}✅ Working models:{RESET}")
    for m in working:
        print(f"   [{m['provider'].upper():<12}] {m['model_id']}")

    print(f"\n{RED}{BOLD}❌ Dead models:{RESET}")
    for m in dead:
        print(f"   [{m['provider'].upper():<12}] {m['model_id']}  →  {m['reason']}")

    # ── Save results ──
    with open('working_models.txt', 'w') as f:
        f.write("# Working models — copy these into providers.py\n\n")
        for prov in ['groq', 'openrouter', 'gemini']:
            models = [m for m in working if m['provider'] == prov]
            if models:
                f.write(f"# {prov.upper()}\n")
                for m in models:
                    f.write(f"{m['model_id']}\n")
                f.write("\n")

    with open('dead_models.txt', 'w') as f:
        f.write("# Dead models — remove these from providers.py\n\n")
        for m in dead:
            f.write(f"[{m['provider']}] {m['model_id']} — {m['reason']}\n")

    print(f"\n{BOLD}Results saved:{RESET}")
    print(f"  ✅ working_models.txt")
    print(f"  ❌ dead_models.txt")
    print()

    # ── Also print providers.py snippet for working models ──
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Copy-paste ready for providers.py:{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    groq_working = [m for m in working if m['provider'] == 'groq']
    or_working   = [m for m in working if m['provider'] == 'openrouter']
    gem_working  = [m for m in working if m['provider'] == 'gemini']

    if groq_working:
        print("GROQ_CHAT_MODELS = [")
        for m in groq_working:
            name = m['model_id'].split('/')[-1]
            print(f"    ('{m['model_id']}', '{name}', '#97c459', 'rgba(99,153,34,0.2)', 'L3'),")
        print("]\n")

    if or_working:
        print("OR_FREE_MODELS = [")
        for m in or_working:
            name = m['model_id'].replace(':free','').split('/')[-1]
            print(f"    ('{m['model_id']}', '{name}', '#c084fc', 'rgba(168,85,247,0.2)', 'OR'),")
        print("]\n")

    if gem_working:
        print("GEMINI_FREE_MODELS = [")
        for m in gem_working:
            print(f"    ('{m['model_id']}', '{m['model_id']}'),")
        print("]\n")

if __name__ == '__main__':
    run()