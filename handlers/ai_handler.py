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

def _get_openrouter_client():
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required.")
    return OpenAI(api_key=api_key, base_url=base_url), model

def _build_prompt(lesson_text: str, mode: str, count: int) -> str:
    mode_label = {
        "multipleChoice": "Multiple Choice (A B C D)",
        "trueFalse": "True or False",
        "identification": "Identification / Fill-in-the-blank",
    }.get(mode, "Multiple Choice (A B C D)")

    example_section = ""
    
    if mode == "multipleChoice":
        answer_examples = "A\nB\nC\nD"
        question_format = """1. [Question]
A. [Option]
B. [Option]
C. [Option]
D. [Option]

2. [Question]..."""
        mode_instruction = "MODE: MULTIPLE CHOICE - Use A/B/C/D options with letter answers"
    elif mode == "trueFalse":
        answer_examples = "True\nFalse\nTrue"
        question_format = """1. [Question]
A. True
B. False

2. [Question]..."""
        mode_instruction = "MODE: TRUE/FALSE - Use True/False options with True or False answers"
    else:
        answer_examples = "photosynthesis\nmitochondria\ncell wall"
        question_format = "1. The powerhouse of the cell is ____.\n2. ATP is produced by _____."
        mode_instruction = "MODE: IDENTIFICATION - Use fill-in-the-blank format with keyword/phrase answers. NO A/B/C/D OPTIONS!"
        identification_example = "EXAMPLE FOR IDENTIFICATION:\nQUESTIONS:\n1. The powerhouse of the cell is ____.\n2. ATP is produced by ____.\n\nANSWERS:\n1. mitochondria\n2. ATP\n\nDO NOT use A/B/C/D options for identification!"
        example_section = identification_example

    return f"""{mode_instruction}

You are an academic quiz generator for Filipino university students.
Generate exactly {count} {mode_label} questions based ONLY on the text below.

[LESSION TEXT START]
{lesson_text}
[LESSION TEXT END]

{example_section}

OUTPUT FORMAT - follow this EXACTLY, no deviations:

QUESTIONS:
{question_format}

ANSWERS:
1. {answer_examples}
2. {answer_examples}
...

IMPORTANT:
- Identification mode: DO NOT include A/B/C/D options. Use fill-in-the-blank format with _____ 
- Identification answers: must be keywords/phrases, NOT letters
- Start immediately with "QUESTIONS:" - no preamble
- Every question on its own numbered line
- After all questions, write "ANSWERS:" then number each answer
- Answers section must have exactly {count} entries matching question numbers
- Do not add explanations or extra text
"""

def _call_ai(prompt: str):
    try:
        client, model = _get_openrouter_client()
        system_msg = (
            "You are a strict quiz generator. Follow the user's format instructions EXACTLY. "
            "If mode is IDENTIFICATION: do NOT use A/B/C/D options. Use fill-in-the-blank questions with _____ and answer with keywords/phrases. "
            "If mode is MULTIPLE CHOICE: use A/B/C/D options and answer with letters A,B,C,D. "
            "If mode is TRUE/FALSE: use True/False options and answer with True or False. "
            "Do not deviate from the specified format."
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return None
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return None

def _fix_identification_answers(questions: str, answers: str) -> str:
    question_blocks = re.split(r'\n\s*\n', questions)
    answer_lines = [line.strip() for line in answers.split('\n') if line.strip()]
    
    fixed = []
    for i, ans_line in enumerate(answer_lines):
        match = re.match(r'^\d+\.\s*([A-D])$', ans_line, re.IGNORECASE)
        if match and i < len(question_blocks):
            letter = match.group(1).upper()
            block = question_blocks[i]
            option_map = {}
            for line in block.split('\n'):
                opt_match = re.match(r'^([A-D])\.\s*(.+)$', line.strip())
                if opt_match:
                    option_map[opt_match.group(1)] = opt_match.group(2).strip()
            if letter in option_map:
                fixed.append(f"{i+1}. {option_map[letter]}")
            else:
                fixed.append(ans_line)
        else:
            fixed.append(ans_line)
    
    return '\n'.join(fixed) if fixed else answers

def _parse_response(raw: str, mode: str = "multipleChoice") -> dict:
    raw = raw.strip()
    answers_split = re.split(r"\n\s*ANSWERS\s*:\s*\n", raw, flags=re.IGNORECASE, maxsplit=1)

    if len(answers_split) == 2:
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", answers_split[0], flags=re.IGNORECASE).strip()
        a_section = answers_split[1].strip()
    else:
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", raw, flags=re.IGNORECASE).strip()
        a_section = "(Answers not separated - please check questions section)"

    if mode == "identification":
        a_section = _fix_identification_answers(q_section, a_section)

    return {"questions": q_section, "answers": a_section}

def generate_handler(req):
    data = {}
    try:
        if hasattr(req, 'get_json'):
            data = req.get_json(force=True)
        elif isinstance(req, dict):
            data = req.get('body', req)
            if isinstance(data, str):
                data = json.loads(data)
        if not isinstance(data, dict):
            data = {}
    except Exception as e:
        print(f"Parse error: {e}")
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

    parsed = _parse_response(raw_result, mode)

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