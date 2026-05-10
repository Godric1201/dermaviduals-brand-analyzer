from geo_audit.analyzer import DEFAULT_MODEL
from geo_audit.ui.api_usage_panel import (
    build_api_usage_display_rows,
    build_empty_api_usage_summary,
    coerce_api_usage_summary,
    format_api_usage_cost,
)


def test_empty_usage_summary_defaults():
    summary = build_empty_api_usage_summary()

    assert summary == {
        "model_name": DEFAULT_MODEL,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "call_count": 0,
        "calls_with_usage": 0,
        "calls_without_usage": 0,
        "usage_available": False,
        "pricing_available": False,
        "estimated_actual_cost_usd": None,
        "pricing_label": None,
    }


def test_coerce_api_usage_summary_handles_none():
    summary = coerce_api_usage_summary(None)

    assert summary["model_name"] == DEFAULT_MODEL
    assert summary["call_count"] == 0
    assert summary["usage_available"] is False
    assert summary["pricing_available"] is False


def test_format_api_usage_cost_for_unavailable_cost():
    assert format_api_usage_cost(build_empty_api_usage_summary()) == "Unavailable"


def test_format_api_usage_cost_for_small_known_cost():
    summary = coerce_api_usage_summary({
        "model_name": "gpt-4o-mini",
        "input_tokens": 1200,
        "output_tokens": 450,
        "total_tokens": 1650,
        "call_count": 1,
        "calls_with_usage": 1,
        "calls_without_usage": 0,
        "usage_available": True,
        "pricing_available": True,
        "estimated_actual_cost_usd": 0.00045,
        "pricing_label": "gpt-4o-mini text token pricing",
    })

    assert format_api_usage_cost(summary) == "< USD 0.01"


def test_display_rows_include_expected_metric_labels():
    rows = build_api_usage_display_rows(build_empty_api_usage_summary())

    assert [row["Metric"] for row in rows] == [
        "Model",
        "AI calls",
        "Calls with usage",
        "Calls without usage",
        "Input tokens",
        "Output tokens",
        "Total tokens",
        "Estimated actual API cost",
        "Pricing assumption",
    ]


def test_unknown_pricing_produces_unavailable_cost_and_pricing_rows():
    rows = build_api_usage_display_rows({
        "model_name": "custom-model",
        "input_tokens": 1200,
        "output_tokens": 450,
        "total_tokens": 1650,
        "call_count": 1,
        "calls_with_usage": 1,
        "calls_without_usage": 0,
        "usage_available": True,
        "pricing_available": False,
        "estimated_actual_cost_usd": None,
        "pricing_label": None,
    })
    row_values = {row["Metric"]: row["Value"] for row in rows}

    assert row_values["Estimated actual API cost"] == "Unavailable"
    assert row_values["Pricing assumption"] == "Unavailable"


def test_display_rows_exclude_prompt_answer_and_raw_payload_fields():
    rows = build_api_usage_display_rows({
        "model_name": "gpt-4o-mini",
        "input_tokens": 1200,
        "output_tokens": 450,
        "total_tokens": 1650,
        "call_count": 1,
        "calls_with_usage": 1,
        "calls_without_usage": 0,
        "usage_available": True,
        "pricing_available": True,
        "estimated_actual_cost_usd": 0.00045,
        "pricing_label": "gpt-4o-mini text token pricing",
        "prompt": "SECRET PROMPT",
        "answer": "SECRET ANSWER",
        "raw_response": {"id": "raw-response-id"},
    })
    rendered = str(rows)

    assert "SECRET PROMPT" not in rendered
    assert "SECRET ANSWER" not in rendered
    assert "raw-response-id" not in rendered
