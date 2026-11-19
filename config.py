"""Local Picky config — secrets and test draft URL from env / Streamlit secrets."""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _secret(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if value:
        return value
    try:
        import streamlit as st

        secrets = getattr(st, "secrets", None)
        if secrets is not None and name in secrets:
            return str(secrets[name]).strip()
    except Exception:
        pass
    return ""


def default_draft_url() -> str:
    """Base draft used for local testing. Set PICKY_DEFAULT_DRAFT_URL in .env (gitignored)."""
    return _secret("PICKY_DEFAULT_DRAFT_URL")
