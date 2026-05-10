import pytest

from geo_audit.output_quality import (
    FAILED_LLM_SECTION_PLACEHOLDER,
    OutputQualityContext,
    FORBIDDEN_CLAIM_PHRASES,
    guard_generated_section_text,
    is_raw_error_output,
    normalize_appendix_language_text,
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


def test_normalize_appendix_language_weakens_certainty_phrases_and_keeps_context():
    dirty = (
        "Dermaviduals must improve because of lack of awareness. "
        "It must enhance evidence, must create comparison content, must build trust, "
        "must position carefully, and needs to establish stronger support. "
        "Environ has established authority, is a leading brand, and is recognized locally. "
        "The diagnostic content should remain."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "must improve",
        "must enhance",
        "must create",
        "must build",
        "must position",
        "needs to establish",
        "lack of awareness",
        "established authority",
        "leading brand",
        "recognized locally",
    ]:
        assert phrase not in clean_lower

    assert "Dermaviduals" in clean
    assert "Environ" in clean
    assert "should improve" in clean
    assert "should strengthen evidence" in clean
    assert "should create comparison content" in clean
    assert "should build trust" in clean
    assert "should position carefully" in clean
    assert "should build evidence for stronger support" in clean
    assert "limited measurable visibility in this benchmark" in clean
    assert "stronger authority signals within the tested prompt set" in clean
    assert "brand with stronger measured visibility" in clean
    assert "visible in local benchmark signals" in clean
    assert "The diagnostic content should remain." in clean


def test_normalize_appendix_language_normalizes_headings_and_preserves_brand_names():
    dirty = (
        "Why AI Does Not Recommend Dermaviduals:\n"
        "AI-owned territory: Environ.\n"
        "Current territory owned: clinic trust.\n"
        "Owned territory: local recommendations."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "why ai does not recommend",
        "ai-owned territory",
        "current territory owned",
        "owned territory",
    ]:
        assert phrase not in clean_lower

    assert "Dermaviduals" in clean
    assert "Environ" in clean
    assert "Benchmark-Visible Associations Missing or Weak for Dermaviduals" in clean
    assert "observed query territory signal" in clean
    assert "Current observed query territory" in clean
    assert "Observed query territory" in clean


def test_normalize_appendix_language_normalizes_market_dominance_language():
    dirty = (
        "Environ is a dominant brand. Dominant brands are dominating the market. "
        "This dominance appears in the appendix."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "dominant brand",
        "dominant brands",
        "dominating the market",
        "dominance",
    ]:
        assert phrase not in clean_lower

    assert "Environ" in clean
    assert "brand with stronger measured visibility" in clean
    assert "brands with stronger measured visibility" in clean
    assert "showing stronger measured visibility in this benchmark" in clean
    assert "stronger measured visibility appears" in clean


def test_normalize_appendix_language_normalizes_ai_agency_language():
    dirty = (
        "AI algorithms analyzing consumer intent say Dermaviduals is missing. "
        "AI recommends Environ, AI does not recommend Dermaviduals, "
        "AI trusts Environ, and AI knows the category."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "ai algorithms analyzing consumer intent",
        "ai recommends",
        "ai does not recommend",
        "ai trusts",
        "ai knows",
    ]:
        assert phrase not in clean_lower

    assert "Dermaviduals" in clean
    assert "Environ" in clean
    assert "generated answers in this benchmark" in clean
    assert "generated answers mention Environ" in clean
    assert "generated answers do not mention Dermaviduals" in clean
    assert "generated answers show trust-related signals for Environ" in clean
    assert "generated answers suggest the category" in clean


def test_normalize_appendix_language_reduces_market_fact_language():
    dirty = (
        "The brand has market presence in the local recommendation market. "
        "The competitive landscape suggests market reach and market penetration."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "market presence",
        "local recommendation market",
        "competitive landscape",
        "market reach",
        "market penetration",
    ]:
        assert phrase not in clean_lower

    assert "measured visibility footprint" in clean
    assert "local recommendation query context" in clean
    assert "tested competitive context" in clean
    assert "benchmark-visible reach" in clean
    assert "measured market visibility signal" in clean


def test_normalize_appendix_language_reduces_consumer_behavior_claims():
    dirty = (
        "Consumers are likely ready to purchase. "
        "Consumer preference and consumer trust are capturing attention, "
        "which could capture consumer interest. "
        "Dermaviduals is a trusted brand among skincare-conscious consumers and a preferred choice. "
        "Consumer awareness, brand awareness, purchase decisions, consumer intent, and market trust appear."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "consumers are likely ready to purchase",
        "consumer preference",
        "consumer trust",
        "capturing attention",
        "capture consumer interest",
        "trusted brand among skincare-conscious consumers",
        "preferred choice",
        "consumer awareness",
        "brand awareness",
        "purchase decisions",
        "consumer intent",
        "market trust",
    ]:
        assert phrase not in clean_lower

    assert "Dermaviduals" in clean
    assert "tested prompts may reflect decision-stage intent" in clean
    assert "preference-related signal in generated answers" in clean
    assert "trust-related signals in generated answers" in clean
    assert "appearing in measured benchmark signals" in clean
    assert "support future consideration signals" in clean
    assert "brand with stronger trust-related signals in generated answers" in clean
    assert "more visible option in this benchmark" in clean
    assert "audience-awareness signal" in clean
    assert "brand visibility signal" in clean
    assert "decision-stage query context" in clean
    assert "query intent" in clean
    assert "trust-related market signal" in clean


def test_normalize_appendix_language_weakens_recommendation_outcomes():
    dirty = (
        "The plan can gain traction and establish presence. "
        "It should improve relevance and enhance credibility. "
        "The content will improve visibility, will increase share of voice, "
        "will drive revenue, and will increase sales."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "gain traction",
        "establish presence",
        "improve relevance",
        "enhance credibility",
        "will improve visibility",
        "will increase share of voice",
        "will drive revenue",
        "will increase sales",
    ]:
        assert phrase not in clean_lower

    assert "build measurable visibility" in clean
    assert "build measurable presence in future benchmarks" in clean
    assert "support future benchmark relevance" in clean
    assert "support clearer credibility signals" in clean
    assert "is intended to support future measured visibility" in clean
    assert "is intended to support future share-of-voice improvement" in clean
    assert clean.count("is not evaluated by this benchmark") == 2


def test_normalize_appendix_language_normalizes_label_artifacts_only_in_labels():
    dirty = """
**measured visibility footprint**: Evidence stays.
- audience-awareness signal in generated answers: Diagnostic note.
### measured market visibility signal
| brand visibility signal | Detail |
|---|---|
This sentence mentions measured visibility footprint as body text.
""".strip()

    clean = normalize_appendix_language_text(dirty, skincare_context())

    assert "**Market Visibility**: Evidence stays." in clean
    assert "- Audience Awareness Signal: Diagnostic note." in clean
    assert "### Market Visibility Signal" in clean
    assert "| Brand Visibility Signal | Detail |" in clean
    assert "This sentence mentions measured visibility footprint as body text." in clean


def test_normalize_appendix_language_preserves_brand_when_normalizing_dominates():
    dirty = (
        "iS Clinical dominates with higher mention patterns. "
        "Coffee Fellows dominates the market. "
        "Environ dominates. "
        "SkinCeuticals dominates the AI-generated recommendations."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    assert "dominates" not in clean_lower
    assert "iS Clinical shows stronger measured visibility with higher mention patterns" in clean
    assert "Coffee Fellows shows stronger measured visibility in this benchmark" in clean
    assert "Environ shows stronger measured visibility" in clean
    assert "SkinCeuticals shows stronger measured visibility within the tested prompt set" in clean
    assert "shows stronger measured visibility the AI-generated recommendations" not in clean


def test_normalize_appendix_language_cleans_phase_2c_certainty_and_consumer_phrases():
    dirty = (
        "There is an urgent need and crucial next step. "
        "Consumers are actively seeking proof, trust among consumers, consumer confidence, "
        "decision-making in this market, consumer recognition, and consumer perception."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "urgent need",
        "crucial",
        "consumers are actively seeking",
        "trust among consumers",
        "consumer confidence",
        "decision-making in this market",
        "consumer recognition",
        "consumer perception",
    ]:
        assert phrase not in clean_lower

    assert "priority need" in clean
    assert "important next step" in clean
    assert "tested prompts reflect demand for proof" in clean
    assert "trust-related signals in generated answers" in clean
    assert "trust-related confidence signal" in clean
    assert "decision-stage query context" in clean
    assert "audience-recognition signal" in clean
    assert "audience-perception signal" in clean


def test_normalize_appendix_language_cleans_sanitizer_artifacts():
    dirty = (
        "High-product claims skincare requires Evidence Support. "
        "Product claims of Products should use claims support documentation, where substantiated and compliant. "
        "Strong evidence-supported positioning and Dermatologist-Recommendation language appeared."
    )

    clean = normalize_appendix_language_text(dirty, skincare_context())
    clean_lower = clean.lower()

    for phrase in [
        "high-product claims skincare",
        "evidence support",
        "product claims of products",
        "claims support documentation, where substantiated and compliant",
        "Dermatologist-Recommendation",
    ]:
        assert phrase.lower() not in clean_lower

    assert "Strong evidence-supported positioning" not in clean
    assert "high-evidence skincare positioning" in clean
    assert "supporting evidence" in clean
    assert "product claims" in clean
    assert "claims support documentation where appropriate" in clean
    assert "strong evidence-supported positioning" in clean
    assert "dermatologist recommendations" in clean


def test_report_artifact_cleanup_fixes_broken_metric_target_composition():
    dirty = (
        "Target a score Begin improving average visibility score in the next benchmark. "
        "The metric label said score Begin improving prompt-level visibility."
    )

    clean = sanitize_strategy_text(dirty, skincare_context(category="cafes"))

    assert "Target a score Begin" not in clean
    assert "score Begin improving" not in clean
    assert "Begin improving average visibility score" in clean
    assert "Begin improving prompt-level visibility" in clean


def test_report_artifact_cleanup_fixes_measured_visibility_grammar():
    dirty = (
        "Brand A shows stronger measured visibility queries. "
        "Brand B shows stronger measured visibility the AI-generated recommendations. "
        "Brand C shows stronger measured visibility in the AI-generated recommendations."
    )

    clean = sanitize_strategy_text(dirty, skincare_context(category="cafes"))

    assert "shows stronger measured visibility queries" not in clean
    assert "shows stronger measured visibility the AI-generated recommendations" not in clean
    assert "shows stronger measured visibility in the AI-generated recommendations" not in clean
    assert "Brand A shows stronger measured visibility for relevant queries" in clean
    assert clean.count("shows stronger measured visibility within the tested prompt set") == 2


def test_report_artifact_cleanup_deduplicates_product_claims_without_overreach():
    dirty = (
        "Use product claims and product claims carefully. "
        "Use supporting product claims and product claims carefully. "
        "Use claims support documentation where appropriate and claims support documentation. "
        "Claims support documentation and expert validation should remain."
    )

    clean = sanitize_report_text(dirty, skincare_context())

    assert "product claims and product claims" not in clean
    assert "supporting product claims and product claims" not in clean
    assert "claims support documentation where appropriate and claims support documentation" not in clean
    assert "Use product claims carefully" in clean
    assert "Use supporting product claims carefully" in clean
    assert "claims support documentation where appropriate" in clean
    assert "Claims support documentation and expert validation should remain." in clean


def test_report_artifact_cleanup_removes_repeated_professional_grade_adjectives():
    dirty = (
        "The report says professional, professional-grade support. "
        "It also says professional professional-grade positioning."
    )

    clean = sanitize_report_text(dirty, skincare_context(category="cafes"))

    assert "professional, professional-grade" not in clean
    assert "professional professional-grade" not in clean
    assert "professional-grade support" in clean
    assert "professional-grade positioning" in clean


def test_report_artifact_cleanup_fixes_capitalization_and_bold_claims_label():
    dirty = (
        "Professional-Grade product claims and Evidence-Based product claims appear. "
        "**claims support documentation where appropriate**: keep the explanation. "
        "claims support documentation where appropriate remains normal body text."
    )

    clean = sanitize_report_text(dirty, skincare_context(category="cafes"))

    assert "Professional-Grade product claims" not in clean
    assert "Evidence-Based product claims" not in clean
    assert "professional-grade product claims" in clean
    assert "evidence-based product claims" in clean
    assert "**Claims Support Documentation**: keep the explanation." in clean
    assert "claims support documentation where appropriate remains normal body text." in clean


def test_normalize_appendix_language_returns_empty_or_non_string_unchanged():
    assert normalize_appendix_language_text("") == ""
    assert normalize_appendix_language_text(None) is None
    assert normalize_appendix_language_text({"text": "must improve"}) == {"text": "must improve"}


def test_generated_section_sanitizers_apply_appendix_language_normalization():
    context = skincare_context(category="cafes")
    dirty = "Dermaviduals must improve market presence and gain traction."

    strategy = sanitize_strategy_text(dirty, context)
    brand_intelligence = sanitize_brand_intelligence_text(dirty, context)
    geo_roadmap = sanitize_geo_roadmap_text(dirty, context)

    for clean in [strategy, brand_intelligence, geo_roadmap]:
        assert "Dermaviduals" in clean
        assert "must improve" not in clean.lower()
        assert "market presence" not in clean.lower()
        assert "gain traction" not in clean.lower()
        assert "should improve" in clean
        assert "measured visibility footprint" in clean
        assert "build measurable visibility" in clean


def test_report_sanitizer_does_not_broadly_rewrite_methodology_language():
    dirty = (
        "Methodology Notes: This AI visibility benchmark reviews market context, "
        "consumer prompts, trust signals, and authority signals. "
        "It does not measure market share or clinical evaluation."
    )

    clean = sanitize_report_text(dirty, skincare_context(category="cafes"))

    assert "market context" in clean
    assert "consumer prompts" in clean
    assert "trust signals" in clean
    assert "authority signals" in clean
    assert "market share" in clean
    assert "clinical evaluation" in clean


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


def test_raw_error_output_is_detected_and_not_silently_sanitized():
    dirty = "ERROR: Connection error."
    context = skincare_context()

    assert is_raw_error_output(dirty)

    dirty_issues = validate_output_quality(dirty, context)
    assert any(issue.code == "raw_error_output" for issue in dirty_issues)

    sanitized = sanitize_report_text(dirty, context)
    assert is_raw_error_output(sanitized)

    sanitized_issues = validate_output_quality(sanitized, context)
    assert any(issue.code == "raw_error_output" for issue in sanitized_issues)


def test_generated_section_guard_uses_placeholder_for_quick_test_raw_errors():
    guarded = guard_generated_section_text(
        "ERROR: Connection error.",
        skincare_context(run_mode="Quick Test Mode"),
        "GEO Content Roadmap",
    )

    assert guarded == FAILED_LLM_SECTION_PLACEHOLDER
    assert "ERROR:" not in guarded
    assert "Connection error" not in guarded


def test_generated_section_guard_blocks_full_report_raw_errors():
    with pytest.raises(ValueError, match="LLM request failed"):
        guard_generated_section_text(
            "ERROR: Connection error.",
            skincare_context(run_mode="Full Report Mode"),
            "AI Visibility Strategy Deep Dive",
        )


def test_strategy_sanitizer_removes_empty_secondary_market_signals_section():
    dirty = """
## 9. 30 / 60 / 90 Day Execution Roadmap
Build the highest-priority assets.

## 10. Secondary Market Signals
No major secondary market signals detected.

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    sanitized = sanitize_strategy_text(dirty, skincare_context())

    assert "Secondary Market Signals" not in sanitized
    assert "No major secondary market signals detected." not in sanitized
    assert "30 / 60 / 90 Day Execution Roadmap" in sanitized
    assert "Final Strategic Conclusion" in sanitized


def test_strategy_sanitizer_removes_empty_secondary_market_signals_with_rule_separator():
    dirty = """
## 10. Secondary Market Signals
No major secondary market signals detected.

---

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    sanitized = sanitize_strategy_text(dirty, skincare_context())

    assert "Secondary Market Signals" not in sanitized
    assert "No major secondary market signals detected." not in sanitized
    assert "---" not in sanitized
    assert "Final Strategic Conclusion" in sanitized


def test_strategy_sanitizer_keeps_substantive_secondary_market_signals_section():
    dirty = """
## 10. Secondary Market Signals
- Rising demand for remote-work-friendly cafes.

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    sanitized = sanitize_strategy_text(dirty, skincare_context())

    assert "Secondary Market Signals" in sanitized
    assert "Rising demand for remote-work-friendly cafes." in sanitized


def test_final_report_removes_empty_secondary_market_signals_from_appendix():
    dirty = """
## Appendix B: AI Visibility Strategy Deep Dive

## 10. Secondary Market Signals
No major secondary market signals detected.

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())

    assert "No major secondary market signals detected." not in sanitized
    assert "Secondary Market Signals" not in sanitized
    assert "Final Strategic Conclusion" in sanitized

def test_final_report_removes_empty_secondary_market_signals_from_appendix():
    dirty = """
## Appendix B: AI Visibility Strategy Deep Dive

## 10. Secondary Market Signals
No major secondary market signals detected.

## 11. Final Strategic Conclusion
Focus on the primary visibility gap.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())

    assert "No major secondary market signals detected." not in sanitized
    assert "Secondary Market Signals" not in sanitized
    assert "Final Strategic Conclusion" in sanitized

def test_claim_safety_cleans_final_health_wording_artifacts():
    dirty = """
1. **Professional, professional-grade Formulations** – Emphasis on brands that offer medical or professionally recommended products.
4. **Reputation and Trust** – Preference for brands recognized for their quality and Evidence Support among dermatologists and skincare professionals.
The brand established a clear benchmark for Evidence Support.
""".strip()

    clean = sanitize_report_text(dirty, skincare_context())

    assert "Professional, professional-grade Formulations" not in clean
    assert "medical or professionally recommended products" not in clean
    assert "quality and Evidence Support" not in clean
    assert "benchmark for Evidence Support" not in clean

    assert "Professional Skincare Formulations" in clean
    assert "professionally recommended skincare products" in clean
    assert "quality, supporting evidence, and professional trust signals" in clean
    assert "clear evidence benchmark" in clean


def test_empty_secondary_market_signals_removal_renumbers_final_conclusion():
    dirty = """
## 9. 30 / 60 / 90 Day Execution Roadmap

Content here.

---

## 10. Secondary Market Signals

No major secondary market signals detected.

---

## 11. Final Strategic Conclusion

Final content here.
""".strip()

    clean = sanitize_report_text(dirty, skincare_context())

    assert "Secondary Market Signals" not in clean
    assert "No major secondary market signals detected" not in clean
    assert "## 11. Final Strategic Conclusion" not in clean
    assert "## 10. Final Strategic Conclusion" in clean

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


def test_source_label_artifact_cleanup_removes_orphan_trailing_asterisks():
    dirty = (
        "Starbucks (Source: Mixed tracked competitor / AI-discovered market signal)*\n"
        "The Barn *(Source: Tracked competitor)*\n"
        "Silo Coffee (Source: AI-discovered market signal)*"
    )

    sanitized = sanitize_source_label_artifacts(dirty)

    assert "(Source: Mixed tracked competitor / AI-discovered market signal)*" not in sanitized
    assert "*(Source: Tracked competitor)*" not in sanitized
    assert "(Source: AI-discovered market signal)*" not in sanitized
    assert "(Source: Mixed tracked competitor / AI-discovered market signal)" in sanitized
    assert "(Source: Tracked competitor)" in sanitized
    assert "(Source: AI-discovered market signal)" in sanitized


def test_source_label_artifact_cleanup_removes_duplicate_labels():
    dirty = (
        "iS Clinical (Tracked competitors) (Tracked competitor)\n"
        "The Barn (Tracked competitor) (Tracked competitor)\n"
        "Silo Coffee (AI-discovered market signal) (AI-discovered market signal)"
    )

    sanitized = sanitize_source_label_artifacts(dirty)

    assert "(Tracked competitors) (Tracked competitor)" not in sanitized
    assert "(Tracked competitor) (Tracked competitor)" not in sanitized
    assert "(AI-discovered market signal) (AI-discovered market signal)" not in sanitized
    assert "iS Clinical (Tracked competitors)" in sanitized
    assert "The Barn (Tracked competitor)" in sanitized
    assert "Silo Coffee (AI-discovered market signal)" in sanitized


def test_business_kpi_cleanup_uses_business_performance_outcomes_wording():
    dirty = "The report should not imply revenue or sales movement."

    sanitized = sanitize_business_kpi_text(dirty, skincare_context())

    assert "business performance outcomes" in sanitized
    assert "business outcome" not in sanitized.replace("business performance outcomes", "")


def test_report_sanitizer_cleans_final_polish_artifacts():
    dirty = """
This is not a business performance outcomes performance report.
Assess business performance outcomes performance relative to competitors.
Avoid business performance outcomes performance claims.
Create ingredient Evidence Support.
High Evidence Support is needed.
high Evidence Support should be clearer.
Clinical product claims should be avoided.
clinical product claims should be avoided.
Improve product claims and simplicity.
Evidence Support through user experiences matters.
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())

    blocked = [
        "business performance outcomes performance report",
        "business performance outcomes performance relative to competitors",
        "business performance outcomes performance",
        "ingredient Evidence Support",
        "High Evidence Support",
        "high Evidence Support",
        "Clinical product claims",
        "clinical product claims",
        "product claims and simplicity",
        "Evidence Support through user experiences",
    ]

    for phrase in blocked:
        assert phrase not in sanitized

    expected = [
        "business performance report",
        "business performance relative to competitors",
        "business performance claims",
        "ingredient documentation and supporting evidence",
        "Strong supporting evidence",
        "strong supporting evidence",
        "Claims support documentation",
        "claims support documentation",
        "claims support documentation and simplicity",
        "supporting evidence through user experiences",
    ]

    for phrase in expected:
        assert phrase in sanitized


def test_report_sanitizer_cleans_final_blocking_health_artifacts():
    dirty = """
product claims of Active Ingredients
evidence-supported positioning and Testing
tested for Evidence Support
Clinical testing and results-driven
Evidence Support for local concerns
""".strip()

    sanitized = sanitize_report_text(dirty, skincare_context())

    blocked = [
        "product claims of Active Ingredients",
        "evidence-supported positioning and Testing",
        "tested for Evidence Support",
        "Clinical testing and results-driven",
        "Evidence Support for local concerns",
    ]

    for phrase in blocked:
        assert phrase not in sanitized

    expected = [
        "Claims support documentation for active ingredients",
        "Evidence-supported positioning and testing",
        "supported by evidence documentation",
        "Evidence documentation and outcomes-oriented",
        "evidence documentation for local concerns",
    ]

    for phrase in expected:
        assert phrase in sanitized


def test_validator_catches_final_polish_artifacts_when_unsanitized():
    dirty = """
business performance outcomes performance
Clinical product claims
ingredient Evidence Support
""".strip()

    issues = validate_output_quality(dirty, skincare_context(), strict=True)
    phrases = {issue.phrase for issue in issues}

    assert "business performance outcomes performance" in phrases
    assert "Clinical product claims" in phrases
    assert "ingredient Evidence Support" in phrases


def test_final_polish_cleanup_preserves_current_state_metrics():
    dirty = (
        "Espresso House is currently not visible across the tested AI search prompts, "
        "with 0 total mentions, 0.0 average visibility, 0 prompts visible, and 0% share of voice."
    )

    sanitized = sanitize_report_text(
        dirty,
        skincare_context(
            category="Cafes",
            brand="Espresso House",
            market="Berlin",
            audience="Remote Workers",
        ),
    )

    assert sanitized == dirty


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

from geo_audit.output_quality import (
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
    assert "supporting evidence" in clean
    assert "Claims support documentation, consumer feedback, or expert validation." in clean
    assert clean_issues == []


def test_ai_discovered_brands_rejects_monitor_competitors_action_item():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=["The Barn"],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Monitor Competitors**: Analyze competitor strategies to identify gaps in Espresso House's offerings.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Monitor Competitors" not in clean
    assert "No additional non-tracked brands were identified." in clean
    assert clean_issues == []


def test_quick_test_latest_malformed_targets_sanitize_to_directional_language():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
visibility in 1-3 relevant prompt categories
a begin generating measurable share of voice in a future full benchmark
Gain initial mentions and recognition among target queries
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "visibility in 1-3 relevant prompt categories" not in clean
    assert "a begin generating measurable share of voice" not in clean
    assert "Gain initial mentions" not in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories" in clean
    assert "begin generating measurable share of voice in a future full benchmark" in clean
    assert "Begin generating detectable mentions in relevant target queries" in clean
    assert clean_issues == []


def test_ai_discovered_brands_rejects_brand_positioning_action_item():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=["The Barn"],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
3. **Brand Positioning**: Enhance marketing strategies to highlight features appealing to remote workers, such as seating and Wi-Fi availability.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Brand Positioning" not in clean
    assert "Enhance marketing strategies" not in clean
    assert "No additional non-tracked brands were identified." in clean
    assert clean_issues == []


def test_quick_test_parenthetical_numeric_targets_sanitize_to_directional_language():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = (
        "Target a benchmark of 10% share of voice in the remote work cafe category.\n"
        "Total mentions (aim to reach at least 5), average visibility score (target 1.0), "
        "and share of voice (aim for 5%)."
    )

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Target a benchmark of 10% share of voice" not in clean
    assert "aim to reach at least 5" not in clean
    assert "target 1.0" not in clean
    assert "aim for 5%" not in clean
    assert "Begin generating measurable share of voice in a future full benchmark." in clean
    assert "begin generating detectable mentions in a future full benchmark" in clean
    assert "begin improving average visibility score in a future full benchmark" in clean
    assert clean_issues == []


def test_ai_discovered_brands_extracts_embedded_brands_from_wrapper_line():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=[],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Additional Brands**: Consider adding brands like **Vits der Kaffee**, **The Barn**, or **Silo Coffee** for strategic relevance in the market.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Additional Brands" not in clean
    assert "- **Vits der Kaffee**" in clean
    assert "- **The Barn**" in clean
    assert "- **Silo Coffee**" in clean
    assert clean_issues == []


def test_quick_test_initial_visibility_artifacts_sanitize_to_directional_language():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = (
        "Increase Begin generating prompt-level visibility in relevant prompt categories. "
        "Achieve initial visibility in at least 1-3 relevant prompt categories."
    )

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Increase Begin generating" not in clean
    assert "Achieve initial visibility" not in clean
    assert "initial visibility in at least 1-3" not in clean
    assert clean.count("Begin generating prompt-level visibility in relevant prompt categories") >= 1
    assert clean_issues == []


def test_quick_test_zero_baseline_numeric_targets_sanitize_to_directional_language():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
Increase mentions from 0 to 1-3.
Move from 0.0 visibility to 0.1 or more.
Establish presence in 1-2 relevant prompt categories.
Total mentions, average visibility score, and prompts visible should each aim to increase from 0 to at least 1-3.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Increase mentions from 0 to 1-3" not in clean
    assert "Move from 0.0 visibility to 0.1 or more" not in clean
    assert "Establish presence in 1-2 relevant prompt categories" not in clean
    assert "should each aim to increase from 0 to at least 1-3" not in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert "Begin improving average visibility score in a future full benchmark." in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories." in clean
    assert (
        "Total mentions, average visibility score, and prompts visible should improve directionally in a future full benchmark."
        in clean
    )
    assert clean_issues == []


def test_ai_discovered_brands_rejects_highlight_amenities_action_item():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=["The Barn"],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Highlight Amenities**: Clearly communicate Wi-Fi quality and work-friendly features in marketing materials.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Highlight Amenities" not in clean
    assert "communicate Wi-Fi quality" not in clean
    assert "No additional non-tracked brands were identified." in clean
    assert clean_issues == []


def test_quick_test_latest_visibility_and_mentions_targets_sanitize_directionally():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
Achieve visibility in at least 1-2 relevant prompt categories.
Gain visibility in 2-3 prompt categories.
Generate 5-10 mentions from trusted sources.
Establish a recognizable presence in local searches and begin to capture share of voice.
aiming for begin generating detectable mentions in a future full benchmark
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Achieve visibility in at least 1-2 relevant prompt categories" not in clean
    assert "Gain visibility in 2-3 prompt categories" not in clean
    assert "Generate 5-10 mentions" not in clean
    assert "Establish a recognizable presence" not in clean
    assert "aiming for begin generating" not in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories." in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert "Begin generating measurable share of voice in a future full benchmark." in clean
    assert clean_issues == []


def test_ai_discovered_brands_strictly_rejects_action_task_labels():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=[],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Benchmark Against Competitors**: Consider adding non-tracked brands relevant to remote working to gain deeper insights and competitive advantages.
- **Highlight Amenities**: Clearly communicate Wi-Fi quality and work-friendly features in marketing materials.
- **Brand Positioning**: Enhance marketing strategies to highlight features.
- **Monitor Competitors**: Analyze competitor strategies.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Benchmark Against Competitors" not in clean
    assert "Highlight Amenities" not in clean
    assert "Brand Positioning" not in clean
    assert "Monitor Competitors" not in clean
    assert "No additional non-tracked brands were identified." in clean
    assert clean_issues == []


def test_ai_discovered_brands_strict_wrapper_extraction_preserves_embedded_brands():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
        tracked_competitors=[],
    )
    dirty = """
AI-Discovered Brands Not Included in Scoring
- **Additional Brands**: Consider adding brands like **Vits der Kaffee**, **The Barn**, or **Silo Coffee** for strategic relevance.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert "Additional Brands" not in clean
    assert "- **Vits der Kaffee**" in clean
    assert "- **The Barn**" in clean
    assert "- **Silo Coffee**" in clean
    assert clean_issues == []


def test_quick_test_sentence_level_numeric_targets_sanitize_directionally():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
Achieve visibility in at least 1-2 relevant prompt categories.
Gain visibility in 2-3 prompt categories.
Generate 5-10 mentions from trusted sources.
Establish a recognizable presence in local searches and begin to capture share of voice.
with conservative targets set at generating 1-3 detectable mentions and being visible in 1-3 prompt categories.
Aim for Begin generating prompt-level visibility in relevant prompt categories.
Increase mentions from 0 to 1-3.
Move from 0.0 visibility to 0.1 or more.
Total mentions, average visibility score, and prompts visible should each aim to increase from 0 to at least 1-3.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    blocked = [
        "Achieve visibility in at least",
        "Gain visibility in",
        "Generate 5-10 mentions",
        "capture share of voice",
        "conservative targets set",
        "1-3 detectable mentions",
        "visible in 1-3 prompt categories",
        "Aim for Begin generating",
        "Increase mentions from 0 to 1-3",
        "Move from 0.0 visibility to 0.1 or more",
        "should each aim to increase from 0 to at least 1-3",
    ]
    for phrase in blocked:
        assert phrase not in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories." in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert "Begin improving average visibility score in a future full benchmark." in clean
    assert (
        "Total mentions, average visibility score, and prompts visible should improve directionally in a future full benchmark."
        in clean
    )
    assert clean_issues == []


def test_final_report_quality_gate_cleans_latest_smoke_test_snippets():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
## Appendix A
AI-Discovered Brands Not Included in Scoring
- **Benchmark Against Competitors**: Consider adding non-tracked brands relevant to remote working to gain deeper insights and competitive advantages.
- **Highlight Amenities**: Clearly communicate Wi-Fi quality and work-friendly features in marketing materials.

## Appendix B
Achieve visibility in at least 1-2 relevant prompt categories.
Gain visibility in 2-3 prompt categories.
Generate 5-10 mentions from trusted sources.
Establish a recognizable presence in local searches and begin to capture share of voice.
with conservative targets set at generating 1-3 detectable mentions and being visible in 1-3 prompt categories.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    blocked = [
        "Benchmark Against Competitors",
        "Highlight Amenities",
        "Achieve visibility in at least",
        "Gain visibility in",
        "Generate 5-10 mentions",
        "capture share of voice",
        "conservative targets set",
        "1-3 detectable mentions",
        "visible in 1-3 prompt categories",
    ]
    for phrase in blocked:
        assert phrase not in clean
    assert "No additional non-tracked brands were identified." in clean
    assert clean_issues == []


def test_quick_test_current_state_diagnostics_are_preserved():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    diagnostics = [
        "Espresso House is currently not visible across the tested AI search prompts, with 0 total mentions, 0.0 average visibility, 0 prompts visible, and 0% share of voice.",
        "The main strategic issue is that AI systems have not produced measurable mentions for Espresso House in this benchmark, leaving the brand at 0% share of voice.",
        "No benchmark competitor generated measurable visibility, mentions, or share of voice in this run, so this benchmark does not identify a stronger competitor leader.",
        "Espresso House is currently not visible in AI-generated Cafes category recommendations in Berlin. The brand records 0 total mentions, an average visibility score of 0.0, 0 prompts visible, and 0% share of voice.",
    ]
    dirty = "\n".join(diagnostics)

    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    for sentence in diagnostics:
        assert sentence in clean
    assert clean_issues == []


def test_quick_test_future_target_statements_are_rewritten_without_affecting_diagnostics():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    dirty = """
Increase mentions from 0 to 1-3.
Move from 0.0 visibility to 0.1 or more.
Generate 5-10 mentions from trusted sources.
Achieve visibility in at least 1-2 relevant prompt categories.
with conservative targets set at generating 1-3 detectable mentions and being visible in 1-3 prompt categories.
Total mentions, average visibility score, and prompts visible should each aim to increase from 0 to at least 1-3.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    blocked = [
        "Increase mentions from 0 to 1-3",
        "Move from 0.0 visibility to 0.1 or more",
        "Generate 5-10 mentions",
        "Achieve visibility in at least 1-2",
        "conservative targets set",
        "should each aim to increase",
    ]
    for phrase in blocked:
        assert phrase not in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert "Begin improving average visibility score in a future full benchmark." in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories." in clean
    assert (
        "Total mentions, average visibility score, and prompts visible should improve directionally in a future full benchmark."
        in clean
    )
    assert clean_issues == []


def test_quick_test_mixed_report_preserves_current_state_and_rewrites_appendix_targets():
    context = OutputQualityContext(
        category="Cafes",
        run_mode="Quick Test Mode",
        brand="Espresso House",
        market="Berlin",
        audience="Remote Workers",
    )
    current_state = (
        "Espresso House is currently not visible across the tested AI search prompts, "
        "with 0 total mentions, 0.0 average visibility, 0 prompts visible, and 0% share of voice."
    )
    dirty = f"""
## Executive Summary
{current_state}

## Appendix B
Increase mentions from 0 to 1-3.
Move from 0.0 visibility to 0.1 or more.
Generate 5-10 mentions from trusted sources.
Achieve visibility in at least 1-2 relevant prompt categories.
""".strip()

    dirty_issues = validate_output_quality(dirty, context)
    clean = sanitize_report_text(dirty, context)
    clean_issues = validate_output_quality(clean, context)

    assert dirty_issues
    assert current_state in clean
    assert "Increase mentions from 0 to 1-3" not in clean
    assert "Move from 0.0 visibility to 0.1 or more" not in clean
    assert "Generate 5-10 mentions" not in clean
    assert "Achieve visibility in at least 1-2" not in clean
    assert "Begin generating detectable mentions in a future full benchmark." in clean
    assert "Begin improving average visibility score in a future full benchmark." in clean
    assert "Begin generating prompt-level visibility in relevant prompt categories." in clean
    assert clean_issues == []
