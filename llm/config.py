from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file) automatically.
load_dotenv(Path(__file__).parent.parent / ".env", override=False)


@dataclass
class LLMConfig:
    """Runtime configuration for the LLM client.

    Populated from environment variables by default; override any field
    programmatically when you need a non-default value.

    Priority: custom endpoint > OpenRouter.
    A custom endpoint is active when CUSTOM_BASE_URL is set.
    """

    base_url: str = field(default_factory=lambda: (
        os.environ.get("CUSTOM_BASE_URL")
        or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    ))
    api_key: str = field(default_factory=lambda: (
        os.environ.get("CUSTOM_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY", "")
    ).removeprefix("Bearer ").strip())
    model: str = field(default_factory=lambda: (
        os.environ.get("CUSTOM_DEFAULT_MODEL")
        or os.environ.get("OPENROUTER_DEFAULT_MODEL", "google/gemini-flash-1.5")
    ))
    temperature: float = field(default_factory=lambda: float(
        os.environ.get("LLM_TEMPERATURE", "0.2")
    ))
    max_tokens: int = field(default_factory=lambda: int(
        os.environ.get("LLM_MAX_TOKENS", "4096")
    ))

    def is_custom_endpoint(self) -> bool:
        return bool(os.environ.get("CUSTOM_BASE_URL"))
