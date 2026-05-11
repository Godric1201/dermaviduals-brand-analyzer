import pandas as pd

from geo_audit.report_diagnosis import (
    ASSOCIATION_GROWTH_STRATEGY,
    CATEGORY_OWNERSHIP_STRATEGY,
    EVIDENCE_TAXONOMY,
    FIRST_DETECTION_STRATEGY,
    VISIBILITY_CATEGORY_ANCHOR,
    VISIBILITY_COMPETITIVELY_VISIBLE,
    VISIBILITY_NOT_DETECTED,
    VISIBILITY_PARTIALLY_VISIBLE,
    VISIBILITY_WEAKLY_DETECTED,
    VisibilityMetrics,
    build_evidence_gap_map,
    build_first_detection_task_roadmap,
    build_market_relevance_interpretation,
    build_validation_plan,
    build_visible_reference_brands,
    classify_visibility_state,
    get_target_visibility_metrics,
    is_zero_visibility,
    select_strategy_mode,
)


def test_classify_visibility_state_uses_clear_thresholds():
    assert classify_visibility_state(VisibilityMetrics(0, 0, 0, 0)) == (
        VISIBILITY_NOT_DETECTED
    )
    assert classify_visibility_state(VisibilityMetrics(1, 10, 1, 1)) == (
        VISIBILITY_WEAKLY_DETECTED
    )
    assert classify_visibility_state(VisibilityMetrics(3, 20, 2, 3)) == (
        VISIBILITY_PARTIALLY_VISIBLE
    )
    assert classify_visibility_state(VisibilityMetrics(8, 45, 4, 10)) == (
        VISIBILITY_COMPETITIVELY_VISIBLE
    )
    assert classify_visibility_state(VisibilityMetrics(20, 65, 8, 25)) == (
        VISIBILITY_CATEGORY_ANCHOR
    )


def test_zero_visibility_selects_first_detection_strategy():
    metrics = VisibilityMetrics(
        total_mentions=0,
        average_visibility_score=0,
        prompts_visible=0,
        share_of_voice_percent=0,
    )

    assert is_zero_visibility(metrics)
    assert classify_visibility_state(metrics) == VISIBILITY_NOT_DETECTED
    assert select_strategy_mode(metrics) == FIRST_DETECTION_STRATEGY


def test_non_zero_average_visibility_is_not_not_detected():
    metrics = VisibilityMetrics(
        total_mentions=0,
        average_visibility_score=10,
        prompts_visible=0,
        share_of_voice_percent=0,
    )

    assert not is_zero_visibility(metrics)
    assert classify_visibility_state(metrics) == VISIBILITY_WEAKLY_DETECTED


def test_non_zero_visibility_selects_growth_or_ownership_strategy():
    assert select_strategy_mode(VisibilityMetrics(2, 10, 1, 2)) == (
        ASSOCIATION_GROWTH_STRATEGY
    )
    assert select_strategy_mode(VisibilityMetrics(10, 45, 4, 10)) == (
        CATEGORY_OWNERSHIP_STRATEGY
    )


def test_evidence_taxonomy_contains_required_categories():
    assert EVIDENCE_TAXONOMY == (
        "Entity Evidence",
        "Market Evidence",
        "Offering Evidence",
        "Trust Evidence",
        "Third-Party Evidence",
        "Comparison Evidence",
        "Structured Evidence",
        "Community Evidence",
    )


def test_get_target_visibility_metrics_handles_missing_target_as_zero():
    summary_df = pd.DataFrame([
        {
            "brand": "Reference Brand",
            "total_mentions": 6,
            "average_visibility_score": 50,
            "prompts_visible": 3,
            "share_of_voice_percent": 100,
        }
    ])

    metrics = get_target_visibility_metrics(summary_df, "Missing Brand")

    assert metrics == VisibilityMetrics(0, 0, 0, 0)


def test_visible_reference_brands_uses_reference_brand_language():
    summary_df = pd.DataFrame([
        {
            "brand": "Target Brand",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Global Leader",
            "total_mentions": 12,
            "average_visibility_score": 68,
            "prompts_visible": 4,
            "share_of_voice_percent": 70,
        },
    ])

    reference_brands = build_visible_reference_brands(summary_df, "Target Brand")

    assert reference_brands[0]["Brand"] == "Global Leader"
    assert reference_brands[0]["Reference Role"] == "Visible category anchor"
    assert "brand to attack" in reference_brands[0]["Interpretation"]


def test_market_relevance_interpretation_is_cautious():
    interpretation = build_market_relevance_interpretation(
        "Target Brand",
        "Taiwan and Asia-Pacific",
        "reinsurance",
        [{"Brand": "Munich Re"}],
    )

    assert "AI-visible reference brands" in interpretation
    assert "visible category anchors" in interpretation
    assert "may indicate" in interpretation
    assert "interpretation risk" in interpretation
    assert "not a confirmed fact" in interpretation


def test_evidence_gap_map_and_task_roadmap_are_actionable():
    gaps = build_evidence_gap_map(
        "Target Brand",
        "reinsurance",
        "Taiwan and Asia-Pacific",
        "enterprise buyers",
    )
    tasks = build_first_detection_task_roadmap(
        "Target Brand",
        "reinsurance",
        "Taiwan and Asia-Pacific",
        "enterprise buyers",
        [{"Brand": "Munich Re"}],
    )

    assert {row["Evidence Type"] for row in gaps} >= set(EVIDENCE_TAXONOMY)

    for row in gaps:
        assert row["Current Diagnosis"]
        assert row["Gap Addressed"]
        assert row["Why It Matters"]
        assert row["Validation Method"]

    for row in tasks:
        assert row["Action"]
        assert row["Gap Addressed"]
        assert row["Evidence Type"]
        assert row["Why It Matters"]
        assert row["Where Evidence Should Live"]
        assert row["Benchmark Validation Method"]
        assert row["Expected Influence"]
        assert "create more content" not in row["Action"].lower()
        assert "improve brand marketing" not in row["Action"].lower()


def test_validation_plan_defines_first_measurable_inclusion_without_timeline_promise():
    plan = build_validation_plan(["Best Options", "Local Recommendations"])
    combined = " ".join(row["Plan"] for row in plan)

    assert "First measurable inclusion" in combined
    assert "What does not count as proof" not in combined
    assert "No fixed timeline should be promised" in combined
    assert "promise AI mentions" in combined
