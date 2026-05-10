import json

import pandas as pd

from geo_audit.benchmark_snapshot import (
    build_benchmark_snapshot,
    dataframe_to_records,
    normalize_api_usage_summary,
    serialize_benchmark_snapshot,
)


def build_sample_snapshot(**kwargs):
    summary_df = pd.DataFrame([
        {
            "brand": "espresso house",
            "total_mentions": 2,
            "average_visibility_score": 1.5,
        }
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "espresso house",
            "visibility_score": 1,
        }
    ])

    defaults = {
        "brand": "Espresso House",
        "market": "Berlin",
        "category": "cafes",
        "audience": "remote workers",
        "report_date": "2026-05-02",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "prompt_count": 20,
        "competitors": ["Coffee Fellows", "Einstein Kaffee"],
        "query_intent_categories": ["Best Options", "Local Recommendations"],
        "summary_df": summary_df,
        "detailed_df": detailed_df,
        "brand_intelligence": {
            "recommendation_drivers": "Trust and convenience",
            "target_brand_understanding": "AI-inferred brand understanding",
            "positioning_gap_analysis": "Build more comparison content",
        },
    }
    defaults.update(kwargs)

    return build_benchmark_snapshot(**defaults)


def test_benchmark_snapshot_has_expected_top_level_keys():
    snapshot = build_sample_snapshot()

    assert set(snapshot) == {
        "schema_version",
        "generated_at",
        "metadata",
        "summary_records",
        "detailed_records",
        "brand_intelligence",
        "notes",
    }
    assert snapshot["schema_version"] == "1.0"
    assert snapshot["generated_at"] == "2026-05-02"


def test_benchmark_snapshot_metadata_includes_run_context():
    snapshot = build_sample_snapshot()

    metadata = snapshot["metadata"]

    assert metadata["brand"] == "Espresso House"
    assert metadata["market"] == "Berlin"
    assert metadata["category"] == "cafes"
    assert metadata["audience"] == "remote workers"
    assert metadata["report_date"] == "2026-05-02"
    assert metadata["run_mode"] == "Full Report Mode"
    assert metadata["prompt_limit"] is None
    assert metadata["prompt_count"] == 20
    assert metadata["competitors"] == ["Coffee Fellows", "Einstein Kaffee"]
    assert metadata["query_intent_categories"] == [
        "Best Options",
        "Local Recommendations",
    ]

    assert metadata["run_metadata"] == {
        "model_name": "gpt-4o-mini",
        "prompt_set_version": "v1",
        "repeat_count": 1,
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "prompt_count": 20,
        "raw_answers_included": False,
        "api_usage": None,
        "generated_at": "2026-05-02",
    }


def test_dataframe_to_records_converts_dataframe_rows():
    df = pd.DataFrame([
        {"brand": "Espresso House", "score": 2},
        {"brand": "Coffee Fellows", "score": 1},
    ])

    assert dataframe_to_records(df) == [
        {"brand": "Espresso House", "score": 2},
        {"brand": "Coffee Fellows", "score": 1},
    ]


def test_dataframe_to_records_handles_none_and_missing_values():
    df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "score": float("nan"),
            "timestamp": pd.NaT,
        }
    ])

    records = dataframe_to_records(df)

    assert dataframe_to_records(None) == []
    assert records == [
        {
            "brand": "Espresso House",
            "score": None,
            "timestamp": None,
        }
    ]
    json.dumps(records, default=str)


def test_serialize_benchmark_snapshot_returns_valid_json_string():
    snapshot = build_sample_snapshot()

    serialized = serialize_benchmark_snapshot(snapshot)
    parsed = json.loads(serialized)

    assert isinstance(serialized, str)
    assert parsed["metadata"]["brand"] == "Espresso House"
    assert parsed["brand_intelligence"]["recommendation_drivers"] == "Trust and convenience"


def test_raw_answer_records_are_excluded_by_default():
    raw_answer_df = pd.DataFrame([
        {"prompt": "test prompt", "answer": "test answer"},
    ])

    snapshot = build_sample_snapshot(raw_answer_df=raw_answer_df)

    assert "raw_answer_records" not in snapshot
    assert snapshot["metadata"]["run_metadata"]["raw_answers_included"] is False


def test_raw_answer_records_are_included_only_when_requested():
    raw_answer_df = pd.DataFrame([
        {"prompt": "test prompt", "answer": "test answer"},
    ])

    snapshot = build_sample_snapshot(
        include_raw_answers=True,
        raw_answer_df=raw_answer_df,
    )

    assert snapshot["raw_answer_records"] == [
        {"prompt": "test prompt", "answer": "test answer"},
    ]
    assert snapshot["metadata"]["run_metadata"]["raw_answers_included"] is True


def test_raw_answer_records_serialize_cleanly_to_json():
    raw_answer_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        },
    ])

    snapshot = build_sample_snapshot(
        include_raw_answers=True,
        raw_answer_df=raw_answer_df,
    )

    serialized = serialize_benchmark_snapshot(snapshot)
    parsed = json.loads(serialized)

    assert parsed["metadata"]["run_metadata"]["raw_answers_included"] is True
    assert parsed["raw_answer_records"] == [
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        },
    ]


def test_benchmark_snapshot_includes_api_usage_metadata():
    api_usage_summary = {
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

    snapshot = build_sample_snapshot(api_usage_summary=api_usage_summary)

    assert snapshot["metadata"]["run_metadata"]["api_usage"] == api_usage_summary


def test_benchmark_snapshot_handles_missing_api_usage_metadata():
    snapshot = build_sample_snapshot(api_usage_summary=None)

    assert snapshot["metadata"]["run_metadata"]["api_usage"] is None


def test_benchmark_snapshot_api_usage_serializes_cleanly():
    snapshot = build_sample_snapshot(
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

    serialized = serialize_benchmark_snapshot(snapshot)
    parsed = json.loads(serialized)

    assert parsed["metadata"]["run_metadata"]["api_usage"]["total_tokens"] == 1650
    assert (
        parsed["metadata"]["run_metadata"]["api_usage"]["pricing_label"]
        == "gpt-4o-mini text token pricing"
    )


def test_benchmark_snapshot_api_usage_excludes_prompt_answer_and_raw_payloads():
    snapshot = build_sample_snapshot(
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
            "prompt": "SECRET PROMPT TEXT",
            "answer": "SECRET ANSWER TEXT",
            "raw_response": {"id": "raw-response-id"},
        }
    )

    serialized = serialize_benchmark_snapshot(snapshot)
    api_usage = snapshot["metadata"]["run_metadata"]["api_usage"]

    assert set(api_usage) == {
        "model_name",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "call_count",
        "calls_with_usage",
        "calls_without_usage",
        "usage_available",
        "pricing_available",
        "estimated_actual_cost_usd",
        "pricing_label",
    }
    assert "SECRET PROMPT TEXT" not in serialized
    assert "SECRET ANSWER TEXT" not in serialized
    assert "raw-response-id" not in serialized


def test_normalize_api_usage_summary_allowlists_aggregate_fields_only():
    normalized = normalize_api_usage_summary({
        "model_name": "gpt-4o-mini",
        "input_tokens": 1,
        "output_tokens": 2,
        "total_tokens": 3,
        "call_count": 1,
        "calls_with_usage": 1,
        "calls_without_usage": 0,
        "usage_available": True,
        "pricing_available": True,
        "estimated_actual_cost_usd": 0.01,
        "pricing_label": "gpt-4o-mini text token pricing",
        "prompt": "do not export",
        "answer": "do not export",
    })

    assert normalized == {
        "model_name": "gpt-4o-mini",
        "input_tokens": 1,
        "output_tokens": 2,
        "total_tokens": 3,
        "call_count": 1,
        "calls_with_usage": 1,
        "calls_without_usage": 0,
        "usage_available": True,
        "pricing_available": True,
        "estimated_actual_cost_usd": 0.01,
        "pricing_label": "gpt-4o-mini text token pricing",
    }


def test_quick_test_note_is_included_only_for_quick_test_mode():
    quick_snapshot = build_sample_snapshot(
        run_mode="Quick Test Mode",
        prompt_limit=1,
    )
    full_snapshot = build_sample_snapshot()

    assert quick_snapshot["notes"]["quick_test_mode"] == (
        "Quick Test Mode output is not client-deliverable."
    )
    assert full_snapshot["notes"]["quick_test_mode"] is None
    assert (
        full_snapshot["notes"]["brand_intelligence"]
        == "Brand Intelligence diagnostic output is not part of visibility scoring or share of voice."
    )


def test_benchmark_snapshot_sanitizes_brand_intelligence_without_changing_records():
    summary_df = pd.DataFrame([
        {"brand": "Dermaviduals", "total_mentions": 0},
    ])
    detailed_df = pd.DataFrame([
        {"brand": "Dermaviduals", "visibility_score": 0},
    ])

    snapshot = build_benchmark_snapshot(
        brand="Dermaviduals",
        market="Hong Kong",
        category="skincare products",
        audience="skincare-conscious consumers",
        report_date="2026-05-02",
        run_mode="Quick Test Mode",
        prompt_limit=1,
        prompt_count=1,
        competitors=["Environ"],
        query_intent_categories=["Best Options"],
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence={
            "recommendation_drivers": "clinical backing",
            "target_brand_understanding": "product effectiveness",
            "positioning_gap_analysis": (
                "AI-Discovered Brands Not Included in Scoring\n"
                "- Market Research"
            ),
        },
    )

    assert snapshot["summary_records"] == [{"brand": "Dermaviduals", "total_mentions": 0}]
    assert snapshot["detailed_records"] == [{"brand": "Dermaviduals", "visibility_score": 0}]
    assert "clinical backing" not in snapshot["brand_intelligence"]["recommendation_drivers"].lower()
    assert "product effectiveness" not in snapshot["brand_intelligence"]["target_brand_understanding"].lower()
    assert "Market Research" not in snapshot["brand_intelligence"]["positioning_gap_analysis"]
    assert "No additional non-tracked brands were identified." in snapshot["brand_intelligence"]["positioning_gap_analysis"]
