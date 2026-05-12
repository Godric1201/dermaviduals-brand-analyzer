import pandas as pd

from geo_audit.brand_understanding import BrandUnderstandingProbeResult
from geo_audit.market_relevance import MarketRelevanceProbeResult
from geo_audit.markdown_report import build_executive_markdown_report
from geo_audit.output_quality import (
    FAILED_LLM_SECTION_PLACEHOLDER,
    OutputQualityContext,
    validate_output_quality,
)


def create_markdown_inputs():
    summary_df = pd.DataFrame([
        {
            "brand": "espresso house",
            "total_mentions": 2,
            "average_visibility_score": 3.5,
            "prompts_visible": 2,
            "share_of_voice_percent": 20.0,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 8,
            "average_visibility_score": 7.2,
            "prompts_visible": 4,
            "share_of_voice_percent": 80.0,
        },
    ])
    summary_display_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 2,
            "average_visibility_score": 3.5,
            "prompts_visible": 2,
            "share_of_voice_percent": 20.0,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 8,
            "average_visibility_score": 7.2,
            "prompts_visible": 4,
            "share_of_voice_percent": 80.0,
        },
    ])
    detailed_pivot_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "Espresso House": 2.0,
            "Coffee Fellows": 7.0,
        }
    ])
    top_brands_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Coffee Fellows",
            "visibility_score": 7.0,
        }
    ])

    return {
        "brand": "espresso house",
        "display_brand": "Espresso House",
        "category": "cafes",
        "display_category": "Cafes",
        "market": "Berlin",
        "display_market": "Berlin",
        "audience": "remote workers",
        "display_audience": "Remote Workers",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "deliverable_status": "Client Deliverable",
        "summary_df": summary_df,
        "summary_display_df": summary_display_df,
        "detailed_pivot_df": detailed_pivot_df,
        "top_brands_df": top_brands_df,
        "recommendations": "Test recommendations",
        "plan": "Test strategy plan",
        "gap_analysis": "Test gap analysis",
        "brand_win_explanation": "Test brand win explanation",
        "replacement_strategy": "Test replacement strategy",
        "brand_intelligence": {
            "recommendation_drivers": "Test recommendation drivers",
            "target_brand_understanding": "Test target brand understanding",
            "positioning_gap_analysis": "Test positioning gap analysis",
        },
        "brand_intelligence_done": True,
        "geo_content_roadmap": "| Priority | Query Intent |\n|---|---|\n| 1 | Best Options |",
        "geo_content_roadmap_done": True,
        "prompt_categories": ["Best Options", "Local Recommendations"],
    }


def create_zero_visibility_markdown_inputs():
    inputs = create_markdown_inputs()
    summary_df = pd.DataFrame([
        {
            "brand": "Regional Re",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Munich Re",
            "total_mentions": 18,
            "average_visibility_score": 75.0,
            "prompts_visible": 6,
            "share_of_voice_percent": 45.0,
        },
        {
            "brand": "Swiss Re",
            "total_mentions": 14,
            "average_visibility_score": 68.0,
            "prompts_visible": 5,
            "share_of_voice_percent": 35.0,
        },
    ])
    detailed_pivot_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "Regional Re": 0,
            "Munich Re": 75.0,
            "Swiss Re": 68.0,
        },
        {
            "prompt_category": "Local Recommendations",
            "Regional Re": 0,
            "Munich Re": 65.0,
            "Swiss Re": 60.0,
        },
    ])
    top_brands_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Munich Re",
            "visibility_score": 75.0,
        },
        {
            "prompt_category": "Local Recommendations",
            "brand": "Swiss Re",
            "visibility_score": 60.0,
        },
    ])
    inputs.update({
        "brand": "Regional Re",
        "display_brand": "Regional Re",
        "category": "reinsurance",
        "display_category": "Reinsurance",
        "market": "Taiwan and Asia-Pacific",
        "display_market": "Taiwan and Asia-Pacific",
        "audience": "enterprise insurance buyers",
        "display_audience": "Enterprise Insurance Buyers",
        "summary_df": summary_df,
        "summary_display_df": summary_df.copy(),
        "detailed_pivot_df": detailed_pivot_df,
        "top_brands_df": top_brands_df,
        "geo_content_roadmap": None,
        "geo_content_roadmap_done": False,
        "brand_intelligence": None,
        "brand_intelligence_done": False,
        "prompt_categories": ["Best Options", "Local Recommendations"],
    })
    return inputs


def create_brand_understanding_result(**overrides):
    values = {
        "brand_known_status": "Clear",
        "inferred_category": "Regional reinsurance provider",
        "category_alignment": "Clear",
        "inferred_market": "Taiwan and Asia-Pacific",
        "market_alignment": "Clear",
        "inferred_audience": "Enterprise Insurance Buyers",
        "audience_alignment": "Clear",
        "inferred_offerings": ["Treaty reinsurance"],
        "inferred_strengths": ["Regional market knowledge"],
        "missing_or_uncertain_evidence": ["Third-party proof points"],
        "possible_hallucinations": [],
        "diagnosis_summary": "Regional Re appears known but not naturally retrieved.",
        "recommended_interpretation": "Recommendation retrieval gap",
        "validation_note": "AI-inferred brand understanding probe. Validate before using as client-facing fact.",
    }
    values.update(overrides)
    return BrandUnderstandingProbeResult(**values)


def create_market_relevance_result(**overrides):
    values = {
        "market_lock_status": "Global-default risk",
        "local_brand_presence_signal": "Weak",
        "visible_market_fit": [
            {
                "brand": "Munich Re",
                "market_fit": "Global-default",
                "rationale": "Highly visible global category anchor.",
            }
        ],
        "global_default_risk_reason": "Visible brands are globally famous category leaders.",
        "market_evidence_gap_summary": "Local and regional market evidence is not visible in the benchmark context.",
        "recommended_interpretation": "Global-default retrieval risk",
        "validation_note": "AI-inferred market relevance probe. Validate before using as client-facing fact.",
    }
    values.update(overrides)
    return MarketRelevanceProbeResult(**values)


def create_role_differentiation_markdown_inputs():
    inputs = create_zero_visibility_markdown_inputs()
    summary_df = pd.DataFrame([
        {
            "brand": "Regional DC",
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
    detailed_pivot_df = pd.DataFrame([
        {
            "prompt_category": "Use-Case Recommendations",
            "Regional DC": 0,
            "Rittal": 72,
            "Arup": 58,
            "Drees & Sommer": 0,
        },
        {
            "prompt_category": "AI Generated - Alternatives",
            "Regional DC": 0,
            "Rittal": 74,
            "Arup": 0,
            "Drees & Sommer": 0,
        },
        {
            "prompt_category": "AI Generated - Local Recommendations",
            "Regional DC": 0,
            "Rittal": 0,
            "Arup": 56,
            "Drees & Sommer": 0,
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
    inputs.update({
        "brand": "Regional DC",
        "display_brand": "Regional DC",
        "category": "data center providers",
        "display_category": "Data Center Providers",
        "market": "Germany",
        "display_market": "Germany",
        "audience": "enterprise infrastructure buyers",
        "display_audience": "Enterprise Infrastructure Buyers",
        "summary_df": summary_df,
        "summary_display_df": summary_df.copy(),
        "detailed_pivot_df": detailed_pivot_df,
        "top_brands_df": top_brands_df,
        "prompt_categories": [
            "Best Options",
            "Budget-Friendly Options",
            "Premium Options",
            "Audience-Specific Recommendations",
            "Alternatives To Leading Competitors",
            "Trust And Review Signals",
        ],
        "market_relevance": create_market_relevance_result(
            market_lock_status="Market-specific",
            local_brand_presence_signal="Clear",
            visible_market_fit=[
                {
                    "brand": "Rittal",
                    "market_fit": "Market-relevant",
                    "rationale": "Market fit appears plausible.",
                },
                {
                    "brand": "Arup",
                    "market_fit": "Market-relevant",
                    "rationale": "Market fit appears plausible.",
                },
                {
                    "brand": "Drees & Sommer",
                    "market_fit": "Market-relevant",
                    "rationale": "Market fit appears plausible.",
                },
            ],
            recommended_interpretation="Market-specific competitive gap",
        ),
        "market_relevance_done": True,
    })
    return inputs


def test_build_executive_markdown_report_returns_string_with_core_sections():
    report = build_executive_markdown_report(**create_markdown_inputs())

    assert isinstance(report, str)
    assert "Report Overview" in report
    assert "Executive Summary" in report
    assert "Competitive Benchmark" in report
    assert "Trigger-Level Visibility Findings" in report
    assert "Top Brand Winners by Query Type" in report
    assert "GEO Content Roadmap" in report
    assert "Measurement Plan" in report
    assert "Query Intent Coverage" in report
    assert "Brand" in report
    assert "Total Mentions" in report
    assert "Average Visibility Score" in report
    assert "Prompts Visible" in report
    assert "Share of Voice %" in report
    assert "Espresso House" in report
    assert "Berlin" in report
    assert "Cafes" in report
    assert "Remote Workers" in report
    assert "Appendix B: AI Visibility Strategy Deep Dive" in report
    assert "Test strategy plan" in report


def test_build_executive_markdown_report_uses_first_detection_strategy_for_zero_visibility():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())

    expected_order = [
        "## 1. Recommendation Readiness Verdict",
        "## 2. Brand Understanding Summary",
        "## 3. Who AI Retrieved Instead",
        "## 4. Why Those Brands Were Retrieved",
        "## 5. Target vs Retrieved Brand Gap",
        "## 6. First 3 Evidence Assets to Build",
        "## 7. Validation Plan",
        "## 8. Supporting Benchmark Data",
        "## 9. Methodology / Reliability Notes",
    ]

    last_index = -1
    for heading in expected_order:
        current_index = report.index(heading)
        assert current_index > last_index
        last_index = current_index

    assert "Not Detected" in report
    assert "First Detection Strategy" in report
    assert "candidate-set inclusion" in report
    assert "Reliability Level" in report
    assert "Evidence Gap Map" in report
    assert "First 3 Evidence Assets to Build" in report
    assert "Validation Plan" in report
    assert "first measurable inclusion" in report
    assert "0 total mentions" in report
    assert "The Brand Understanding Probe was not available" in report
    assert "The Market Relevance Probe was not available" in report
    assert "Evidence-Building Task Roadmap" not in report


def test_zero_visibility_diagnosis_sections_use_cards_instead_of_wide_tables():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())

    assert "Evidence Gap Map" in report
    assert "First 3 Evidence Assets to Build" in report
    assert "Validation Plan" in report
    assert (
        "| Evidence Type | Current Diagnosis | Gap Addressed | Why It Matters | Validation Method |"
        not in report
    )
    assert (
        "| Action | Gap Addressed | Evidence Type | Why It Matters | Where Evidence Should Live |"
        not in report
    )
    assert "**Entity Evidence**" in report
    assert "- Current diagnosis:" in report
    assert "- Gap addressed:" in report
    assert "- Why it matters:" in report
    assert "- Validation:" in report
    assert "**Priority 1 - Regional Re service/category entity page**" in report
    assert "- What to build:" in report
    assert "- Target retrieval driver:" in report
    assert "- Targets / prompt groups:" in report


def test_zero_visibility_report_renders_exactly_three_priority_assets():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())
    assets_section = report.split("## 6. First 3 Evidence Assets to Build", 1)[1]
    assets_section = assets_section.split("## 7. Validation Plan", 1)[0]

    assert assets_section.count("**Priority ") == 3
    assert assets_section.count("- What to build:") == 3
    assert assets_section.count("- Why it matters:") == 3
    assert assets_section.count("- Target retrieval driver:") == 3
    assert assets_section.count("- Targets / prompt groups:") == 3
    assert assets_section.count("- Validation:") == 3


def test_zero_visibility_supporting_data_contains_demoted_evidence_gap_and_tables():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())
    supporting_section = report.split("## 8. Supporting Benchmark Data", 1)[1]
    supporting_section = supporting_section.split("## 9. Methodology / Reliability Notes", 1)[0]

    assert "### Evidence Gap Map" in supporting_section
    assert "### Competitive Benchmark" in supporting_section
    assert "### Trigger-Level Visibility Findings" in supporting_section
    assert "### Top Brand Winners by Query Type" in supporting_section
    assert report.index("### Evidence Gap Map") > report.index("## 8. Supporting Benchmark Data")
    assert "## 4. Evidence Gap Map" not in report
    assert "## 5. Evidence-Building Task Roadmap" not in report


def test_zero_visibility_markdown_uses_clear_brand_understanding_probe_cautiously():
    inputs = create_zero_visibility_markdown_inputs()
    inputs["brand_understanding"] = create_brand_understanding_result()
    inputs["brand_understanding_done"] = True

    report = build_executive_markdown_report(**inputs)

    assert "Brand Understanding Probe" in report
    assert "AI-inferred" in report
    assert "appears to be recognized" in report
    assert "recommendation retrieval, evidence depth, or market relevance" in report
    assert "requires validation" in report.lower()
    assert "Recommendation retrieval gap" in report
    assert "| Probe Signal | AI-Inferred Result |" not in report
    assert "- Brand understanding: Clear" in report
    assert "- Category alignment: Clear" in report
    assert "- Recommended interpretation: Recommendation retrieval gap" in report


def test_zero_visibility_markdown_flags_probe_alignment_problem_cautiously():
    inputs = create_zero_visibility_markdown_inputs()
    inputs["brand_understanding"] = create_brand_understanding_result(
        category_alignment="Misaligned",
        market_alignment="Misaligned",
        recommended_interpretation="Mixed diagnosis",
        diagnosis_summary="The brand appears associated with a different category and market.",
    )
    inputs["brand_understanding_done"] = True

    report = build_executive_markdown_report(**inputs)

    assert "alignment problem" in report
    assert "category and market contexts" in report
    assert "not only a lack of evidence" in report
    assert "requires validation" in report.lower()


def test_zero_visibility_markdown_uses_reference_brand_and_market_risk_language():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())

    assert "AI-visible reference brands" in report
    assert "category anchors" in report
    assert "retrieved alternatives" in report
    assert "Benchmark-based retrieval role" in report
    assert "Target vs Retrieved Brand Gap" in report
    assert "Observed benchmark signal" in report
    assert "Inferred retrieval role" in report
    assert "Required validation" in report
    assert "not verified competitive intelligence" in report
    assert "may indicate" in report
    assert "interpretation risk" in report
    assert "not a confirmed fact" in report
    assert "Munich Re" in report
    assert "Swiss Re" in report


def test_zero_visibility_markdown_differentiates_market_relevant_retrieval_roles():
    report = build_executive_markdown_report(
        **create_role_differentiation_markdown_inputs()
    )

    assert "- Benchmark-based retrieval role: Trust / premium reference" in report
    assert "- Benchmark-based retrieval role: Planning / consulting authority" in report
    assert "- Benchmark-based retrieval role: Comparison anchor" in report
    assert "Secondary signals:" in report
    assert "Role basis:" in report
    assert "Market note:" in report
    assert "Role signal summary:" not in report
    assert "Market-fit modifier:" not in report
    assert "Query-type signals:" not in report
    assert "AI Generated - Alternatives, AI Generated - Local Recommendations" not in report
    assert "use as a modifier, not verified market fact" in report

    roles_section = report.split("## 4. Why Those Brands Were Retrieved", 1)[1]
    roles_section = roles_section.split("## 5. Target vs Retrieved Brand Gap", 1)[0]
    assert "- Benchmark-based retrieval role: Local market provider" not in roles_section

    for line in roles_section.splitlines():
        if line.startswith("- Secondary signals:"):
            assert line.count(",") <= 1
            assert "Local market provider" not in line


def test_zero_visibility_markdown_uses_global_default_market_probe_cautiously():
    inputs = create_zero_visibility_markdown_inputs()
    inputs["market_relevance"] = create_market_relevance_result()
    inputs["market_relevance_done"] = True

    report = build_executive_markdown_report(**inputs)

    assert "Market Relevance Probe" in report
    assert "AI-inferred" in report
    assert "appears to lean toward globally visible category anchors" in report
    assert "may indicate a market evidence gap" in report
    assert "requires validation" in report.lower()
    assert "not a verified market fact" in report
    assert "Global-default retrieval risk" in report
    assert "| Probe Signal | AI-Inferred Result |" not in report
    assert "| Visible Brand | Market Fit | Rationale |" not in report
    assert "- Market lock status: Global-default risk" in report
    assert "- Local brand presence: Weak" in report
    assert "- Munich Re — Global-default: Highly visible global category anchor." in report


def test_zero_visibility_market_specific_probe_does_not_confirm_global_default_behavior():
    inputs = create_zero_visibility_markdown_inputs()
    inputs["market_relevance"] = create_market_relevance_result(
        market_lock_status="Market-specific",
        local_brand_presence_signal="Clear",
        visible_market_fit=[
            {
                "brand": "Swiss Re",
                "market_fit": "Market-relevant",
                "rationale": "Appears relevant to the target market context.",
            }
        ],
        global_default_risk_reason="No clear global-default risk from the compact context.",
        market_evidence_gap_summary="Visible brands appear to have market relevance.",
        recommended_interpretation="Market-specific competitive gap",
    )
    inputs["market_relevance_done"] = True

    report = build_executive_markdown_report(**inputs)

    assert "Market Relevance Probe" in report
    assert "visible brands appear to have market relevance" in report
    assert "less likely to be only a global-default artifact" in report
    assert "requires validation" in report.lower()
    assert "confirmed global-default" not in report.lower()


def test_zero_visibility_markdown_avoids_generic_or_overpromised_objectives():
    report = build_executive_markdown_report(**create_zero_visibility_markdown_inputs())
    report_lower = report.lower()

    blocked_phrases = [
        "improve brand marketing",
        "get more reviews",
        "create more content",
        "guarantee ai mentions",
        "will get mentioned",
        "will improve share of voice",
        "proven market leader",
        "share-of-voice growth is the first objective",
        "30 / 60 / 90 Day Roadmap",
    ]

    for phrase in blocked_phrases:
        assert phrase not in report_lower

    assert "no fixed timeline should be promised" in report_lower
    assert "candidate-set inclusion" in report_lower
    assert "share-of-voice growth should come after" in report_lower
    assert "not verified market fact" in report_lower


def test_non_zero_markdown_stays_on_existing_report_path():
    report = build_executive_markdown_report(**create_markdown_inputs())

    assert "## 2. Executive Summary" in report
    assert "## 7. Strategic Priorities" in report
    assert "## 9. 30 / 60 / 90 Day Roadmap" in report
    assert "First Detection Strategy" not in report
    assert "Evidence-Building Task Roadmap" not in report


def test_build_executive_markdown_report_normalizes_dirty_appendix_text():
    inputs = create_markdown_inputs()
    inputs["display_brand"] = "Espresso House"
    inputs["plan"] = (
        "Dominant brand: Coffee Fellows is dominating the market. "
        "iS Clinical dominates with skincare signals. "
        "Espresso House must enhance local recommendations."
    )
    inputs["brand_win_explanation"] = (
        "Why AI selects it: Coffee Fellows has convenient locations. "
        "What signal it owns: remote worker cafe intent. "
        "AI algorithms analyzing consumer intent identify a preferred choice. "
        "Consumers are actively seeking quiet locations."
    )
    inputs["replacement_strategy"] = (
        "AI-owned territory: Coffee Fellows appears for Berlin cafe queries. "
        "Owned territory: consumer preference and trust among consumers."
    )
    inputs["gap_analysis"] = (
        "Why AI Does Not Recommend Espresso House: "
        "Dominant brands suggest Espresso House must position itself more clearly. "
        "Consumer confidence affects decision-making in this market."
    )

    report = build_executive_markdown_report(**inputs)
    report_lower = report.lower()

    for phrase in [
        "Why AI selects it",
        "What signal it owns",
        "AI-owned territory",
        "Dominant brands",
        "dominant brand",
        "dominates",
        "dominating the market",
        "preferred choice",
        "AI algorithms analyzing consumer intent",
        "must enhance",
        "consumers are actively seeking",
        "trust among consumers",
        "consumer confidence",
        "decision-making in this market",
        "Why AI Does Not Recommend",
        "must position itself",
    ]:
        assert phrase.lower() not in report_lower

    assert "Espresso House" in report
    assert "Coffee Fellows" in report
    assert "iS Clinical" in report
    assert "Benchmark signal behind visibility" in report
    assert "Observed query territory signal" in report
    assert "observed query territory signal" in report
    assert "brand with stronger measured visibility" in report
    assert "brands with stronger measured visibility" in report
    assert "showing stronger measured visibility in this benchmark" in report
    assert "generated answers in this benchmark" in report
    assert "more visible option in this benchmark" in report
    assert "tested prompts reflect demand for quiet locations" in report
    assert "trust-related signals in generated answers" in report
    assert "trust-related confidence signal" in report
    assert "decision-stage query context" in report
    assert "iS Clinical shows stronger measured visibility with skincare signals" in report
    assert "should strengthen local recommendations" in report
    assert "Benchmark-Visible Associations Missing or Weak for Espresso House" in report
    assert "should clarify its benchmark positioning" in report


def test_build_executive_markdown_report_uses_clean_measurement_targets():
    report = build_executive_markdown_report(**create_markdown_inputs())

    expected_targets = [
        "Begin generating detectable mentions in the next benchmark cycle.",
        "Begin improving average visibility score in the next benchmark cycle.",
        "Begin generating prompt-level visibility in relevant query categories.",
        "Begin generating measurable share of voice in the next benchmark cycle.",
    ]
    blocked_targets = [
        "At least 5 detectable mentions",
        "Above 5.0",
        "Visible in at least 3 prompt categories",
        "At least 5%",
        "detectable mentions in a future full benchmark",
    ]

    for target in expected_targets:
        assert target in report

    for target in blocked_targets:
        assert target not in report


def test_build_executive_markdown_report_uses_consistent_methodology_outcome_wording():
    report = build_executive_markdown_report(**create_markdown_inputs())

    expected = (
        "Scores reflect AI answer visibility, not market share, product performance, "
        "customer satisfaction, or broader business performance outcomes."
    )

    assert expected in report
    assert "not actual business performance outcomes, market share" not in report
    assert report.count("business performance outcomes") == 1
    assert "business outcomes." not in report
    assert "business outcome Performance Metrics" not in report


def test_build_executive_markdown_report_uses_client_facing_table_headers():
    report = build_executive_markdown_report(**create_markdown_inputs())

    assert "total_mentions" not in report
    assert "average_visibility_score" not in report
    assert "share_of_voice_percent" not in report
    assert "Query Type" in report
    assert "Brand" in report
    assert "Visibility Score" in report


def test_build_executive_markdown_report_includes_quick_test_warning():
    inputs = create_markdown_inputs()
    inputs["run_mode"] = "Quick Test Mode"
    inputs["prompt_limit"] = 1
    inputs["deliverable_status"] = "Not Client Deliverable"

    report = build_executive_markdown_report(**inputs)

    assert "TEST VERSION ONLY" in report
    assert "Not Client Deliverable" in report


def test_build_executive_markdown_report_includes_optional_appendices():
    report = build_executive_markdown_report(**create_markdown_inputs())

    assert "Appendix A: Brand Intelligence & Positioning Audit" in report
    assert "GEO Content Roadmap" in report
    assert "Tracked competitors are included in visibility scoring and share of voice." in report
    assert "AI-discovered market signals are diagnostic references only" in report


def test_build_executive_markdown_report_avoids_duplicate_market_in_intro():
    inputs = create_markdown_inputs()
    inputs["display_brand"] = "Dermaviduals"
    inputs["display_category"] = "Professional Skincare Products"
    inputs["display_market"] = "Hong Kong"
    inputs["display_audience"] = "skincare-conscious consumers in Hong Kong"

    report = build_executive_markdown_report(**inputs)

    assert "in Hong Kong in Hong Kong" not in report
    assert "recommendations for skincare-conscious consumers in Hong Kong" in report
    assert "based on the tested prompt set" in report


def test_build_executive_markdown_report_omits_optional_appendices_when_absent():
    inputs = create_markdown_inputs()
    inputs["brand_intelligence"] = None
    inputs["brand_intelligence_done"] = False
    inputs["geo_content_roadmap"] = None
    inputs["geo_content_roadmap_done"] = False
    inputs["brand_win_explanation"] = None
    inputs["replacement_strategy"] = None
    inputs["gap_analysis"] = None

    report = build_executive_markdown_report(**inputs)

    assert "Brand Intelligence & Positioning Audit" not in report
    assert "GEO Content Roadmap" not in report
    assert "Appendix A:" not in report
    assert "Appendix C:" not in report
    assert "Appendix D:" not in report
    assert "Appendix E:" not in report


def test_build_executive_markdown_report_avoids_blocked_skincare_terms_for_generic_case():
    report = build_executive_markdown_report(**create_markdown_inputs())

    blocked_terms = [
        "professional skincare",
        "clinic-grade",
        "barrier repair",
        "post-treatment",
        "Hong Kong professional skincare",
    ]

    report_lower = report.lower()
    for term in blocked_terms:
        assert term.lower() not in report_lower


def test_build_executive_markdown_report_handles_missing_target_row_without_crashing():
    inputs = create_markdown_inputs()
    inputs["brand"] = "missing brand"
    inputs["display_brand"] = "Missing Brand"

    report = build_executive_markdown_report(**inputs)

    assert isinstance(report, str)
    assert "Missing Brand" in report
    assert "0 total mentions" in report


def test_build_executive_markdown_report_uses_compressed_appendix_structure():
    report = build_executive_markdown_report(**create_markdown_inputs())

    assert "## 8. GEO Content Roadmap" in report
    assert "## 9. 30 / 60 / 90 Day Roadmap" in report
    assert "## 10. Measurement Plan" in report
    assert "## 11. Recommended Next Step" in report
    assert "## 12. Methodology Notes" in report
    assert "## Appendix A: Brand Intelligence & Positioning Audit" in report
    assert "## Appendix B: AI Visibility Strategy Deep Dive" in report
    assert "## Appendix C: AI Decision Explanation" in report
    assert "## Appendix D: Replacement Strategy" in report
    assert "## Appendix E: Gap Analysis" in report
    assert "## 9. Appendix" not in report


def test_build_executive_markdown_report_applies_final_quality_gate():
    inputs = create_markdown_inputs()
    inputs["category"] = "skincare products"
    inputs["display_category"] = "Skincare Products"
    inputs["recommendations"] = "Strong clinical backing and product effectiveness."
    inputs["plan"] = "capture 10% share of voice. Aim for at least 5 mentions."
    inputs["brand_intelligence"] = {
        "recommendation_drivers": (
            "Top Competitor-Owned Associations (Source: AI-discovered market signal)s)\n\n"
            "AI-Discovered Brands Not Included in Scoring\n"
            "- Market Research"
        ),
        "target_brand_understanding": "clinical evidence",
        "positioning_gap_analysis": "Medical-Grade Efficacy",
    }
    inputs["geo_content_roadmap"] = (
        "| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| 1 | Trust | The Science Behind Espresso House: Professional Endorsements and Efficacy | Medical-Grade Efficacy | | Comparison table data showcasing ingredient efficacy | Intended benchmark influence: target-brand association | 30 Days |"
    )

    report = build_executive_markdown_report(**inputs)
    report_lower = report.lower()

    blocked_terms = [
        "clinical backing",
        "product effectiveness",
        "clinical evidence",
        "medical-grade efficacy",
        "ingredient efficacy",
        "capture 10% share of voice",
        "aim for at least 5 mentions",
        "top competitor-owned associations (source:",
        "market research",
    ]

    for term in blocked_terms:
        assert term not in report_lower

    assert "No additional non-tracked brands were identified." in report


def test_build_executive_markdown_report_removes_empty_secondary_market_signals_from_strategy():
    inputs = create_markdown_inputs()
    inputs["plan"] = """
## 10. Secondary Market Signals
No major secondary market signals detected.

---

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    report = build_executive_markdown_report(**inputs)

    assert "No major secondary market signals detected." not in report
    assert "Secondary Market Signals" not in report
    assert "Final Strategic Conclusion" in report


def test_build_executive_markdown_report_passes_tracked_competitors_to_final_gate():
    inputs = create_markdown_inputs()
    inputs["category"] = "skincare products"
    inputs["display_category"] = "Skincare Products"
    inputs["brand_intelligence"] = {
        "recommendation_drivers": (
            "| Advantage Signal | Evidence Source | Example Brands | Source Type |\n"
            "| --- | --- | --- | --- |\n"
            "| High-potency serums for rejuvenation | Benchmark answers | iS Clinical | AI-discovered market signals |\n\n"
            "AI-Discovered Brands Not Included in Scoring\n"
            "- **Influencer Engagement**: Collaborate with local influencers to amplify brand credibility."
        ),
        "target_brand_understanding": "Test target brand understanding",
        "positioning_gap_analysis": "Test positioning gap analysis",
    }

    report = build_executive_markdown_report(
        **inputs,
        tracked_competitors=["iS Clinical"],
    )
    issues = validate_output_quality(
        report,
        OutputQualityContext(
            category="Skincare Products",
            run_mode=inputs["run_mode"],
            brand=inputs["display_brand"],
            market=inputs["display_market"],
            audience=inputs["display_audience"],
            tracked_competitors=["iS Clinical"],
        ),
        content_type="final_markdown_report",
        strict=True,
    )

    assert "Influencer Engagement" not in report
    assert "iS Clinical | Tracked competitors" in report
    assert issues == []


def test_build_executive_markdown_report_guards_raw_llm_errors_in_quick_test():
    inputs = create_markdown_inputs()
    inputs["run_mode"] = "Quick Test Mode"
    inputs["prompt_limit"] = 1
    inputs["deliverable_status"] = "Not Client Deliverable"
    inputs["recommendations"] = "ERROR: Connection error."
    inputs["plan"] = "ERROR: Connection error."
    inputs["geo_content_roadmap"] = "ERROR: Connection error."
    inputs["brand_win_explanation"] = "ERROR: Connection error."
    inputs["replacement_strategy"] = "ERROR: Connection error."
    inputs["gap_analysis"] = "ERROR: Connection error."
    inputs["brand_intelligence"] = {
        "recommendation_drivers": "ERROR: Connection error.",
        "target_brand_understanding": "ERROR: Connection error.",
        "positioning_gap_analysis": "ERROR: Connection error.",
    }

    report = build_executive_markdown_report(**inputs)
    issues = validate_output_quality(
        report,
        OutputQualityContext(
            category=inputs["display_category"],
            run_mode=inputs["run_mode"],
            brand=inputs["display_brand"],
            market=inputs["display_market"],
            audience=inputs["display_audience"],
            tracked_competitors=["Coffee Fellows"],
        ),
        content_type="final_markdown_report",
        strict=True,
    )

    assert "ERROR:" not in report
    assert "Connection error" not in report
    assert FAILED_LLM_SECTION_PLACEHOLDER in report
    assert issues == []
