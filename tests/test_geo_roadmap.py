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
