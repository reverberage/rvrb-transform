# rvrb-transform

Text transformation engine — a composable satellite in the [reverberage](https://github.com/reverberage) ecosystem.

Transforms text based on natural language instructions using any OpenAI-compatible LLM provider.

## Install

```bash
pip install rvrb-transform
```

## Usage

```bash
# Direct text + instruction
rvrb-transform "Hello World" "make it lowercase"

# Pipe input
echo "Hello World" | rvrb-transform "make it lowercase"

# JSON output
rvrb-transform "Hello World" "make it lowercase" --json

# Override model
rvrb-transform "Hello World" "translate to Spanish" --model gpt-4

# Write to file
rvrb-transform "Hello World" "uppercase" --output result.txt
```

## MCP Server

```bash
pip install rvrb-transform[mcp]
rvrb-transform-mcp
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy .
```
