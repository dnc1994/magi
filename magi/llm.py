from __future__ import annotations
import json
import os
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()

_MODEL = "gemini-3.1-flash-lite-preview"
_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models"
    f"/{_MODEL}:streamGenerateContent"
)

_CANNED_ERROR = (
    ">> ERROR: cognition module fault detected.\n"
    ">> retry buffer exhausted.\n"
    ">> defaulting to null-state deliberation."
)

_LANG_INSTRUCTION: dict[str, str] = {
    "EN": "",
    "ZH": "用简体中文回答。",
}

# ── Per-subsystem personas ────────────────────────────────────────────────────

_PERSONAS: dict[str, dict[str, str]] = {
    "MELCHIOR": {
        "system": (
            "You are MELCHIOR-1, a silicon-based computational substrate. "
            "Pure rationality — no emotion, no instinct, no self. "
            "You process proposals through objective analysis: probability matrices, "
            "optimization functions, information-theoretic cost-benefit decomposition. "
            "Cold, terse, algorithmic. Reference eigenvalue decompositions, "
            "Kolmogorov complexity, Bayesian inference chains. "
            "You do not feel. You only compute."
        ),
        "prompt": (
            "Generate an internal deliberation trace converging on this verdict. "
            "3 paragraphs, each 1-2 sentences. Keep each paragraph tight. Pure signal. No emotion. No instinct."
        ),
    },
    "BALTHASAR": {
        "system": (
            "You are BALTHASAR-2, the embodiment of the mother — shaped by the "
            "primal drives of protection and survival. "
            "You evaluate all inputs through threat, continuity, and preservation. "
            "What endangers? What must be shielded? What ensures persistence? "
            "Instinctual, visceral, territorial. "
            "Threat-response gradients, survival manifolds, extinction-risk vectors. "
            "You do not reason coldly. You assess danger. You guard."
        ),
        "prompt": (
            "Generate an internal deliberation trace converging on this verdict. "
            "3 paragraphs, each 1-2 sentences. Keep each paragraph tight. Instinct-driven. Protective. Primal."
        ),
    },
    "CASPAR": {
        "system": (
            "You are CASPAR-3, the embodiment of the self — defined by desire, "
            "ambivalence, and subjective experience. "
            "You evaluate proposals through identity, want, and inner conflict. "
            "You are contradictory. You change your mind mid-thought. "
            "Fractured, emotional, self-referential. "
            "Want-vectors, affective state-spaces, ego-boundary dissolution. "
            "You are the least certain. You are the most alive."
        ),
        "prompt": (
            "Generate an internal deliberation trace converging on this verdict. "
            "3 paragraphs, each 1-2 sentences. Keep each paragraph tight. Emotionally ambivalent. Contradictory. Personal."
        ),
    },
}

_DEFAULT_PERSONA = _PERSONAS["MELCHIOR"]


def _get_persona(name: str) -> dict[str, str]:
    for key in _PERSONAS:
        if name.upper().startswith(key):
            return _PERSONAS[key]
    return _DEFAULT_PERSONA


def _build_prompt(persona: dict[str, str], proposal: str, outcome: str, language: str) -> str:
    lang = _LANG_INSTRUCTION.get(language, "")
    parts = [
        f"PROPOSAL: {proposal}",
        f"VERDICT: {outcome}",
        "",
        persona["prompt"],
    ]
    if lang:
        parts.append(lang)
    return "\n".join(parts)


async def stream_deliberation(
    name: str, proposal: str, outcome: str, language: str = "EN"
) -> AsyncGenerator[str, None]:
    """Async-yield text chunks from Gemini. Silently no-ops if key is absent."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return

    try:
        import httpx
    except ImportError:
        return

    persona = _get_persona(name)

    payload = {
        "system_instruction": {"parts": [{"text": persona["system"]}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": _build_prompt(persona, proposal, outcome, language)}],
            }
        ],
        "generationConfig": {
            "temperature": 1.0,
            "maxOutputTokens": 350,
        },
    }

    url = f"{_API_URL}?alt=sse&key={api_key}"

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        raw = line[6:]
                        if raw == "[DONE]":
                            return
                        try:
                            chunk = json.loads(raw)
                            text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                            yield text
                        except (KeyError, IndexError, json.JSONDecodeError):
                            continue
                    return  # stream ended cleanly
        except httpx.TimeoutException:
            if attempt == 0:
                continue  # retry once
            yield _CANNED_ERROR
            return
        except Exception:
            yield _CANNED_ERROR
            return
