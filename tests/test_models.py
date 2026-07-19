"""Tests for rvrb_transform models."""

from __future__ import annotations

import pickle
from pathlib import Path

from rvrb_transform.models import (
    MediaInput,
    MediaModality,
    MediaOutput,
    ProviderError,
    QuotaExhaustedError,
    TransformResult,
)


class TestMediaModality:
    def test_values(self) -> None:
        assert MediaModality.TEXT == "text"
        assert MediaModality.AUDIO == "audio"
        assert MediaModality.IMAGE == "image"
        assert MediaModality.VIDEO == "video"

    def test_member_count(self) -> None:
        assert len(MediaModality) == 4


class TestMediaInput:
    def test_basic(self) -> None:
        mi = MediaInput(path=Path("/tmp/test.txt"), modality=MediaModality.TEXT)
        assert mi.path == Path("/tmp/test.txt")
        assert mi.modality == MediaModality.TEXT
        assert mi.metadata == {}

    def test_with_metadata(self) -> None:
        mi = MediaInput(
            path=Path("/tmp/test.mp3"),
            modality=MediaModality.AUDIO,
            metadata={"duration_seconds": 120},
        )
        assert mi.metadata["duration_seconds"] == 120


class TestMediaOutput:
    def test_basic(self) -> None:
        mo = MediaOutput(data="transformed text")
        assert mo.data == "transformed text"
        assert mo.modality == MediaModality.TEXT
        assert mo.format == "text"

    def test_custom_format(self) -> None:
        mo = MediaOutput(data=b"bytes", modality=MediaModality.IMAGE, format="png")
        assert mo.format == "png"
        assert mo.data == b"bytes"


class TestTransformResult:
    def test_basic(self) -> None:
        result = TransformResult(
            input_text="hello",
            instruction="uppercase",
            output_text="HELLO",
            model="qwen3-coder-plus",
            provider="qwen",
        )
        assert result.output_text == "HELLO"
        assert result.tokens_used is None

    def test_with_tokens(self) -> None:
        result = TransformResult(
            input_text="hello",
            instruction="uppercase",
            output_text="HELLO",
            model="qwen3-coder-plus",
            provider="qwen",
            tokens_used=150,
        )
        assert result.tokens_used == 150

    def test_json_roundtrip(self) -> None:
        result = TransformResult(
            input_text="hello",
            instruction="uppercase",
            output_text="HELLO",
            model="gpt-4",
            provider="openai",
        )
        data = result.model_dump(mode="json")
        restored = TransformResult.model_validate(data)
        assert restored.input_text == "hello"
        assert restored.output_text == "HELLO"


class TestProviderError:
    def test_basic(self) -> None:
        err = ProviderError("model-1", 429, "rate limited")
        assert err.model_id == "model-1"
        assert err.status_code == 429
        assert err.body == "rate limited"
        assert "model-1" in str(err)

    def test_default_body(self) -> None:
        err = ProviderError("m", 500)
        assert err.body is None

    def test_pickling(self) -> None:
        err = pickle.loads(pickle.dumps(ProviderError("m", 401, "bad auth")))
        assert err.model_id == "m"
        assert err.status_code == 401


class TestQuotaExhaustedError:
    def test_is_provider_error(self) -> None:
        err = QuotaExhaustedError("m", 429, "quota")
        assert isinstance(err, ProviderError)

    def test_pickling(self) -> None:
        err = pickle.loads(pickle.dumps(QuotaExhaustedError("m", 429, "quota")))
        assert isinstance(err, QuotaExhaustedError)
