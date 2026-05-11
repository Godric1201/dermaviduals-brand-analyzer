import pandas as pd

from geo_audit.ui.results_sections import (
    build_executive_snapshot_metrics,
    build_prompt_matrix_display_df,
)


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


def test_build_prompt_matrix_display_df_translates_expected_columns():
    display_df = build_prompt_matrix_display_df([
        {
            "category": "Best Options",
            "prompt_category": "Local Recommendations",
            "prompt": "Which cafes are best for remote work?",
        }
    ])

    assert list(display_df.columns) == [
        "Category",
        "Prompt Category",
        "Prompt",
    ]


def test_build_prompt_matrix_display_df_handles_empty_prompt_list():
    display_df = build_prompt_matrix_display_df([])

    assert display_df.empty
    assert list(display_df.columns) == []


def test_build_prompt_matrix_display_df_preserves_prompt_values():
    display_df = build_prompt_matrix_display_df([
        {
            "category": "Best Options",
            "prompt_category": "Local Recommendations",
            "prompt": "Which cafes are best for remote work?",
        }
    ])

    assert display_df.iloc[0]["Category"] == "Best Options"
    assert display_df.iloc[0]["Prompt Category"] == "Local Recommendations"
    assert display_df.iloc[0]["Prompt"] == "Which cafes are best for remote work?"
