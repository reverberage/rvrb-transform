"""Tests for TransformEngine."""

from __future__ import annotations

import pytest

from rvrb_transform.engine import TransformEngine
from rvrb_transform.models import ProviderError
from tests.conftest import MockProvider


class TestConstruction:
    def test_creates_with_mock_provider(self) -> None:
        engine = TransformEngine(provider=MockProvider())
        assert engine.provider is not None

    def test_provider_attribute(self) -> None:
        provider = MockProvider(model="test-model", base_url="test://")
        engine = TransformEngine(provider=provider)
        assert engine.provider.model == "test-model"
        assert engine.provider.base_url == "test://"


class TestTransform:
    def test_returns_string(self) -> None:
        engine = TransformEngine(provider=MockProvider())
        result = engine.transform("Hello world", "uppercase")
        assert isinstance(result, str)
        assert result == "mock response"

    def test_single_public_method(self) -> None:
        engine = TransformEngine(provider=MockProvider())
        public_methods = [
            m for m in dir(engine) if not m.startswith("_") and callable(getattr(engine, m))
        ]
        assert "transform" in public_methods
        assert "provider" not in public_methods


class TestSystemPrompt:
    def test_system_prompt_describes_transformation(self) -> None:
        class SpyProvider:
            model = "spy"
            base_url = "spy://"

            def __init__(self) -> None:
                self.captured_messages: list[dict[str, str]] = []

            def complete(self, messages: list[dict[str, str]], **kwargs: object) -> str:
                self.captured_messages = messages
                return "result"

            def complete_structured(
                self, messages: list[dict[str, str]], output_type: object, **kwargs: object
            ) -> object:
                return output_type()  # type: ignore[call-arg]

            def complete_with_tools(
                self, messages: list[dict[str, str]], tools: list[dict[str, str]], **kwargs: object
            ) -> object:
                return None  # type: ignore[return-value]

        spy = SpyProvider()
        TransformEngine(provider=spy).transform("Text to process", "make it uppercase")

        assert len(spy.captured_messages) == 2
        assert spy.captured_messages[0]["role"] == "system"
        assert "transform" in spy.captured_messages[0]["content"].lower()
        assert spy.captured_messages[1]["role"] == "user"
        assert "Text to process" in spy.captured_messages[1]["content"]
        assert "make it uppercase" in spy.captured_messages[1]["content"]


class TestTemperature:
    def test_temperature_zero(self) -> None:
        class KwargSpy:
            model = "spy"
            base_url = "spy://"
            captured_kwargs: dict[str, object] = {}

            def complete(self, messages: list[dict[str, str]], **kwargs: object) -> str:
                KwargSpy.captured_kwargs = dict(kwargs)  # type: ignore[arg-type]
                return "ok"

            def complete_structured(
                self, messages: list[dict[str, str]], output_type: object, **kwargs: object
            ) -> object:
                return output_type()  # type: ignore[call-arg]

            def complete_with_tools(
                self, messages: list[dict[str, str]], tools: list[dict[str, str]], **kwargs: object
            ) -> object:
                return None  # type: ignore[return-value]

        TransformEngine(provider=KwargSpy()).transform("hello", "uppercase")
        assert KwargSpy.captured_kwargs.get("temperature") in (0, 0.0)


class TestErrorPropagation:
    def test_provider_error_wrapped(self) -> None:
        class FailingProvider:
            model = "fail"
            base_url = "fail://"

            def complete(self, messages: list[dict[str, str]], **kwargs: object) -> str:
                raise ProviderError("fail", 500, "provider exploded")

            def complete_structured(
                self, messages: list[dict[str, str]], output_type: object, **kwargs: object
            ) -> object:
                return output_type()  # type: ignore[call-arg]

            def complete_with_tools(
                self, messages: list[dict[str, str]], tools: list[dict[str, str]], **kwargs: object
            ) -> object:
                return None  # type: ignore[return-value]

        engine = TransformEngine(provider=FailingProvider())
        with pytest.raises(RuntimeError, match="Transform failed"):
            engine.transform("hello", "uppercase")
