import json

import pandas as pd

from geo_audit.ui.exports import build_benchmark_snapshot_export


def build_export_fixture(**kwargs):
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 2,
            "average_visibility_score": 1.5,
        }
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Espresso House",
            "visibility_score": 1,
        }
    ])
    raw_answer_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        }
    ])
    defaults = {
        "display_brand": "Espresso House",
        "display_market": "Berlin",
        "display_category": "cafes",
        "display_audience": "remote workers",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "prompt_count": 20,
        "competitors": ["Coffee Fellows", "Einstein Kaffee"],
        "prompt_categories": ["Best Options", "Local Recommendations"],
        "summary_df": summary_df,
        "detailed_df": detailed_df,
        "snapshot_brand_intelligence": None,
        "include_raw_answers": False,
        "raw_answer_df": raw_answer_df,
        "api_usage_summary": None,
        "report_date": "2026-05-02",
    }
    defaults.update(kwargs)

    return build_benchmark_snapshot_export(**defaults)


def test_benchmark_snapshot_export_excludes_raw_answers_by_default():
    export = build_export_fixture()

    assert "raw_answer_records" not in export.snapshot
    assert export.snapshot["metadata"]["run_metadata"]["raw_answers_included"] is False


def test_benchmark_snapshot_export_includes_raw_answers_when_requested():
    export = build_export_fixture(include_raw_answers=True)

    assert export.snapshot["raw_answer_records"] == [
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        }
    ]
    assert export.snapshot["metadata"]["run_metadata"]["raw_answers_included"] is True


def test_benchmark_snapshot_export_includes_api_usage_metadata():
    export = build_export_fixture(
        api_usage_summary={
            "model_name": "gpt-4o-mini",
            "input_tokens": 1200,
            "output_tokens": 450,
            "total_tokens": 1650,
            "call_count": 3,
            "calls_with_usage": 2,
            "calls_without_usage": 1,
            "usage_available": True,
            "pricing_available": True,
            "estimated_actual_cost_usd": 0.00045,
            "pricing_label": "gpt-4o-mini text token pricing",
        }
    )

    api_usage = export.snapshot["metadata"]["run_metadata"]["api_usage"]

    assert api_usage["model_name"] == "gpt-4o-mini"
    assert api_usage["total_tokens"] == 1650
    assert api_usage["estimated_actual_cost_usd"] == 0.00045


def test_benchmark_snapshot_export_json_bytes_decode_as_utf8_json():
    export = build_export_fixture()
    parsed = json.loads(export.json_bytes.decode("utf-8"))

    assert parsed["metadata"]["brand"] == "Espresso House"
    assert parsed["metadata"]["run_metadata"]["generated_at"] == "2026-05-02"


def test_benchmark_snapshot_export_filename_uses_snapshot_json_export_name():
    export = build_export_fixture()

    assert "benchmark_snapshot" in export.file_name
    assert export.file_name.endswith(".json")


def test_benchmark_snapshot_export_excludes_raw_api_payload_fields():
    export = build_export_fixture(
        api_usage_summary={
            "model_name": "gpt-4o-mini",
            "input_tokens": 1200,
            "output_tokens": 450,
            "total_tokens": 1650,
            "call_count": 3,
            "calls_with_usage": 2,
            "calls_without_usage": 1,
            "usage_available": True,
            "pricing_available": True,
            "estimated_actual_cost_usd": 0.00045,
            "pricing_label": "gpt-4o-mini text token pricing",
            "prompt": "SECRET PROMPT",
            "answer": "SECRET ANSWER",
            "raw_response": {"id": "raw-response-id"},
        }
    )
    serialized = export.json_bytes.decode("utf-8")

    assert "SECRET PROMPT" not in serialized
    assert "SECRET ANSWER" not in serialized
    assert "raw-response-id" not in serialized
