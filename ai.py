"""OpenAI / ChatGPT helpers for Picky. Keys load from env or Streamlit secrets."""

from __future__ import annotations

import os
from functools import lru_cache

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_openai_api_key() -> str:
    """Resolve OPENAI_API_KEY from environment or Streamlit secrets (never hardcode)."""
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if key:
        return key
    try:
        import streamlit as st

        secrets = getattr(st, "secrets", None)
        if secrets is not None and "OPENAI_API_KEY" in secrets:
            return str(secrets["OPENAI_API_KEY"]).strip()
    except Exception:
        pass
    return ""


def openai_configured() -> bool:
    return bool(get_openai_api_key())


@lru_cache(maxsize=1)
def get_openai_client():
    """Return an OpenAI client or None if the key / package is missing."""
    key = get_openai_api_key()
    if not key:
        return None
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "Install the openai package: python -m pip install openai"
        ) from exc
    return OpenAI(api_key=key)


def chat_complete(
    messages: list[dict[str, str]],
    *,
    model: str = "gpt-4o-mini",
    temperature: float = 0.4,
    max_tokens: int = 650,
) -> str:
    """Send a chat completion and return the assistant text."""
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        store=False,
    )
    choice = response.choices[0].message.content if response.choices else ""
    return (choice or "").strip()

def get_scout_access_code() -> str:
    """Optional private research access gate for publicly hosted deployments.

    If unset, AI Scout remains disabled to prevent anonymous visitors from
    spending the owner's API credits. Never expose this value in a UI.
    """
    value = (os.getenv("PICKY_AI_SCOUT_ACCESS_CODE") or "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get("PICKY_AI_SCOUT_ACCESS_CODE", "")).strip()
    except Exception:
        return ""


def scout_access_granted(submitted: str) -> bool:
    """Compare secret phrases without returning the configured value."""
    from hmac import compare_digest
    configured = get_scout_access_code()
    return bool(configured and submitted and compare_digest(configured, submitted))

