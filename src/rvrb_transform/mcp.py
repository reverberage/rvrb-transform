"""MCP server for text transformation."""

from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP

    HAS_MCP = True
except ImportError:  # pragma: no cover
    HAS_MCP = False


def transform_text(
    input_text: str,
    instruction: str,
) -> dict[str, Any]:
    """Transform text using an LLM.

    Args:
        input_text: The text to transform.
        instruction: Natural-language transformation instruction.
    """
    from rvrb_transform.engine import TransformEngine
    from rvrb_transform.provider import get_provider

    try:
        provider = get_provider()
        engine = TransformEngine(provider=provider)
        result = engine.transform(input_text, instruction)
        return {
            "input_text": input_text,
            "instruction": instruction,
            "output_text": result,
            "model": getattr(provider, "model", ""),
        }
    except Exception as exc:
        return {"error": str(exc)}


def _build_server() -> Any:
    """Create and return a configured MCP server instance.

    Returns None if the ``mcp`` package is not installed.
    """
    if not HAS_MCP:
        return None

    mcp_server = FastMCP("rvrb-transform")

    @mcp_server.tool()
    def transform(
        input_text: str,
        instruction: str,
    ) -> dict[str, Any]:
        """Transform text based on a natural language instruction."""
        return transform_text(input_text, instruction)

    return mcp_server


mcp: Any = _build_server()


def main() -> None:
    """Entry point for ``rvrb-transform-mcp``."""
    if mcp is None:
        msg = "MCP support requires the 'mcp' extra. Install with: pip install rvrb-transform[mcp]"
        raise ImportError(msg)

    mcp.run(transport="stdio")
