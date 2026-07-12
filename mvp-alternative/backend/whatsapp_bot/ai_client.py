"""Client unifié OpenAI / Gemini pour le diagnostic."""

import json
from typing import Optional
from config import get_settings


def _call_openai(messages: list[dict], temperature: float, max_tokens: int) -> Optional[str]:
    from openai import OpenAI
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _call_gemini(messages: list[dict], temperature: float, max_tokens: int) -> Optional[str]:
    from google import genai
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    client = genai.Client(api_key=settings.gemini_api_key)

    # Convertir les messages OpenAI en format Gemini
    system_msg = None
    user_contents = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            user_contents.append(m["content"])

    full_prompt = ""
    if system_msg:
        full_prompt += system_msg + "\n\n"
    full_prompt += "\n".join(user_contents)

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=full_prompt,
        config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
        },
    )
    return response.text


def get_completion(messages: list[dict], temperature: float = 0.3, max_tokens: int = 1000) -> Optional[dict]:
    """Appelle le LLM configuré (OpenAI ou Gemini) et retourne un dict JSON."""
    settings = get_settings()
    provider = settings.ai_provider

    if provider == "gemini":
        content = _call_gemini(messages, temperature, max_tokens)
    else:
        content = _call_openai(messages, temperature, max_tokens)

    if not content:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
