import io

import pytest

from benchmark_comparison import (
    compare_target_brand_metrics,
    find_brand_summary_record,
    load_snapshot_json,
    normalize_brand_name,
)


def make_snapshot(brand="Espresso House", summary_records=None):
    return {
        "metadata": {
            "brand": brand,
            "report_date": "2026-05-02",
            "run_mode": "Full Report Mode",
            "prompt_count": 20,
        },
        "summary_records": summary_records if summary_records is not None else [
            {
                "brand": brand,
                "total_mentions": 2,
                "average_visibility_score": 1.5,
                "prompts_visible": 2,
                "share_of_voice_percent": 20,
            }
        ],
    }


def metrics_by_name(comparison):
    return {
        row["Metric"]: row
        for row in comparison["metrics"]
    }


def test_normalize_brand_name_trims_collapses_and_lowercases():
    assert normalize_brand_name("  Espresso   House  ") == "espresso house"
    assert normalize_brand_name(None) == ""


def test_load_snapshot_json_reads_valid_json():
    uploaded_file = io.BytesIO(b'{"metadata": {"brand": "Espresso House"}}')

    snapshot = load_snapshot_json(uploaded_file)

    assert snapshot["metadata"]["brand"] == "Espresso House"


def test_load_snapshot_json_raises_value_error_for_invalid_json():
    uploaded_file = io.BytesIO(b"{not json")

    with pytest.raises(ValueError, match="Invalid benchmark snapshot JSON"):
        load_snapshot_json(uploaded_file)


def test_find_brand_summary_record_matches_case_insensitively():
    snapshot = make_snapshot(summary_records=[
        {"brand": "coffee fellows", "total_mentions": 1},
        {"brand": "ESPRESSO HOUSE", "total_mentions": 3},
    ])

    record = find_brand_summary_record(snapshot, "espresso house")

    assert record["brand"] == "ESPRESSO HOUSE"
    assert record["total_mentions"] == 3


def test_compare_target_brand_metrics_computes_deltas():
    previous_snapshot = make_snapshot(summary_records=[
        {
            "brand": "Espresso House",
            "total_mentions": 1,
            "average_visibility_score": 2.5,
            "prompts_visible": 1,
            "share_of_voice_percent": 10,
        }
    ])
    current_snapshot = make_snapshot(summary_records=[
        {
            "brand": "espresso house",
            "total_mentions": 3,
            "average_visibility_score": 4.0,
            "prompts_visible": 2,
            "share_of_voice_percent": 25,
        }
    ])

    comparison = compare_target_brand_metrics(previous_snapshot, current_snapshot)
    metrics = metrics_by_name(comparison)

    assert metrics["Total Mentions"] == {
        "Metric": "Total Mentions",
        "Previous": 1,
        "Current": 3,
        "Change": 2,
    }
    assert metrics["Average Visibility Score"]["Change"] == 1.5
    assert metrics["Prompts Visible"]["Change"] == 1
    assert metrics["Share of Voice %"]["Change"] == 15
    assert comparison["warnings"] == []


def test_compare_target_brand_metrics_handles_missing_previous_target_row():
    previous_snapshot = make_snapshot(summary_records=[
        {"brand": "Coffee Fellows", "total_mentions": 3},
    ])
    current_snapshot = make_snapshot()

    comparison = compare_target_brand_metrics(previous_snapshot, current_snapshot)
    metrics = metrics_by_name(comparison)

    assert metrics["Total Mentions"]["Previous"] == 0
    assert metrics["Total Mentions"]["Current"] == 2
    assert (
        "Previous snapshot does not contain a matching target brand row; previous values are treated as 0."
        in comparison["warnings"]
    )


def test_compare_target_brand_metrics_warns_on_brand_mismatch():
    previous_snapshot = make_snapshot(brand="Different Brand")
    current_snapshot = make_snapshot(brand="Espresso House")

    comparison = compare_target_brand_metrics(previous_snapshot, current_snapshot)

    assert (
        "Previous snapshot target brand does not match the current analysis context."
        in comparison["warnings"]
    )
