import pandas as pd
import pytest

from conftest import import_without_real_analyzer


@pytest.fixture()
def geo_roadmap_module():
    return import_without_real_analyzer("geo_roadmap")


def test_generate_geo_content_roadmap_builds_consulting_prompt(
    monkeypatch,
    geo_roadmap_module,
):
    captured_prompts = []

    def fake_ask_ai(prompt, language="English"):
        captured_prompts.append((prompt, language))
        return "| Priority | Query Intent | Content Asset |\n|---|---|---|\n| 1 | Best Options | Comparison page |"

    monkeypatch.setattr(geo_roadmap_module, "ask_ai", fake_ask_ai)

    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 2,
            "average_visibility_score": 4,
        }
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Espresso House",
            "visibility_score": 4,
        }
    ])
    brand_intelligence = {
        "recommendation_drivers": "Reviews and local convenience",
        "target_brand_understanding": "AI-inferred cafe brand",
        "positioning_gap_analysis": "Needs stronger comparison visibility",
    }

    result = geo_roadmap_module.generate_geo_content_roadmap(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["Coffee Fellows", "Einstein Kaffee"],
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence=brand_intelligence,
        query_intent_categories=["Best Options", "Local Recommendations"],
        report_language="English",
    )

    prompt, language = captured_prompts[0]

    assert result.startswith("| Priority | Query Intent | Content Asset |")
    assert language == "English"
    assert "Espresso House" in prompt
    assert "cafes" in prompt
    assert "Berlin" in prompt
    assert "remote workers" in prompt
    assert "Coffee Fellows" in prompt
    assert "Best Options" in prompt
    assert "query intent" in prompt.lower()
    assert "Content Asset" in prompt
    assert "Evidence Needed" in prompt
    assert "Expected Metric Impact" in prompt
    assert "distinct content asset" in prompt
    assert "Do not repeat" in prompt
    assert "Every Content Asset must be a specific publishable title" in prompt
    assert "Generic assets are forbidden" in prompt
    assert "publishable" in prompt
    assert "Do not use vague/internal strategy assets" in prompt
    assert "Evidence Needed must be concrete" in prompt
    assert "Do not claim guaranteed metric improvement" in prompt
    assert "Intended benchmark influence" in prompt
    assert "Only use clinical-study claims if substantiated and compliant" in prompt
    assert "only where substantiated and compliant" in prompt
    assert "third-party evidence" in prompt
    assert "expert validation" in prompt
    assert "ingredient documentation" in prompt
    assert "not part of visibility scoring" in prompt
    assert "30 Days" in prompt
    assert "60 Days" in prompt
    assert "90 Days" in prompt
    assert "Next Benchmark Cycle" in prompt
    assert "No calendar quarters" in prompt
    assert "specific years" in prompt
    assert "total mentions" in prompt
    assert "average visibility score" in prompt
    assert "prompts visible" in prompt
    assert "share of voice" in prompt
    assert "query intent visibility" in prompt
    assert "target-brand association" in prompt
    assert "Quick Test Mode" in prompt
    assert "directional" in prompt
    assert "Do not make unsupported performance promises" in prompt


def test_geo_roadmap_generic_asset_and_claim_safety_sanitizers(geo_roadmap_module):
    assert geo_roadmap_module.is_generic_content_asset(
        "Comparison Page for Top Products"
    ) is True

    roadmap = "\n".join([
        "| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |",
        "|---|---|---|---|---|---|---|---|",
        "| 1 | Local Recommendations | Comparison Page for Top Products | Ingredient transparency | SkinCeuticals | clinical trials and clinically effective proof | Intended benchmark influence: total_mentions and prompts_visible | 30 Days |",
        "| 2 | Decision Criteria | FAQ Page on Product Benefits | Sensitive skin fit | | published studies demonstrating product effectiveness | Intended benchmark influence: target-brand association | 60 Days |",
        "| 3 | Trust Signals | Review Collection Initiative | Review proof | | customer reviews | Intended benchmark influence: query intent visibility | 90 Days |",
        "| 4 | Evidence | Evidence-Building Page on Ingredients | Product proof | | clinical efficacy and medical-grade claims | Intended benchmark influence: average_visibility_score | Next Benchmark Cycle |",
    ])

    sanitized = geo_roadmap_module.sanitize_geo_roadmap_markdown(
        roadmap,
        brand="Dermaviduals",
        market="Hong Kong",
        category="skincare products",
        audience="skincare-conscious consumers",
        tracked_competitors=["SkinCeuticals", "Environ"],
    )

    assert "Dermaviduals vs SkinCeuticals Comparison Page for Hong Kong Consumers" in sanitized
    assert "Dermaviduals Product Benefits FAQ for Skincare-Conscious Consumers in Hong Kong" in sanitized
    assert "Dermaviduals Hong Kong Customer Review Collection Page" in sanitized
    assert "Dermaviduals Ingredient Evidence & Product Selection Page" in sanitized
    assert "claims support documentation, only where substantiated and compliant" in sanitized
    assert "evidence-supported" in sanitized
    assert "substantiated product evidence" in sanitized
    assert "professional-grade positioning, where substantiated" in sanitized
    assert "Intended benchmark influence: total_mentions and prompts_visible" in sanitized
    assert "30%" not in sanitized
