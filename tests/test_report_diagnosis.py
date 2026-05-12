import pandas as pd

from geo_audit.report_diagnosis import (
    ASSOCIATION_GROWTH_STRATEGY,
    CATEGORY_OWNERSHIP_STRATEGY,
    RELIABILITY_DIRECTIONAL,
    RELIABILITY_EXPLORATORY,
    RELIABILITY_INSUFFICIENT,
    RELIABILITY_STRONG,
    RETRIEVAL_ROLE_COMPARISON,
    RETRIEVAL_ROLE_BUDGET,
    RETRIEVAL_ROLE_LOCAL,
    RETRIEVAL_ROLE_PLANNING,
    RETRIEVAL_ROLE_TECHNICAL,
    RETRIEVAL_ROLE_TRUST,
    RETRIEVAL_ROLE_UNCLEAR,
    EVIDENCE_TAXONOMY,
    FIRST_DETECTION_STRATEGY,
    VISIBILITY_CATEGORY_ANCHOR,
    VISIBILITY_COMPETITIVELY_VISIBLE,
    VISIBILITY_NOT_DETECTED,
    VISIBILITY_PARTIALLY_VISIBLE,
    VISIBILITY_WEAKLY_DETECTED,
    VisibilityMetrics,
    build_first_three_evidence_assets,
    build_evidence_gap_map,
    build_first_detection_task_roadmap,
    build_retrieved_brand_profiles,
    build_secondary_retrieval_signals,
    build_market_relevance_interpretation,
    build_validation_plan,
    build_visible_reference_brands,
    classify_benchmark_reliability,
    classify_retrieval_role,
    classify_visibility_state,
    format_reference_brand_names,
    get_target_visibility_metrics,
    is_zero_visibility,
    select_strategy_mode,
    score_retrieval_roles,
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


def test_reference_brand_names_are_formatted_naturally():
    assert format_reference_brand_names([
        {"Brand": "Munich Re"},
    ]) == "Munich Re"
    assert format_reference_brand_names([
        {"Brand": "Munich Re"},
        {"Brand": "Swiss Re"},
    ]) == "Munich Re and Swiss Re"
    assert format_reference_brand_names([
        {"Brand": "Munich Re"},
        {"Brand": "Swiss Re"},
        {"Brand": "Hannover Re"},
    ]) == "Munich Re, Swiss Re, and Hannover Re"


def test_market_relevance_interpretation_uses_natural_two_brand_list():
    interpretation = build_market_relevance_interpretation(
        "Regional Re",
        "Taiwan and Asia-Pacific",
        "reinsurance",
        [{"Brand": "Munich Re"}, {"Brand": "Swiss Re"}],
    )

    assert (
        "The benchmark retrieved AI-visible reference brands such as Munich Re "
        "and Swiss Re, while Regional Re was not detected."
    ) in interpretation
    assert "may indicate" in interpretation
    assert "interpretation risk" in interpretation
    assert "not a confirmed fact" in interpretation
    assert "dedicated market-relevance probes" in interpretation


def test_benchmark_reliability_uses_conservative_labels():
    assert classify_benchmark_reliability(
        run_mode="Full Report Mode",
        prompt_categories=["Best Options"],
        reference_brands=[],
    )["label"] == RELIABILITY_INSUFFICIENT

    assert classify_benchmark_reliability(
        run_mode="Quick Test Mode",
        prompt_categories=["Best Options"],
        reference_brands=[{"Brand": "Reference Brand"}],
    )["label"] == RELIABILITY_EXPLORATORY

    directional = classify_benchmark_reliability(
        run_mode="Full Report Mode",
        prompt_categories=["Best Options", "Local Recommendations"],
        reference_brands=[{"Brand": "Reference Brand"}, {"Brand": "Second Brand"}],
    )
    assert directional["label"] == RELIABILITY_DIRECTIONAL
    assert directional["label"] != RELIABILITY_STRONG


def test_retrieval_role_classification_uses_prompt_signals():
    assert classify_retrieval_role(
        prompt_categories=["Alternatives and comparison prompts"],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_COMPARISON
    assert classify_retrieval_role(
        prompt_categories=["Trust And Review Signals"],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_TRUST
    assert classify_retrieval_role(
        prompt_categories=["Technical Infrastructure Use-Case Recommendations"],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_TECHNICAL
    assert classify_retrieval_role(
        prompt_categories=["Audience-Specific Advisory Recommendations"],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_PLANNING
    assert classify_retrieval_role(
        prompt_categories=["Budget-Friendly Options"],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_BUDGET
    assert classify_retrieval_role(
        prompt_categories=[],
        visible_market_fit="Market-relevant",
    ) == RETRIEVAL_ROLE_LOCAL
    assert classify_retrieval_role(
        prompt_categories=["General prompts"]
    ) == RETRIEVAL_ROLE_UNCLEAR


def test_secondary_retrieval_signals_exclude_primary_role():
    role_scores = score_retrieval_roles(
        prompt_categories=[
            "Alternatives To Leading Competitors",
            "Trust And Review Signals",
            "Audience-Specific Advisory Recommendations",
            "Use-Case Recommendations",
        ],
        visible_market_fit="Market-relevant",
    )
    primary_role = classify_retrieval_role(
        prompt_categories=[
            "Alternatives To Leading Competitors",
            "Trust And Review Signals",
            "Audience-Specific Advisory Recommendations",
            "Use-Case Recommendations",
        ],
        visible_market_fit="Market-relevant",
    )
    secondary = build_secondary_retrieval_signals(role_scores, primary_role)

    assert primary_role == RETRIEVAL_ROLE_COMPARISON
    assert RETRIEVAL_ROLE_TRUST in secondary
    assert RETRIEVAL_ROLE_LOCAL not in secondary
    assert len(secondary) <= 2


def test_retrieved_brand_profiles_are_cautious_and_structured():
    summary_df = pd.DataFrame([
        {
            "brand": "Target Brand",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Global Reference",
            "total_mentions": 18,
            "average_visibility_score": 75,
            "prompts_visible": 6,
            "share_of_voice_percent": 45,
        },
    ])
    top_brands_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Global Reference",
            "visibility_score": 75,
        }
    ])

    profiles = build_retrieved_brand_profiles(
        summary_df,
        "Target Brand",
        top_brands_df=top_brands_df,
    )

    assert profiles[0]["brand"] == "Global Reference"
    assert profiles[0]["competitor_tier"] == "Category anchor"
    assert profiles[0]["retrieval_role"] == RETRIEVAL_ROLE_TRUST
    assert "Based on this benchmark" in profiles[0]["inferred_reason"]
    assert "requires validation" in profiles[0]["required_validation"]


def test_retrieved_brand_profiles_differentiate_market_relevant_brands():
    summary_df = pd.DataFrame([
        {
            "brand": "Target Brand",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Rittal",
            "total_mentions": 20,
            "average_visibility_score": 82,
            "prompts_visible": 5,
            "share_of_voice_percent": 40,
        },
        {
            "brand": "Arup",
            "total_mentions": 12,
            "average_visibility_score": 55,
            "prompts_visible": 3,
            "share_of_voice_percent": 25,
        },
        {
            "brand": "Drees & Sommer",
            "total_mentions": 8,
            "average_visibility_score": 45,
            "prompts_visible": 2,
            "share_of_voice_percent": 15,
        },
    ])
    top_brands_df = pd.DataFrame([
        {"prompt_category": "Best Options", "brand": "Rittal", "visibility_score": 80},
        {"prompt_category": "Budget-Friendly Options", "brand": "Rittal", "visibility_score": 70},
        {"prompt_category": "Premium Options", "brand": "Rittal", "visibility_score": 85},
        {"prompt_category": "Audience-Specific Recommendations", "brand": "Arup", "visibility_score": 60},
        {"prompt_category": "Alternatives To Leading Competitors", "brand": "Drees & Sommer", "visibility_score": 55},
        {"prompt_category": "Trust And Review Signals", "brand": "Drees & Sommer", "visibility_score": 50},
    ])
    detailed_pivot_df = pd.DataFrame([
        {
            "prompt_category": "Use-Case Recommendations",
            "Rittal": 72,
            "Arup": 58,
            "Drees & Sommer": 0,
        },
        {
            "prompt_category": "AI Generated - Alternatives",
            "Rittal": 74,
            "Arup": 0,
            "Drees & Sommer": 0,
        },
        {
            "prompt_category": "AI Generated - Local Recommendations",
            "Rittal": 0,
            "Arup": 56,
            "Drees & Sommer": 0,
        },
    ])
    market_relevance = {
        "visible_market_fit": [
            {"brand": "Rittal", "market_fit": "Market-relevant", "rationale": "Market fit appears plausible."},
            {"brand": "Arup", "market_fit": "Market-relevant", "rationale": "Market fit appears plausible."},
            {"brand": "Drees & Sommer", "market_fit": "Market-relevant", "rationale": "Market fit appears plausible."},
        ]
    }

    profiles = build_retrieved_brand_profiles(
        summary_df,
        "Target Brand",
        top_brands_df=top_brands_df,
        detailed_pivot_df=detailed_pivot_df,
        market_relevance=market_relevance,
    )
    roles_by_brand = {
        profile["brand"]: profile["retrieval_role"]
        for profile in profiles
    }

    assert roles_by_brand["Rittal"] == RETRIEVAL_ROLE_TRUST
    assert roles_by_brand["Arup"] == RETRIEVAL_ROLE_PLANNING
    assert roles_by_brand["Drees & Sommer"] == RETRIEVAL_ROLE_COMPARISON
    assert len(set(roles_by_brand.values())) > 1
    assert set(roles_by_brand.values()) != {RETRIEVAL_ROLE_LOCAL}

    for profile in profiles:
        assert profile["primary_retrieval_role"] == profile["retrieval_role"]
        assert profile["role_basis"]
        assert "Query-type signals:" not in profile["role_basis"]
        assert profile["market_fit_modifier"]


def test_retrieved_brand_profiles_use_detailed_pivot_categories_when_not_top_winner():
    summary_df = pd.DataFrame([
        {
            "brand": "Target Brand",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Tech Brand",
            "total_mentions": 6,
            "average_visibility_score": 35,
            "prompts_visible": 2,
            "share_of_voice_percent": 30,
        },
    ])
    top_brands_df = pd.DataFrame([
        {"prompt_category": "Best Options", "brand": "Other Brand", "visibility_score": 70},
    ])
    detailed_pivot_df = pd.DataFrame([
        {
            "prompt_category": "Technical Infrastructure Recommendations",
            "Tech Brand": 42,
            "Other Brand": 70,
        }
    ])

    profiles = build_retrieved_brand_profiles(
        summary_df,
        "Target Brand",
        top_brands_df=top_brands_df,
        detailed_pivot_df=detailed_pivot_df,
    )

    assert profiles[0]["brand"] == "Tech Brand"
    assert profiles[0]["retrieval_role"] == RETRIEVAL_ROLE_TECHNICAL
    assert "Technical Infrastructure Recommendations" in profiles[0]["prompt_categories"]


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


def test_first_three_evidence_assets_prioritize_entity_and_market_gaps():
    assets = build_first_three_evidence_assets(
        brand="Target Brand",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise buyers",
        reference_brands=[{"Brand": "Munich Re"}],
        retrieved_brand_profiles=[{
            "retrieval_role": RETRIEVAL_ROLE_COMPARISON,
        }],
        brand_understanding=None,
        market_relevance={
            "market_lock_status": "Global-default risk",
            "local_brand_presence_signal": "Weak",
        },
        prompt_categories=["Best Options", "Local Recommendations"],
    )

    assert len(assets) == 3
    assert assets[0]["asset_name"] == "Target Brand service/category entity page"
    assert "market relevance" in assets[1]["asset_name"].lower()
    assert assets[2]["asset_name"] == "Reinsurance alternatives and comparison page"

    for asset in assets:
        assert asset["priority"]
        assert asset["asset_name"]
        assert asset["what_to_build"]
        assert asset["why_it_matters"]
        assert asset["target_retrieval_driver"]
        assert asset["targets_or_prompt_groups"]
        assert asset["validation"]
        combined = " ".join(str(value).lower() for value in asset.values())
        assert "improve marketing" not in combined
        assert "create more content" not in combined
        assert "get more reviews" not in combined


def test_first_three_evidence_assets_use_differentiated_role_distribution():
    assets = build_first_three_evidence_assets(
        brand="Target Brand",
        category="data center providers",
        market="Germany",
        audience="enterprise infrastructure buyers",
        reference_brands=[{"Brand": "Rittal"}],
        retrieved_brand_profiles=[
            {"retrieval_role": RETRIEVAL_ROLE_TECHNICAL},
            {"retrieval_role": RETRIEVAL_ROLE_PLANNING},
            {"retrieval_role": RETRIEVAL_ROLE_COMPARISON},
        ],
        brand_understanding={
            "brand_known_status": "Clear",
            "category_alignment": "Clear",
            "market_alignment": "Clear",
            "audience_alignment": "Clear",
        },
        market_relevance={
            "market_lock_status": "Market-specific",
            "local_brand_presence_signal": "Clear",
        },
        prompt_categories=["Technical Infrastructure", "Audience-Specific", "Alternatives"],
    )

    assert len(assets) == 3
    assert assets[0]["asset_name"] == "Data center infrastructure capability proof page"
    assert assets[1]["asset_name"] == "Germany planning and project credibility page"
    assert assets[2]["asset_name"] == "Data center infrastructure alternatives and comparison page"

    for asset in assets:
        assert asset["priority"]
        assert asset["what_to_build"]
        assert asset["why_it_matters"]
        assert asset["target_retrieval_driver"]
        assert asset["targets_or_prompt_groups"]
        assert asset["validation"]


def test_first_three_evidence_asset_names_shorten_long_categories():
    long_category = (
        "Data center infrastructure consulting, planning, construction, "
        "and technical services"
    )
    assets = build_first_three_evidence_assets(
        brand="DC-Datacenter-Group GmbH",
        category=long_category,
        market="Germany",
        audience="enterprise infrastructure buyers",
        reference_brands=[{"Brand": "Rittal"}],
        retrieved_brand_profiles=[
            {"retrieval_role": RETRIEVAL_ROLE_COMPARISON},
            {"retrieval_role": RETRIEVAL_ROLE_TRUST},
        ],
        brand_understanding=None,
        market_relevance={
            "market_lock_status": "Market-specific",
            "local_brand_presence_signal": "Clear",
        },
        prompt_categories=["Alternatives", "Trust And Review Signals"],
    )

    asset_names = [asset["asset_name"] for asset in assets]

    assert "DC-Datacenter-Group GmbH service/category entity page" in asset_names
    assert "Data center infrastructure alternatives and comparison page" in asset_names
    assert long_category not in " ".join(asset_names)


def test_validation_plan_defines_first_measurable_inclusion_without_timeline_promise():
    plan = build_validation_plan(["Best Options", "Local Recommendations"])
    combined = " ".join(row["Plan"] for row in plan)

    assert "First measurable inclusion" in combined
    assert "What does not count as proof" not in combined
    assert "No fixed timeline should be promised" in combined
    assert "promise AI mentions" in combined
