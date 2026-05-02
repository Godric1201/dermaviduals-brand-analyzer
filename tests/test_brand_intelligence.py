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
