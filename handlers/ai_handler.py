"""
FRES AI Handler — OpenRouter AI Integration (OpenAI-compatible API)
/api/ai/generate
/api/ai/logs

OpenRouter provides FREE models with generous limits:
- 50 requests/day free (no expiration)
- 20 requests/minute rate limit
- Multiple free models available (Qwen, NVIDIA, etc.)
- Get API key at: https://openrouter.ai
"""
import os
import json

import logging
import re
from openai import OpenAI

logger = logging.getLogger("FRES.ai")

# OpenRouter configuration
# Free models: https://openrouter.ai/openrouter/free
# Recommended free model: "openrouter/auto" or specific like "qwen/qwen-2.5-72b-instruct:free"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def _get_openrouter_client():
    """Initialize and return the OpenRouter client."""
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is not set!")
        raise ValueError("OPENROUTER_API_KEY environment variable is required. Get one at https://openrouter.ai")
    
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )
def _build_prompt(lesson_text: str, mode: str, count: int) -> str:
    mode_label = {
        "multipleChoice":  "Multiple Choice (A B C D)",
        "trueFalse":       "True or False",
        "identification":  "Identification / Fill-in-the-blank",
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
        client = _get_openrouter_client()
        
        # Generate content using OpenRouter
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
        
        # Extract and return the text response
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            if result:
                return result.strip()
        return None
        
    except Exception as e:
        error_msg = str(e)
        
        # Check for rate limit / quota errors
        if "429" in error_msg or "rate_limit" in error_msg.lower():
            logger.error(
                "OpenRouter rate limit exceeded. "
                "Free tier: 50 requests/day. Wait or upgrade at https://openrouter.ai"
            )
        else:
            logger.error(f"OpenRouter API error: {e}", exc_info=True)
        
        return None

def _parse_response(raw: str) -> dict:
    """
    Split the Gemini response into questions section and answers section.
    """
    raw = raw.strip()

    # Split using the "ANSWERS:" header as a delimiter
    answers_split = re.split(r"\n\s*ANSWERS\s*:\s*\n", raw, flags=re.IGNORECASE, maxsplit=1)

    if len(answers_split) == 2:
        q_section = answers_split[0].strip()
        a_section = answers_split[1].strip()

        # Remove the "QUESTIONS:" header from the start if it exists
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", q_section, flags=re.IGNORECASE).strip()
    else:
        # Fallback if Gemini fails to include the header
        q_section = re.sub(r"^QUESTIONS\s*:\s*\n?", "", raw, flags=re.IGNORECASE).strip()
        a_section = "(Answers not separated — please check questions section)"

    return {"questions": q_section, "answers": a_section}

# ─── Route Handlers ──────────────────────────────────────────────────────────

def generate(handler, match):
    data = handler.body

    # Accept structured fields from generator.js
    lesson_text     = (data.get("lesson_text") or data.get("prompt") or "").strip()
    mode            = data.get("type", "multipleChoice")
    count           = int(data.get("count", 10))
    user_id         = data.get("user_id")
    prompt_override  = data.get("prompt_override")

    if not lesson_text and not prompt_override:
        return handler._send_json(
            {"success": False, "error": "Missing input text for generation."}, 400
        )

    # Use existing prompt if provided by frontend, otherwise build new one
    final_prompt = prompt_override if prompt_override else _build_prompt(lesson_text, mode, count)

    raw_result = _call_ai(final_prompt)
    if raw_result is None:
        return handler._send_json(
            {
                "success": False, 
                "error": "AI connection failed. Check your API key or rate limits. "
                         "Free tier: 50 requests/day. Get a key at https://openrouter.ai"
            }, 
            503
        )

    # This call will now work because _parse_response is defined above!
    parsed = _parse_response(raw_result)

    # Log to database
    try:
        handler.db.execute(
            "INSERT INTO chat_logs (user_id, prompt, response) VALUES (?, ?, ?)",
            (user_id, (lesson_text or final_prompt)[:500], raw_result[:2000])
        )
        handler.db.commit()
    except Exception as e:
        logger.warning(f"DB log failed: {e}")

    return handler._send_json({
        "success":   True,
        "questions": parsed["questions"],
        "answers":   parsed["answers"],
        "raw":       raw_result
    })

def get_logs(handler, match):
    rows = handler.db.execute(
        "SELECT id, user_id, prompt, created_at FROM chat_logs ORDER BY id DESC LIMIT 50"
    ).fetchall()
    return handler._send_json([dict(r) for r in rows])