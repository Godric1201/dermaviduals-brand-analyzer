import json

import pandas as pd

from benchmark_snapshot import (
    build_benchmark_snapshot,
    dataframe_to_records,
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

    assert snapshot["metadata"] == {
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
