from output_quality import (
    OutputQualityContext,
    FORBIDDEN_CLAIM_PHRASES,
    sanitize_business_kpi_text,
    sanitize_ai_discovered_brands_section,
    sanitize_brand_intelligence_text,
    sanitize_competitor_advantage_table,
    sanitize_claim_safety_text,
    sanitize_geo_roadmap_text,
    sanitize_report_text,
    sanitize_snapshot_payload,
    sanitize_source_label_artifacts,
    sanitize_strategy_text,
    validate_output_quality,
)


def skincare_context(**overrides):
    context = OutputQualityContext(
        category="Skincare Products",
        run_mode="Quick Test Mode",
        brand="Dermaviduals",
        market="Hong Kong",
        audience="skincare-conscious consumers",
        tracked_competitors=["Environ"],
        target_brand_metrics={
            "total_mentions": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
    )
    for key, value in overrides.items():
        setattr(context, key, value)
    return context


def test_claim_safety_sanitizer_removes_forbidden_health_adjacent_claims():
    dirty = " ".join([
        "Clinical Study References",
        "clinical backing",
        "clinically proven",
        "clinical-grade",
        "medical-grade efficacy",
        "product efficacy",
        "showing efficacy",
        "ingredient efficacy",
        "product effectiveness",
        "validate product claims",
        "clinical collaboration",
        "clinical studies",
        "clinical evidence",
        "clinical data",
        "clinical validations",
        "efficacy claims",
        "proven results",
        "clinical trial",
        "clinical trials",
        "clinically backed",
    ])

    sanitized = sanitize_claim_safety_text(dirty, skincare_context())
    sanitized_lower = sanitized.lower()

    for phrase in FORBIDDEN_CLAIM_PHRASES:
        assert phrase.lower() not in sanitized_lower

    assert "claims support documentation" in sanitized_lower
    assert "expert validation" in sanitized_lower
    assert "evidence-supported positioning" in sanitized_lower
    assert "professional-grade" in sanitized_lower
    assert "product claims" in sanitized_lower
    assert "professional evidence review" in sanitized_lower


def test_ai_discovered_brands_section_keeps_only_non_tracked_brand_bullets():
    dirty = """
### AI-Discovered Brands Not Included in Scoring
- **Trend of Professional Skincare**: Rising popularity.
- **Competitive Analysis**: Evaluate pricing.
- **Evidence Building**: Gather reviews.
- **Dermalogica** - Focuses on customized skincare solutions.
- **Environ** - Tracked competitor that must be removed.
""".strip()

    sanitized = sanitize_ai_discovered_brands_section(dirty, skincare_context())

    assert "AI-Discovered Brands Not Included in Scoring" in sanitized
    assert "Dermalogica" in sanitized
    assert "Trend of Professional Skincare" not in sanitized
    assert "Competitive Analysis" not in sanitized
    assert "Evidence Building" not in sanitized
    assert "Environ" not in sanitized


def test_empty_ai_discovered_brands_section_gets_no_additional_brands_message():
    dirty = """
AI-Discovered Brands Not Included in Scoring
- Market Research
- Distribution Strategy
- Marketing Campaigns
""".strip()

    sanitized = sanitize_ai_discovered_brands_section(dirty, skincare_context())

    assert "No additional non-tracked brands were identified." in sanitized
    assert "Market Research" not in sanitized
    assert "Distribution Strategy" not in sanitized
    assert "Marketing Campaigns" not in sanitized


def test_source_label_artifact_cleanup_removes_malformed_suffixes():
    dirty = "Top Competitor-Owned Associations (Source: AI-discovered market signal)s)"

    sanitized = sanitize_source_label_artifacts(dirty)

    assert sanitized == "Top Competitor-Owned Associations"
    assert "(Source:" not in sanitized


def test_geo_roadmap_cleanup_removes_high_risk_title_and_evidence_wording():
    dirty = """
| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |
|---|---|---|---|---|---|---|---|
| 1 | Trust Signals | The Science Behind Dermaviduals: Professional Endorsements and Efficacy | Medical-Grade Efficacy | | Comparison table data showcasing ingredient efficacy | Intended benchmark influence: target-brand association | 30 Days |
""".strip()

    sanitized = sanitize_geo_roadmap_text(dirty, skincare_context())

    assert "The Science Behind Dermaviduals" not in sanitized
    assert "Medical-Grade Efficacy" not in sanitized
    assert "ingredient efficacy" not in sanitized.lower()
    assert "Dermaviduals Professional Trust Signals and Ingredient Documentation" in sanitized
    assert "Evidence-Supported Product Positioning" in sanitized
    assert "ingredient documentation and claims support" in sanitized


def test_quick_test_strategy_cleanup_removes_aggressive_targets():
    dirty = (
        "We should capture 10% share of voice and improve share of voice above 10%. "
        "Aim for at least 5 mentions. This should improve conversion rate and revenue."
    )

    sanitized = sanitize_strategy_text(dirty, skincare_context())
    sanitized_lower = sanitized.lower()

    assert "capture 10% share of voice" not in sanitized_lower
    assert "share of voice above 10%" not in sanitized_lower
    assert "aim for at least 5 mentions" not in sanitized_lower
    assert "conversion rate" not in sanitized_lower
    assert "revenue" not in sanitized_lower
    assert "measurable share of voice in a future full benchmark" in sanitized_lower
    assert "detectable mentions in a future full benchmark" in sanitized_lower


def test_final_report_sanitizer_and_validator_clear_dirty_markdown():
    dirty = """
## Appendix A: Brand Intelligence & Positioning Audit
Top Competitor-Owned Associations (Source: AI-discovered market signal)s)

AI-Discovered Brands Not Included in Scoring
- Market Research

Strong clinical backing and product effectiveness.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())
    issues = validate_output_quality(
        sanitized,
        skincare_context(),
        content_type="final_markdown_report",
    )

    assert issues == []
    assert "No additional non-tracked brands were identified." in sanitized
    assert "clinical backing" not in sanitized.lower()
    assert "product effectiveness" not in sanitized.lower()
    assert "(Source:" not in sanitized


def test_snapshot_payload_sanitizes_narrative_fields_only():
    snapshot = {
        "schema_version": "1.0",
        "summary_records": [{"brand": "Dermaviduals", "total_mentions": 0}],
        "detailed_records": [{"brand": "Dermaviduals", "visibility_score": 0}],
        "brand_intelligence": {
            "recommendation_drivers": "clinical backing",
            "target_brand_understanding": "product effectiveness",
            "positioning_gap_analysis": "Top Competitor-Owned Associations (Source: AI-discovered market signal)s)",
        },
    }

    sanitized = sanitize_snapshot_payload(snapshot, skincare_context())

    assert sanitized["schema_version"] == "1.0"
    assert sanitized["summary_records"] == snapshot["summary_records"]
    assert sanitized["detailed_records"] == snapshot["detailed_records"]
    assert "clinical backing" not in sanitized["brand_intelligence"]["recommendation_drivers"].lower()
    assert "product effectiveness" not in sanitized["brand_intelligence"]["target_brand_understanding"].lower()
    assert "(Source:" not in sanitized["brand_intelligence"]["positioning_gap_analysis"]


def test_brand_intelligence_sanitizer_enforces_table_schema_and_market_sections():
    dirty = """
| Advantage Signal | Source |
|---|---|
| Strong comparison proof with Environ | (Source: Tracked competitor) |
| Retail trust with Dermalogica | (Source: Tracked competitor) |

AI-Discovered Brands Not Included in Scoring
- Market Awareness
- **Dermalogica** - Retail trust.
""".strip()

    sanitized = sanitize_brand_intelligence_text(dirty, skincare_context())

    assert "| Advantage Signal | Evidence Source | Example Brands | Source Type |" in sanitized
    assert "Tracked competitors" in sanitized
    assert "AI-discovered market signals" in sanitized
    assert "Market Awareness" not in sanitized
    assert "Dermalogica" in sanitized


def test_ai_discovered_brands_rejects_action_items_from_latest_output():
    dirty = """
### AI-Discovered Brands Not Included in Scoring
- **Partnerships**: Establish relationships with local dermatologists for endorsements and recommendations.
- **Consumer Engagement**: Implement a feedback system to gather insights and testimonials for credibility enhancement.
Market Trends / Demand Signals
No additional non-tracked market signals were identified.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())
    issues = validate_output_quality(sanitized, skincare_context())

    assert "Partnerships" not in sanitized
    assert "Consumer Engagement" not in sanitized
    assert "No additional non-tracked brands were identified." in sanitized
    assert issues == []


def test_competitor_advantage_table_reclassifies_tracked_example_brand():
    dirty = """
| Advantage Signal | Evidence Source | Example Brands | Source Type |
| --- | --- | --- | --- |
| High-potency serums for rejuvenation | Benchmark answers | iS Clinical | AI-discovered market signals |
""".strip()
    context = skincare_context(tracked_competitors=["iS Clinical", "Environ"])

    sanitized = sanitize_competitor_advantage_table(dirty, context)

    assert (
        "| High-potency serums for rejuvenation | Benchmark answers | iS Clinical | Tracked competitors |"
        in sanitized
    )
    assert "iS Clinical | AI-discovered market signals" not in sanitized


def test_strategy_conservative_target_malformed_replacement_cleanup():
    dirty = (
        "Target a detectable begin generating measurable share of voice in a future full benchmark. "
        "Aim for a begin generating measurable share of voice in a full benchmark. "
        "target begin generating measurable share of voice"
    )

    sanitized = sanitize_strategy_text(dirty, skincare_context())
    sanitized_lower = sanitized.lower()

    assert "Begin generating measurable share of voice in a future full benchmark." in sanitized
    assert "target a detectable begin generating" not in sanitized_lower
    assert "target begin generating" not in sanitized_lower
    assert "Aim for a begin generating" not in sanitized


def test_claim_safety_removes_malformed_compliant_clause():
    dirty = (
        "claims support documentation, where substantiated and compliant showing product claims. "
        "claims support documentation, where substantiated and compliant showing efficacy. "
        "claims support documentation, where substantiated and compliant product claims."
    )

    sanitized = sanitize_claim_safety_text(dirty, skincare_context())
    sanitized_lower = sanitized.lower()

    assert "claims support documentation, consumer feedback, or expert validation" in sanitized
    assert "where substantiated and compliant showing" not in sanitized_lower
    assert "where substantiated and compliant product claims" not in sanitized_lower


def test_final_markdown_quality_gate_catches_latest_dirty_patterns():
    dirty = """
## Appendix A: Brand Intelligence & Positioning Audit
AI-Discovered Brands Not Included in Scoring
- **Partnerships**: Establish relationships with local dermatologists for endorsements and recommendations.
- **Consumer Engagement**: Implement a feedback system to gather insights and testimonials for credibility enhancement.

| Advantage Signal | Evidence Source | Example Brands | Source Type |
| --- | --- | --- | --- |
| High-potency serums for rejuvenation | Benchmark answers | iS Clinical | AI-discovered market signals |

Target a detectable begin generating measurable share of voice in a future full benchmark.
claims support documentation, where substantiated and compliant showing product claims
""".strip()
    context = skincare_context(tracked_competitors=["iS Clinical", "Environ"])

    dirty_issues = validate_output_quality(
        dirty,
        context,
        content_type="final_markdown_report",
        strict=True,
    )
    sanitized = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(
        sanitized,
        context,
        content_type="final_markdown_report",
        strict=True,
    )

    assert dirty_issues
    assert clean_issues == []
    assert "Partnerships" not in sanitized
    assert "Consumer Engagement" not in sanitized
    assert "iS Clinical | Tracked competitors" in sanitized
    assert "target a detectable begin" not in sanitized.lower()
    assert "where substantiated and compliant showing" not in sanitized.lower()


def test_docx_like_text_quality_gate_uses_same_validator():
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Partnerships**: Establish relationships with local dermatologists for endorsements and recommendations.
- **Consumer Engagement**: Implement a feedback system to gather insights and testimonials for credibility enhancement.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())
    issues = validate_output_quality(
        sanitized,
        skincare_context(),
        content_type="docx_text",
        strict=True,
    )

    assert "Partnerships" not in sanitized
    assert "Consumer Engagement" not in sanitized
    assert "No additional non-tracked brands were identified." in sanitized
    assert issues == []


def test_ai_discovered_brands_rejects_influencer_engagement():
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Influencer Engagement**: Collaborate with local influencers to amplify brand credibility.
Market Trends / Demand Signals
No additional non-tracked market signals were identified.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())
    issues = validate_output_quality(sanitized, skincare_context(), strict=True)

    assert "Influencer Engagement" not in sanitized
    assert "No additional non-tracked brands were identified." in sanitized
    assert issues == []


def test_duplicate_empty_placeholders_are_collapsed():
    dirty = """
AI-Discovered Brands Not Included in Scoring
No additional non-tracked brands were identified.
No additional non-tracked brands were identified.
No additional non-tracked brands were identified.

Market Trends / Demand Signals
No additional non-tracked market signals were identified.
No additional non-tracked market signals were identified.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())

    assert sanitized.count("No additional non-tracked brands were identified.") == 1
    assert sanitized.count("No additional non-tracked market signals were identified.") == 1


def test_geo_latest_high_risk_titles_are_sanitized():
    dirty = """
| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |
|---|---|---|---|---|---|---|---|
| 1 | Trust | Pollution Defense: How Dermaviduals Protects Your Skin | The Science Behind Dermaviduals for Skin Health | | Third-party reviews | Intended benchmark influence: target-brand association | 30 Days |
""".strip()

    sanitized = sanitize_geo_roadmap_text(dirty, skincare_context())

    assert "Protects Your Skin" not in sanitized
    assert "The Science Behind Dermaviduals for Skin Health" not in sanitized
    assert "Dermaviduals Ingredient Guide for Pollution-Exposed Skin" in sanitized
    assert "Dermaviduals Professional Trust Signals and Ingredient Documentation" in sanitized


def test_validate_catches_latest_dirty_patterns_before_sanitize():
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Influencer Engagement**: Collaborate with local influencers to amplify brand credibility.

| Priority | Query Intent | Content Asset | Target Association |
|---|---|---|---|
| 1 | Trust | Pollution Defense: How Dermaviduals Protects Your Skin | The Science Behind Dermaviduals for Skin Health |
""".strip()

    dirty_issues = validate_output_quality(dirty, skincare_context(), strict=True)
    sanitized = sanitize_report_text(dirty, skincare_context())
    clean_issues = validate_output_quality(sanitized, skincare_context(), strict=True)

    assert dirty_issues
    assert clean_issues == []
    assert "Influencer Engagement" not in sanitized
    assert "Protects Your Skin" not in sanitized
    assert "The Science Behind Dermaviduals for Skin Health" not in sanitized

from output_quality import (
    OutputQualityContext,
    sanitize_report_text,
    validate_output_quality,
)


def test_ai_discovered_brands_rejects_action_items_before_and_after_sanitize():
    context = OutputQualityContext(
        category="skincare",
        run_mode="Quick Test Mode",
        tracked_competitors=["La Roche-Posay", "CeraVe"],
    )

    dirty = """
AI-Discovered Brands Not Included in Scoring

- **Consumer Education** – Build awareness around skincare routines.
- **Collect Testimonials** – Gather consumer proof.
- **Validation Efforts** – Support future claims.
- **User Feedback Collection** – Collect reviews.
- **User-Generated Content** – Encourage customer posts.
"""

    dirty_issues = validate_output_quality(dirty, context)
    assert dirty_issues

    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert "No additional non-tracked brands were identified." in clean
    assert "Consumer Education" not in clean
    assert "Collect Testimonials" not in clean
    assert "Validation Efforts" not in clean
    assert "User Feedback Collection" not in clean
    assert "User-Generated Content" not in clean
    assert clean_issues == []


def test_quick_test_numeric_targets_fail_then_sanitize_to_directional_language():
    context = OutputQualityContext(
        category="skincare",
        run_mode="Quick Test Mode",
    )

    dirty = """
Recommendations:
- Reach 10% share of voice.
- The goal of achieving at least 10% share of voice is realistic.
- Increase average visibility score to above 10.
- Improve visibility score above 20%.
- Aim for at least 1-3 mentions.
"""

    dirty_issues = validate_output_quality(dirty, context)
    assert dirty_issues

    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert "Reach 10% share of voice" not in clean
    assert "at least 10% share of voice" not in clean
    assert "above 10" not in clean
    assert "above 20" not in clean
    assert "1-3 mentions" not in clean

    assert "Begin generating measurable share of voice in a future full benchmark." in clean
    assert "Begin improving average visibility score in a future full benchmark." in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert clean_issues == []


def test_malformed_claim_sentences_fail_then_sanitize_cleanly():
    context = OutputQualityContext(
        category="skincare",
        run_mode="Quick Test Mode",
    )

    dirty = """
Evidence of Effectiveness

- business outcomes Performance Metrics
- Research studies or claims support documentation, where substantiated and compliant supporting product claims.
- Publishing results from claims support documentation, where substantiated and compliant can substantiate product claims.
- claims support documentation, where substantiated and compliant Data
"""

    dirty_issues = validate_output_quality(dirty, context)
    assert dirty_issues

    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert "business outcomes Performance Metrics" not in clean
    assert "Evidence of Effectiveness" not in clean
    assert "where substantiated and compliant supporting product claims" not in clean
    assert "Publishing results from claims support documentation" not in clean
    assert "claims support documentation, where substantiated and compliant Data" not in clean

    assert "market performance indicators" in clean
    assert "Evidence Support" in clean
    assert "Claims support documentation, consumer feedback, or expert validation." in clean
    assert clean_issues == []