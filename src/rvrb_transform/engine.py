"""Text transformation engine."""

from __future__ import annotations

from typing import Any, Protocol

from rvrb_transform.models import ProviderError


class ModelProvider(Protocol):
    """Protocol for a model provider used by the transform engine."""

    model: str

    def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str: ...


class TransformEngine:
    """Single-method text transformation engine.

    Constructs a system prompt + user message, calls ``provider.complete()``,
    and returns the raw response.
    """

    def __init__(self, provider: ModelProvider) -> None:
        self.provider = provider

    def transform(self, text: str, instruction: str) -> str:
        """Apply the instruction to the text and return the result.

        Parameters
        ----------
        text : str
            The input text to transform.
        instruction : str
            Natural-language instruction describing the desired transformation.

        Returns
        -------
        str
            The transformed text.
        """
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a text transformation engine. "
                    "Apply the user's instruction to the provided text. "
                    "Return only the transformed text, no explanation or commentary."
                ),
            },
            {
                "role": "user",
                "content": f"Text:\n{text}\n\nInstruction: {instruction}",
            },
        ]

        try:
            return self.provider.complete(messages, temperature=0)
        except ProviderError as exc:
            raise RuntimeError(f"Transform failed: {exc}") from exc
