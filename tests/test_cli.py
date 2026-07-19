"""Tests for the Typer CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from rvrb_transform.cli import app

runner = CliRunner()


class TestCLIHelp:
    def test_help_succeeds(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Transform" in result.output or "transform" in result.output.lower()


class TestCLIArgs:
    def test_no_instruction_fails(self) -> None:
        result = runner.invoke(app, ["hello"])
        assert result.exit_code == 1
        assert "instruction" in result.output.lower() or "Error" in result.output

    def test_stdin_input_no_args_fails(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code != 0


class TestCLIJson:
    def test_json_flag_accepted(self) -> None:
        result = runner.invoke(
            app,
            ["hello", "uppercase", "--json"],
        )
        assert result.exit_code == 1  # fails because no real provider


class TestCLIModel:
    def test_model_flag_accepted(self) -> None:
        result = runner.invoke(
            app,
            ["hello", "uppercase", "--model", "gpt-4"],
        )
        assert result.exit_code == 1  # fails because no real provider


class TestCLIProvider:
    def test_provider_flag_accepted(self) -> None:
        result = runner.invoke(
            app,
            ["hello", "uppercase", "--provider", "openai"],
        )
        assert result.exit_code == 1  # fails because no real provider
