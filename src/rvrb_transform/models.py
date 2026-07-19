"""Pydantic models for text transformation."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class MediaModality(StrEnum):
    """Supported media modalities."""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


class MediaInput(BaseModel):
    """Input media reference."""

    path: Path
    modality: MediaModality = MediaModality.TEXT
    metadata: dict[str, object] = Field(default_factory=dict)


class MediaOutput(BaseModel):
    """Output media result."""

    data: str | bytes
    modality: MediaModality = MediaModality.TEXT
    format: str = "text"


class TransformResult(BaseModel):
    """Result of a text transformation."""

    input_text: str
    instruction: str
    output_text: str
    model: str = ""
    provider: str = ""
    tokens_used: int | None = None


# ---------------------------------------------------------------------------
# Provider interface types (no external dependency on n3rverberage)
# ---------------------------------------------------------------------------


class ToolCall(BaseModel):
    """A function call requested by the model."""

    id: str
    name: str
    arguments: dict[str, object] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Result of a completion with optional tool calls."""

    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ProviderError(RuntimeError):
    """Generic provider error during a completion call."""

    def __init__(
        self,
        model_id: str,
        status_code: int,
        body: str | None = None,
    ) -> None:
        self.model_id = model_id
        self.status_code = status_code
        self.body = body
        super().__init__(f"[{model_id}] HTTP {status_code}: {body or 'unknown error'}")

    def __reduce__(self) -> tuple[type, tuple[str, int, str | None]]:
        return (type(self), (self.model_id, self.status_code, self.body))


class QuotaExhaustedError(ProviderError):
    """Quota exhausted for a model."""
