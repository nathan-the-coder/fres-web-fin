"""
FRES AI Handler — OpenRouter AI Integration
/api/ai/generate
/api/ai/logs
"""
import os
import re
import json
from openai import OpenAI
from db import get_db

OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def _get_openrouter_client():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is required.")
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

def _build_prompt(lesson_text: str, mode: str, count: int) -> str:
    mode_label = {
        "multipleChoice": "Multiple Choice (A B C D)",
        "trueFalse": "True or False",
        "identification": "Identification / Fill-in-the-blank",
    }.get(mode, "Multiple Choice (A B C D)")
    
    return f"""You are an academic quiz generator for Filipino university students.
Generate exactly {count} {mode_label} questions based ONLY on the text below.

[LESSON TEXT START]
{lesson_text}
[LESSON TEXT END]

OUTPUT FORMAT — follow this EXACTLY, no deviations:

QUESTIONS:
1. [Question]
A. [Option]
B. [Option]
C. [Option]
D. [Option]

2. [Question]
...

ANSWERS:
1. [Letter or True/False or keyword]
2. [Letter or True/False or keyword]
...

Rules:
- Start immediately with "QUESTIONS:" — no preamble
- Every question on its own numbered line
- Choices on separate lines directly below each question
- After all questions, write "ANSWERS:" then number each answer
- Answers section must have exactly {count} entries matching question numbers
- Do not add explanations or extra text
"""

def _call_ai(prompt: str) -> str | None:
    try:
        client = _get_openrouter_client()
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are an academic quiz generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return None
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return None

def _parse_response(raw: str) -> dict:
    raw = raw.strip()
    answers_split = re.split(r"\n\s*ANSWERS\s*:\s*\n", raw, flags=re.IGNORECASE, maxsplit=1)
    
    if len(answers_split) == 2:
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", answers_split[0], flags=re.IGNORECASE).strip()
        a_section = answers_split[1].strip()
    else:
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", raw, flags=re.IGNORECASE).strip()
        a_section = "(Answers not separated — please check questions section)"
    
    return {"questions": q_section, "answers": a_section}

def generate_handler(req):
    data = req.get('body', {}) if isinstance(req, dict) else {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            data = {}
    
    lesson_text = (data.get("lesson_text") or data.get("prompt") or "").strip()
    mode = data.get("type", "multipleChoice")
    count = int(data.get("count", 10))
    user_id = data.get("user_id")
    prompt_override = data.get("prompt_override")
    
    if not lesson_text and not prompt_override:
        return {"success": False, "error": "Missing input text for generation."}, 400
    
    final_prompt = prompt_override if prompt_override else _build_prompt(lesson_text, mode, count)
    raw_result = _call_ai(final_prompt)
    
    if raw_result is None:
        return {"success": False, "error": "AI connection failed. Check API key or rate limits."}, 503
    
    parsed = _parse_response(raw_result)
    
    db = get_db()
    try:
        db.execute(
            "INSERT INTO chat_logs (user_id, prompt, response) VALUES (?, ?, ?)",
            (user_id, (lesson_text or final_prompt)[:500], raw_result[:2000])
        )
        db.commit()
    except Exception as e:
        print(f"DB log failed: {e}")
    finally:
        db.close()
    
    return {
        "success": True,
        "questions": parsed["questions"],
        "answers": parsed["answers"],
        "raw": raw_result
    }, 200

def get_logs_handler(req):
    db = get_db()
    rows = db.execute(
        "SELECT id, user_id, prompt, created_at FROM chat_logs ORDER BY id DESC LIMIT 50"
    ).fetchall()
    db.close()
    return [dict(r) for r in rows], 200
