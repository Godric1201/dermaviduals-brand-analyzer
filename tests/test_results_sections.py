import pandas as pd

from geo_audit.ui.results_sections import build_executive_snapshot_metrics


def test_build_executive_snapshot_metrics_finds_target_brand():
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "average_visibility_score": 1.5,
            "total_mentions": 3,
            "share_of_voice_percent": 42.5,
            "prompts_visible": 2,
        }
    ])
    detailed_df = pd.DataFrame([
        {"brand": "Espresso House", "visibility_score": 1},
        {"brand": "Espresso House", "visibility_score": 2},
    ])

    metrics = build_executive_snapshot_metrics(
        summary_df,
        detailed_df,
        "Espresso House",
    )

    assert metrics == {
        "target_found": True,
        "organic_score": 1.5,
        "target_score": 1.5,
        "target_mentions": 3,
        "target_sov": 42.5,
        "target_visible_prompts": 2,
    }


def test_build_executive_snapshot_metrics_matches_brand_case_insensitively():
    summary_df = pd.DataFrame([
        {
            "brand": "espresso house",
            "average_visibility_score": 1.5,
            "total_mentions": 3,
            "share_of_voice_percent": 42.5,
            "prompts_visible": 2,
        }
    ])
    detailed_df = pd.DataFrame([
        {"brand": "ESPRESSO HOUSE", "visibility_score": 2},
    ])

    metrics = build_executive_snapshot_metrics(
        summary_df,
        detailed_df,
        "Espresso House",
    )

    assert metrics["target_found"] is True
    assert metrics["organic_score"] == 2


def test_build_executive_snapshot_metrics_handles_missing_target_brand():
    summary_df = pd.DataFrame([
        {
            "brand": "Coffee Fellows",
            "average_visibility_score": 1.5,
            "total_mentions": 3,
            "share_of_voice_percent": 42.5,
            "prompts_visible": 2,
        }
    ])
    detailed_df = pd.DataFrame([
        {"brand": "Coffee Fellows", "visibility_score": 2},
    ])

    metrics = build_executive_snapshot_metrics(
        summary_df,
        detailed_df,
        "Espresso House",
    )

    assert metrics == {
        "target_found": False,
        "organic_score": 0,
    }


def test_build_executive_snapshot_metrics_uses_zero_for_nan_organic_score():
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "average_visibility_score": 0,
            "total_mentions": 0,
            "share_of_voice_percent": 0,
            "prompts_visible": 0,
        }
    ])
    detailed_df = pd.DataFrame([
        {"brand": "Coffee Fellows", "visibility_score": 2},
    ])

    metrics = build_executive_snapshot_metrics(
        summary_df,
        detailed_df,
        "Espresso House",
    )

    assert metrics["target_found"] is True
    assert metrics["organic_score"] == 0
