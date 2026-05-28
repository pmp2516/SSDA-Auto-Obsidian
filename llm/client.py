from __future__ import annotations

from openai import OpenAI

from .config import LLMConfig
from .prompts import EXTRACT_OCR_SYSTEM, FILL_TEMPLATE_SYSTEM, FILL_TEMPLATE_USER


class LLMClient:
    """For OpenAI compatible endpoints .

    Works with OpenRouter, Ollama and more.

    Usage::

        client = LLMClient()                          # reads from .env
        client = LLMClient(LLMConfig(model="..."))    # explicit override

        note = client.fill_template(extracted_text, template_markdown)
        data = client.extract_ocr(raw_ocr_text)       # returns parsed dict
    """

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._openai = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
        )

    def fill_template(self, extracted_text: str, template: str) -> str:
        """Ask the LLM to fill *template* with *extracted_text*.

        Returns the filled-in markdown string.
        """
        user_msg = FILL_TEMPLATE_USER.format(
            extracted_text=extracted_text,
            template=template,
        )
        return self._chat(FILL_TEMPLATE_SYSTEM, user_msg)

    def extract_ocr(self, raw_text: str) -> dict:
        """Post-process raw OCR output into structured data.

        Returns a dict with keys: text, todos, tags.
        The LLM is instructed to return JSON; this method parses it.
        """
        import json

        response_text = self._chat(EXTRACT_OCR_SYSTEM, raw_text)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM did not return valid JSON for OCR extraction.\n"
                f"Raw response:\n{response_text}"
            ) from exc

    def _chat(self, system: str, user: str, model: str | None = None) -> str:
        """Single-turn chat completion. Returns the assistant message text."""
        response = self._openai.chat.completions.create(
            model=model or self.config.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned an empty response.")
        return content
