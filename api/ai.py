"""
FRES AI Endpoint - Vercel Serverless Function
"""
import os
import sys
import re
import logging

sys.path.insert(0, os.path.dirname(__file__))

from openai import OpenAI

from base import get_db, parse_body, success_response, error_response, cors_preflight

logger = logging.getLogger("FRES.ai")

# OpenRouter configuration
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def _build_prompt(lesson_text: str, mode: str, count: int) -> str:
    """Build the prompt for quiz generation."""
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
    """Call AI using OpenRouter API (OpenAI-compatible)."""
    try:
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an academic quiz generator for Filipino university students. Always follow the exact format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
        )

        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            if result:
                return result.strip()
        return None

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate_limit" in error_msg.lower():
            logger.error(
                "OpenRouter rate limit exceeded. "
                "Free tier: 50 requests/day. Wait or upgrade at https://openrouter.ai"
            )
        else:
            logger.error(f"OpenRouter API error: {e}", exc_info=True)
        return None


def _parse_response(raw: str) -> dict:
    """Split the AI response into questions and answers sections."""
    raw = raw.strip()
    answers_split = re.split(r"\n\s*ANSWERS\s*:\s*\n", raw, flags=re.IGNORECASE, maxsplit=1)

    if len(answers_split) == 2:
        q_section = answers_split[0].strip()
        a_section = answers_split[1].strip()
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", q_section, flags=re.IGNORECASE).strip()
    else:
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", raw, flags=re.IGNORECASE).strip()
        a_section = "(Answers not separated — please check questions section)"

    return {"questions": q_section, "answers": a_section}


def generate(event):
    """Handle /api/ai/generate requests."""
    data = parse_body(event)

    lesson_text = (data.get("lesson_text") or data.get("prompt") or "").strip()
    mode = data.get("type", "multipleChoice")
    count = int(data.get("count", 10))
    user_id = data.get("user_id")
    prompt_override = data.get("prompt_override")

    if not lesson_text and not prompt_override:
        return error_response("Missing input text for generation.", 400)

    final_prompt = prompt_override if prompt_override else _build_prompt(lesson_text, mode, count)
    raw_result = _call_ai(final_prompt)

    if raw_result is None:
        return error_response(
            "AI connection failed. Check your API key or rate limits. "
            "Free tier: 50 requests/day. Get a key at https://openrouter.ai",
            503
        )

    parsed = _parse_response(raw_result)

    # Log to database
    try:
        db = get_db()
        db.execute(
            "INSERT INTO chat_logs (user_id, prompt, response) VALUES (?, ?, ?)",
            (user_id, (lesson_text or final_prompt)[:500], raw_result[:2000])
        )
        db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"DB log failed: {e}")

    return success_response({
        "questions": parsed["questions"],
        "answers": parsed["answers"],
        "raw": raw_result
    })


def get_logs(event):
    """Handle /api/ai/logs requests."""
    db = get_db()
    rows = db.execute(
        "SELECT id, user_id, prompt, created_at FROM chat_logs ORDER BY id DESC LIMIT 50"
    ).fetchall()
    db.close()
    return success_response({"logs": [dict(r) for r in rows]})


def handler(event, context):
    """Main entry point for Vercel serverless function."""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_preflight(event)

    # Route to appropriate handler
    path = event.get("path", "")

    if event.get("httpMethod") == "GET" and "logs" in path:
        return get_logs(event)
    elif event.get("httpMethod") == "POST":
        return generate(event)
    else:
        return error_response("Method not allowed", 405)
