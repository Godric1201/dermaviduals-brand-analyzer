import pandas as pd
import pytest

from conftest import import_without_real_analyzer


@pytest.fixture()
def brand_intelligence_module():
    return import_without_real_analyzer("brand_intelligence")


def create_fake_inputs():
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 1,
            "average_visibility_score": 4,
            "prompts_visible": 1,
            "share_of_voice_percent": 25,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 3,
            "average_visibility_score": 7,
            "prompts_visible": 2,
            "share_of_voice_percent": 75,
        },
    ])

    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "prompt": "Best cafes in Berlin",
            "brand": "Coffee Fellows",
            "visibility_score": 7,
        }
    ])

    raw_answers = [
        {
            "prompt_category": "Best Options",
            "prompt": "Best cafes in Berlin",
            "answer": "Coffee Fellows is often mentioned for convenient cafe locations.",
        }
    ]

    return summary_df, detailed_df, raw_answers


def test_run_brand_intelligence_analysis_returns_expected_keys(
    monkeypatch,
    brand_intelligence_module
):
    captured_prompts = []

    def fake_ask_ai(prompt, language="English"):
        captured_prompts.append(prompt)
        return f"fake response {len(captured_prompts)}"

    monkeypatch.setattr(brand_intelligence_module, "ask_ai", fake_ask_ai)

    summary_df, detailed_df, raw_answers = create_fake_inputs()

    result = brand_intelligence_module.run_brand_intelligence_analysis(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows", "einstein kaffee"],
        raw_answers=raw_answers,
        summary_df=summary_df,
        detailed_df=detailed_df,
        user_brand_strengths=["quiet work tables", "central locations"],
    )

    expected_keys = {
        "diagnostic_prompts",
        "diagnostic_answers",
        "recommendation_drivers",
        "target_brand_understanding",
        "positioning_gap_analysis",
        "user_brand_strengths",
        "validation_note",
    }

    assert set(result) == expected_keys
    assert len(result["diagnostic_prompts"]) == 6
    assert len(result["diagnostic_answers"]) == len(result["diagnostic_prompts"])
    assert len(captured_prompts) == len(result["diagnostic_prompts"]) + 3
    assert result["validation_note"]
    assert result["user_brand_strengths"] == [
        "quiet work tables",
        "central locations",
    ]


def test_run_brand_intelligence_analysis_prompts_include_context(
    monkeypatch,
    brand_intelligence_module
):
    captured_prompts = []

    def fake_ask_ai(prompt, language="English"):
        captured_prompts.append(prompt)
        return "fake response"

    monkeypatch.setattr(brand_intelligence_module, "ask_ai", fake_ask_ai)

    summary_df, detailed_df, raw_answers = create_fake_inputs()

    brand_intelligence_module.run_brand_intelligence_analysis(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows", "einstein kaffee"],
        raw_answers=raw_answers,
        summary_df=summary_df,
        detailed_df=detailed_df,
    )

    for prompt in captured_prompts:
        assert "Espresso House" in prompt
        assert "cafes" in prompt
        assert "Berlin" in prompt
        assert "remote workers" in prompt

    combined_prompts = "\n".join(captured_prompts)

    assert "Prompted Diagnostic Fit" in combined_prompts
    assert "Natural benchmark visibility" in combined_prompts
    assert "target-branded diagnostic assessment requiring validation" in combined_prompts
    assert "Benchmark-derived" in combined_prompts
    assert "AI-inferred" in combined_prompts
    assert "User-provided" in combined_prompts
    assert "Tracked Competitors Included in Scoring" in combined_prompts
    assert "AI-Discovered Market Signals Not Included in Scoring" in combined_prompts
    assert "tracked competitors" in combined_prompts
    assert "AI-discovered market signals" in combined_prompts
    assert "tracked competitor list is the only source of truth" in combined_prompts.lower()
    assert "Never label a non-tracked brand as Source: Tracked competitor" in combined_prompts
    assert "Do not list tracked competitors as AI-discovered market signals" in combined_prompts
    assert "verify it is not already in the tracked competitor list" in combined_prompts
    assert "prefer tracked competitors first" in combined_prompts.lower()
    assert "selected as tracked competitors before the benchmark run" in combined_prompts or "Consider adding these brands as tracked competitors before the benchmark run" in combined_prompts
    assert "Do not call non-tracked brands competitors included in benchmark" in combined_prompts
    assert "Prefer compact tables or bullet lists" in combined_prompts
    assert "Avoid generic advice" in combined_prompts
    assert "Advantage Signal | Evidence Source | Example Brands | Source Type" in combined_prompts
    assert "Recommendation likelihood" not in combined_prompts


def test_run_brand_intelligence_analysis_tracks_progress(
    monkeypatch,
    brand_intelligence_module
):
    def fake_ask_ai(prompt, language="English"):
        return "fake response"

    monkeypatch.setattr(brand_intelligence_module, "ask_ai", fake_ask_ai)

    summary_df, detailed_df, raw_answers = create_fake_inputs()
    progress_steps = []

    brand_intelligence_module.run_brand_intelligence_analysis(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows"],
        raw_answers=raw_answers,
        summary_df=summary_df,
        detailed_df=detailed_df,
        on_progress=progress_steps.append,
    )

    assert progress_steps == [
        "diagnostic_prompts",
        "recommendation_drivers",
        "target_understanding",
        "positioning_gap",
    ]


def test_brand_intelligence_does_not_import_scoring(brand_intelligence_module):
    assert "scoring" not in brand_intelligence_module.__dict__
    assert "analyze_answer" not in brand_intelligence_module.__dict__
    assert "summarize_results" not in brand_intelligence_module.__dict__
    assert "calculate_share_of_voice" not in brand_intelligence_module.__dict__


def test_correct_competitor_source_labels_rewrites_non_tracked_brands(
    brand_intelligence_module,
):
    text = """
1. **SkinCeuticals** - Strong antioxidant authority. (Source: Tracked competitor)
2. **Obagi** - Known for prescription-strength products. (Source: Tracked competitor)
3. **La Roche-Posay** - Sensitive skin trust. (Source: Tracked competitor)
""".strip()

    corrected = brand_intelligence_module.correct_competitor_source_labels(
        text,
        ["SkinCeuticals", "Dr. Dennis Gross", "iS Clinical"],
    )

    assert "**SkinCeuticals** - Strong antioxidant authority. (Source: Tracked competitor)" in corrected
    assert "**Obagi** - Known for prescription-strength products. (Source: AI-discovered market signal)" in corrected
    assert "**La Roche-Posay** - Sensitive skin trust. (Source: AI-discovered market signal)" in corrected


def test_correct_competitor_source_labels_matches_case_insensitively(
    brand_intelligence_module,
):
    text = """
- **dr. dennis gross** - Review-led authority. (Source: AI-discovered market signal)
- **La Roche-Posay** - Sensitive skin trust. (Source: Tracked competitor)
""".strip()

    corrected = brand_intelligence_module.correct_competitor_source_labels(
        text,
        ["Dr. Dennis Gross", "SkinCeuticals"],
    )

    assert "- **dr. dennis gross** - Review-led authority. (Source: Tracked competitor)" in corrected
    assert "- **La Roche-Posay** - Sensitive skin trust. (Source: AI-discovered market signal)" in corrected


def test_run_brand_intelligence_analysis_corrects_source_labels_in_outputs(
    monkeypatch,
    brand_intelligence_module,
):
    summary_df, detailed_df, raw_answers = create_fake_inputs()
    responses = iter([
        "diagnostic 1",
        "diagnostic 2",
        "diagnostic 3",
        "diagnostic 4",
        "diagnostic 5",
        "diagnostic 6",
        "1. **SkinCeuticals** - Strong antioxidant authority. (Source: Tracked competitor)\n2. **Obagi** - Known for prescription-strength products. (Source: Tracked competitor)",
        "- **Dr. Dennis Gross** - High review trust. (Source: AI-discovered market signal)",
        "- **La Roche-Posay** - Sensitive skin trust. (Source: Tracked competitor)",
    ])

    monkeypatch.setattr(
        brand_intelligence_module,
        "ask_ai",
        lambda prompt, language="English": next(responses),
    )

    result = brand_intelligence_module.run_brand_intelligence_analysis(
        brand="Dermaviduals",
        category="skincare products",
        market="Hong Kong",
        audience="skincare-conscious consumers",
        competitors=["SkinCeuticals", "Dr. Dennis Gross", "iS Clinical"],
        raw_answers=raw_answers,
        summary_df=summary_df,
        detailed_df=detailed_df,
    )

    assert "(Source: AI-discovered market signal)" in result["recommendation_drivers"]
    assert "**Obagi** - Known for prescription-strength products. (Source: AI-discovered market signal)" in result["recommendation_drivers"]
    assert "**Dr. Dennis Gross** - High review trust. (Source: Tracked competitor)" in result["target_brand_understanding"]
    assert "**La Roche-Posay** - Sensitive skin trust. (Source: AI-discovered market signal)" in result["positioning_gap_analysis"]


def test_remove_tracked_competitors_from_market_signals_filters_existing_tracked(
    brand_intelligence_module,
):
    text = """
AI-Discovered Market Signals Not Included in Scoring
- **Obagi** - Prescription-led familiarity. (Source: AI-discovered market signal)
- **Universkin** - Personalized skincare positioning. (Source: AI-discovered market signal)
Consider adding non-tracked relevant brands like Universkin and Mesoestetic.
Tracked Competitors Included in Scoring
- **SkinCeuticals** - Antioxidant authority. (Source: Tracked competitor)
""".strip()

    cleaned = brand_intelligence_module.remove_tracked_competitors_from_market_signals(
        text,
        ["SkinCeuticals", "Universkin", "Mesoestetic"],
    )

    assert "**Obagi** - Prescription-led familiarity. (Source: AI-discovered market signal)" in cleaned
    assert "**Universkin** - Personalized skincare positioning." not in cleaned
    assert "AI-Discovered Brands Not Included in Scoring" in cleaned
    assert "**SkinCeuticals** - Antioxidant authority. (Source: Tracked competitor)" in cleaned


def test_brand_intelligence_claim_safety_rewrites_regulated_phrasing(
    brand_intelligence_module,
):
    text = (
        "Published studies demonstrating product effectiveness and clinical efficacy "
        "can prove effectiveness through clinical validations and medical-grade claims."
    )

    sanitized = brand_intelligence_module.sanitize_claim_safety(
        text,
        "skincare products",
    )

    assert "consumer study documentation or compliant claims support" in sanitized
    assert "product claims" in sanitized
    assert "support product claims" in sanitized
    assert "expert validation and claims support documentation" in sanitized
    assert "professional-grade positioning, where substantiated" in sanitized


def test_correct_competitor_source_labels_handles_multi_brand_lines(
    brand_intelligence_module,
):
    text = """
2. **Established Dermatological Reputation** - Brands such as La Roche-Posay and Obagi are often cited.
   *Source: Tracked competitor*
3. **Professional Ingredient Trust** - Brands like iS Clinical and SkinCeuticals are often cited.
   (Source: Tracked competitor)
4. **Mixed Comparison Set** - Brands like SkinCeuticals and Obagi appear together.
   (Source: Tracked competitor)
""".strip()

    corrected = brand_intelligence_module.correct_competitor_source_labels(
        text,
        ["iS Clinical", "SkinCeuticals"],
    )

    assert "(Source: AI-discovered market signal)" in corrected
    assert "(Source: Mixed tracked competitor / AI-discovered market signal)" in corrected
    assert corrected.count("(Source: Tracked competitor)") == 1


def test_claim_safety_rewrites_new_harder_phrasing(
    brand_intelligence_module,
):
    text = (
        "Clinical studies or consumer feedback validating product effectiveness. "
        "Invest in claims support documentation, only where substantiated and compliant or studies to substantiate efficacy claims."
    )

    sanitized = brand_intelligence_module.sanitize_claim_safety(
        text,
        "skincare products",
    )

    assert "Claims support documentation, consumer feedback, or expert validation, only where substantiated and compliant" in sanitized
    assert "Develop claims support documentation and consumer evidence where substantiated and compliant" in sanitized


def test_classify_source_type_from_example_brands(brand_intelligence_module):
    assert brand_intelligence_module.classify_source_type_from_example_brands(
        ["SkinCeuticals", "Environ"],
        ["SkinCeuticals", "Environ", "iS Clinical"],
    ) == "Tracked competitors"

    assert brand_intelligence_module.classify_source_type_from_example_brands(
        ["Obagi", "CeraVe"],
        ["SkinCeuticals", "Environ", "iS Clinical"],
    ) == "AI-discovered market signals"

    assert brand_intelligence_module.classify_source_type_from_example_brands(
        ["SkinCeuticals", "Obagi"],
        ["SkinCeuticals", "Environ", "iS Clinical"],
    ) == "Mixed tracked competitors / AI-discovered market signals"


def test_sanitize_competitor_advantage_tables_uses_clean_schema(
    brand_intelligence_module,
):
    text = "\n".join([
        "| Advantage Signal | Source |",
        "|---|---|",
        "| Proven effectiveness in addressing aging and pigmentation | (Source: AI-discovered market signal) |",
        "| Antioxidant authority with SkinCeuticals and Environ | (Source: Tracked competitor) |",
    ])

    sanitized = brand_intelligence_module.sanitize_competitor_advantage_tables(
        text,
        ["SkinCeuticals", "Environ"],
    )

    assert "| Advantage Signal | Evidence Source | Example Brands | Source Type |" in sanitized
    assert "(Source:" not in sanitized
    assert "Tracked competitors" in sanitized
    assert "AI-discovered market signals" in sanitized


def test_claim_safety_removes_additional_bad_clinical_phrasing(
    brand_intelligence_module,
):
    text = (
        "Clinical studies or data demonstrating product efficacy in the local context. "
        "Clinical studies or data demonstrating product efficacy. "
        "clinical studies. clinical evidence. Collaborate with dermatologists for clinical studies. "
        "substantiated product evidence Data. Studies or data demonstrating efficacy in Hong Kong."
    )

    sanitized = brand_intelligence_module.sanitize_claim_safety(
        text,
        "skincare products",
    )

    assert "clinical studies" not in sanitized.lower()
    assert "clinical evidence" not in sanitized.lower()
    assert "substantiated product evidence" not in sanitized
    assert "Collaborate with qualified professionals to review evidence and claims support materials" in sanitized
    assert "Claims Support Documentation" in sanitized
    assert "consumer feedback, expert validation, ingredient documentation, or compliant claims support" in sanitized


def test_claim_safety_cleans_awkward_sentences_and_clinical_wording(
    brand_intelligence_module,
):
    text = (
        "Absence of claims support documentation, where substantiated and compliant validating product efficacy specific to the Hong Kong demographic. "
        "Promote the efficacy of products through claims support documentation, where substantiated and compliant and consumer testimonials. "
        "Professional and Clinical Endorsement. clinically proven antioxidant products. clinical endorsements."
    )

    sanitized = brand_intelligence_module.sanitize_claim_safety(
        text,
        "skincare products",
    )

    assert "Absence of claims support documentation, consumer feedback, or expert validation specific to the Hong Kong market." in sanitized
    assert "Support product claims with compliant documentation, consumer testimonials, and expert validation." in sanitized
    assert "Professional Trust Signals" in sanitized
    assert "evidence-supported antioxidant products" in sanitized
    assert "professional endorsements" in sanitized
    assert "where substantiated and compliant and" not in sanitized
    assert "claims support documentation, where substantiated and compliant validating" not in sanitized


def test_market_signal_cleanup_splits_trends_from_brands(
    brand_intelligence_module,
):
    text = """
AI-Discovered Market Signals Not Included in Scoring
- **Obagi** - Prescription-led familiarity. (Source: AI-discovered market signal)
- Increased Focus on Clean Beauty
- Interest in Personalized Skincare
Tracked Competitors Included in Scoring
- **SkinCeuticals** - Antioxidant authority. (Source: Tracked competitor)
""".strip()

    cleaned = brand_intelligence_module.remove_tracked_competitors_from_market_signals(
        text,
        ["SkinCeuticals"],
    )

    assert "AI-Discovered Brands Not Included in Scoring" in cleaned
    assert "Market Trends / Demand Signals" in cleaned
    assert "**Obagi** - Prescription-led familiarity. (Source: AI-discovered market signal)" in cleaned
    assert "Increased Focus on Clean Beauty" in cleaned
    assert "Interest in Personalized Skincare" in cleaned


def test_market_signal_cleanup_uses_no_additional_brands_when_only_trends_remain(
    brand_intelligence_module,
):
    text = """
AI-Discovered Market Signals Not Included in Scoring
- Increased Focus on Clean Beauty
- Interest in Personalized Skincare
""".strip()

    cleaned = brand_intelligence_module.remove_tracked_competitors_from_market_signals(
        text,
        ["SkinCeuticals"],
    )

    assert "AI-Discovered Brands Not Included in Scoring" in cleaned
    assert "No additional non-tracked brands were identified." in cleaned
    assert "Market Trends / Demand Signals" in cleaned


def test_ai_discovered_brands_section_removes_non_brand_action_items(
    brand_intelligence_module,
):
    text = """
AI-Discovered Brands Not Included in Scoring
- Market Research
- Distribution Strategy
- Marketing Campaigns
- Local claims support documentation for Hong Kong skin concerns
Tracked Competitors Included in Scoring
- **SkinCeuticals** - Antioxidant authority. (Source: Tracked competitor)
""".strip()

    cleaned = brand_intelligence_module.sanitize_ai_discovered_brands_sections(
        text,
        ["SkinCeuticals"],
    )

    assert "Market Research" not in cleaned
    assert "Distribution Strategy" not in cleaned
    assert "Marketing Campaigns" not in cleaned
    assert "Local claims support documentation" not in cleaned
    assert "No additional non-tracked brands were identified." in cleaned
    assert "**SkinCeuticals** - Antioxidant authority. (Source: Tracked competitor)" in cleaned


def test_claim_safety_removes_remaining_high_risk_wording(
    brand_intelligence_module,
):
    text = (
        "claims support documentation, where substantiated and compliant showing product effectiveness in local skin concerns. "
        "Absence of studies demonstrating product effectiveness for common skin concerns in the local market. "
        "Medical-Grade Efficacy. Strong clinical backing. clinical backing."
    )

    sanitized = brand_intelligence_module.sanitize_claim_safety(
        text,
        "skincare products",
    )

    assert "claims support documentation, consumer feedback, or expert validation for Hong Kong market claims" in sanitized
    assert "Absence of claims support documentation, consumer feedback, or expert validation for local market claims." in sanitized
    assert "Evidence-Supported Product Positioning" in sanitized
    assert "Strong evidence-supported positioning" in sanitized
    assert "clinical backing" not in sanitized.lower()
