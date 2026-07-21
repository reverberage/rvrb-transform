"""Typer CLI for text transformation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

app = typer.Typer(
    name="rvrb-transform",
    help="Transform text based on natural language instructions.",
)


@app.command()
def transform_command(
    instruction: str = typer.Argument(
        help="Transformation instruction (e.g., 'uppercase', 'summarize').",
    ),
    text: str = typer.Argument(
        "",
        help="Input text to transform. Reads from stdin if empty.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Override model ID (e.g., qwen3-coder-plus, gpt-4).",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="Provider name: qwen, openai, local.  Overrides N3RVERBERAGE_PROVIDER.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write output to file (default: stdout).",
    ),
) -> None:
    """Transform text based on natural language instructions.

    Usage:
        rvrb-transform "make it uppercase" "Hello World"
        echo "Hello World" | rvrb-transform "make it uppercase"
    """
    if not text:
        if sys.stdin.isatty():
            _print_error("No text provided. Either pass text as an argument or pipe text to stdin.")
            raise typer.Exit(code=1)
        text = sys.stdin.read().strip()

    if not text:
        _print_error("Input text is empty.")
        raise typer.Exit(code=1)

    if not instruction:
        _print_error("No instruction provided.")
        raise typer.Exit(code=1)

    try:
        from rvrb_transform.engine import TransformEngine
        from rvrb_transform.provider import get_provider

        resolved_provider = get_provider(model=model, provider=provider)
        engine = TransformEngine(provider=resolved_provider)
        result_text = engine.transform(text, instruction)
    except ValueError as exc:
        _print_error(str(exc))
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        _print_error(str(exc))
        raise typer.Exit(code=1) from exc

    if json_output:
        result = {
            "input_text": text,
            "instruction": instruction,
            "output_text": result_text,
            "model": getattr(resolved_provider, "model", ""),
            "provider": provider or "",
        }
        output_str = json.dumps(result, indent=2, default=str) + "\n"
    else:
        output_str = result_text + "\n"

    if output:
        output.write_text(output_str)
    else:
        typer.echo(output_str.rstrip("\n"))


def _print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def main() -> None:
    """Entry point for the CLI."""
    app()
