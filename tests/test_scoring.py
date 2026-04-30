import pandas as pd

from scoring import (
    calculate_share_of_voice,
    count_mentions,
    estimate_rank_from_list,
    summarize_results,
)


def test_count_mentions_is_case_insensitive():
    answer = "Dermaviduals is listed first. dermaviduals appears again."

    assert count_mentions(answer, "Dermaviduals") == 2


def test_count_mentions_returns_zero_when_brand_absent():
    answer = "This answer mentions other professional skincare brands."

    assert count_mentions(answer, "Dermaviduals") == 0


def test_estimate_rank_from_numbered_list():
    answer = """
1. Brand A - explanation
2. Dermaviduals - explanation
3. Brand C - explanation
"""

    assert estimate_rank_from_list(answer, "Dermaviduals") == 2


def test_estimate_rank_from_bullet_list():
    answer = """
- Brand A - explanation
- Dermaviduals - explanation
"""

    assert estimate_rank_from_list(answer, "Dermaviduals") == 2


def test_estimate_rank_returns_none_when_brand_not_in_list():
    answer = """
Dermaviduals is mentioned in a paragraph.
There is no ranked recommendation list here.
"""

    assert estimate_rank_from_list(answer, "Dermaviduals") is None


def test_calculate_share_of_voice_from_mentions():
    summary_df = pd.DataFrame(
        [
            {"brand": "Brand A", "total_mentions": 2},
            {"brand": "Brand B", "total_mentions": 6},
            {"brand": "Brand C", "total_mentions": 0},
        ]
    )

    result = calculate_share_of_voice(summary_df)

    assert result.loc[result["brand"] == "Brand A", "share_of_voice_percent"].iloc[0] == 25.0
    assert result.loc[result["brand"] == "Brand B", "share_of_voice_percent"].iloc[0] == 75.0
    assert result.loc[result["brand"] == "Brand C", "share_of_voice_percent"].iloc[0] == 0.0


def test_calculate_share_of_voice_handles_zero_total_mentions():
    summary_df = pd.DataFrame(
        [
            {"brand": "Brand A", "total_mentions": 0},
            {"brand": "Brand B", "total_mentions": 0},
        ]
    )

    result = calculate_share_of_voice(summary_df)

    assert result["share_of_voice_percent"].tolist() == [0, 0]


def test_summarize_results_groups_brand_metrics():
    all_results = [
        {
            "brand": "Dermaviduals",
            "mentions": 1,
            "visibility_score": 100,
            "estimated_rank": 1,
        },
        {
            "brand": "Dermaviduals",
            "mentions": 0,
            "visibility_score": 0,
            "estimated_rank": None,
        },
        {
            "brand": "Brand B",
            "mentions": 2,
            "visibility_score": 45,
            "estimated_rank": None,
        },
    ]

    detailed_df, summary_df = summarize_results(all_results)
    target_row = summary_df[summary_df["brand"] == "Dermaviduals"].iloc[0]
    competitor_row = summary_df[summary_df["brand"] == "Brand B"].iloc[0]

    assert len(detailed_df) == 3
    assert target_row["total_mentions"] == 1
    assert target_row["average_visibility_score"] == 50.0
    assert target_row["prompts_visible"] == 1
    assert target_row["best_estimated_rank"] == 1
    assert competitor_row["total_mentions"] == 2
    assert competitor_row["average_visibility_score"] == 45.0
    assert competitor_row["prompts_visible"] == 1
    assert competitor_row["best_estimated_rank"] == 0


def test_summarize_results_handles_empty_input():
    detailed_df, summary_df = summarize_results([])

    assert detailed_df.empty
    assert summary_df.empty
    assert list(summary_df.columns) == [
        "brand",
        "total_mentions",
        "average_visibility_score",
        "prompts_visible",
        "best_estimated_rank",
    ]
