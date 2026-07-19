"""Shared fixtures for rvrb_transform tests."""

from __future__ import annotations

from rvrb_transform.models import ToolResult


class MockProvider:
    """Standalone mock provider implementing ModelProvider by structure.

    No ABC/Protocol inheritance. No MagicMock. Just a plain class that
    satisfies the ModelProvider structural contract.
    """

    def __init__(self, model: str = "mock-model", base_url: str = "mock://") -> None:
        self.model = model
        self.base_url = base_url

    def complete(self, messages: list[dict], **kwargs: object) -> str:
        return "mock response"

    def complete_structured(
        self,
        messages: list[dict],
        output_type: object,
        **kwargs: object,
    ) -> object:
        return output_type()  # type: ignore[call-arg]

    def complete_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        **kwargs: object,
    ) -> ToolResult:
        return ToolResult(content="mock tool result", tool_calls=[])
