import importlib
import sys
from types import SimpleNamespace

import pytest

from geo_audit.api_usage import (
    UsageTracker,
    extract_openai_usage,
    get_current_usage_tracker,
    record_openai_usage,
    track_api_usage,
)


def fake_response(
    content="Test answer",
    model="gpt-4o-mini",
    prompt_tokens=100,
    completion_tokens=25,
    total_tokens=125,
    include_usage=True,
):
    response = SimpleNamespace(
        model=model,
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ],
    )

    if include_usage:
        response.usage = SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    return response


def test_extract_openai_usage_from_full_response():
    usage = extract_openai_usage(fake_response())

    assert usage == {
        "model_name": "gpt-4o-mini",
        "usage_available": True,
        "input_tokens": 100,
        "output_tokens": 25,
        "total_tokens": 125,
    }


def test_extract_openai_usage_handles_missing_usage():
    usage = extract_openai_usage(
        fake_response(include_usage=False),
        fallback_model_name="fallback-model",
    )

    assert usage["model_name"] == "gpt-4o-mini"
    assert usage["usage_available"] is False
    assert usage["input_tokens"] == 0
    assert usage["output_tokens"] == 0
    assert usage["total_tokens"] == 0


def test_extract_openai_usage_derives_total_tokens_when_missing():
    response = fake_response(total_tokens=None)

    usage = extract_openai_usage(response)

    assert usage["input_tokens"] == 100
    assert usage["output_tokens"] == 25
    assert usage["total_tokens"] == 125


def test_usage_tracker_aggregates_multiple_calls():
    tracker = UsageTracker()

    tracker.record_response(fake_response(prompt_tokens=100, completion_tokens=25, total_tokens=125))
    tracker.record_response(fake_response(prompt_tokens=200, completion_tokens=50, total_tokens=250))
    tracker.record_response(fake_response(include_usage=False))

    summary = tracker.to_summary()

    assert summary["model_name"] == "gpt-4o-mini"
    assert summary["input_tokens"] == 300
    assert summary["output_tokens"] == 75
    assert summary["total_tokens"] == 375
    assert summary["call_count"] == 3
    assert summary["calls_with_usage"] == 2
    assert summary["calls_without_usage"] == 1
    assert summary["usage_available"] is True
    assert summary["pricing_available"] is True
    assert summary["estimated_actual_cost_usd"] == pytest.approx(0.00009)
    assert summary["pricing_label"] == "gpt-4o-mini text token pricing"


def test_usage_tracker_unknown_model_pricing_fallback():
    tracker = UsageTracker()

    tracker.record_response(fake_response(model="custom-model"))
    summary = tracker.to_summary()

    assert summary["model_name"] == "custom-model"
    assert summary["usage_available"] is True
    assert summary["pricing_available"] is False
    assert summary["estimated_actual_cost_usd"] is None
    assert summary["pricing_label"] is None


def test_record_openai_usage_uses_active_context_tracker():
    assert get_current_usage_tracker() is None

    with track_api_usage() as tracker:
        record_openai_usage(fake_response())
        assert get_current_usage_tracker() is tracker

    assert get_current_usage_tracker() is None
    assert tracker.to_summary()["call_count"] == 1


def test_ask_ai_returns_text_while_recording_usage(monkeypatch):
    sys.modules.pop("geo_audit.analyzer", None)
    analyzer = importlib.import_module("geo_audit.analyzer")

    class FakeCompletions:
        def create(self, **kwargs):
            return fake_response(content="Recorded answer")

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=FakeCompletions(),
        ),
    )
    monkeypatch.setattr(analyzer, "get_openai_client", lambda: fake_client)

    with track_api_usage() as tracker:
        answer = analyzer.ask_ai("Sensitive prompt text", "English")

    summary = tracker.to_summary()

    assert answer == "Recorded answer"
    assert summary["call_count"] == 1
    assert summary["input_tokens"] == 100
    assert "Sensitive prompt text" not in str(summary)
    assert "Recorded answer" not in str(summary)
