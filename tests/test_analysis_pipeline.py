import pandas as pd

import analysis_pipeline


def patch_pipeline_dependencies(monkeypatch, captured_prompt_kwargs=None):
    def fake_generate_search_prompts(**kwargs):
        if captured_prompt_kwargs is not None:
            captured_prompt_kwargs.update(kwargs)

        return [
            {"category": "AI 1", "prompt": "AI prompt 1"},
            {"category": "AI 2", "prompt": "AI prompt 2"},
        ]

    monkeypatch.setattr(
        analysis_pipeline,
        "generate_search_prompts",
        fake_generate_search_prompts,
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "ask_ai",
        lambda prompt, language: f"Answer for {prompt}",
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "analyze_answer",
        lambda **kwargs: [{"brand": kwargs["brand"], "visibility_score": 1}],
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "summarize_results",
        lambda all_results: (
            pd.DataFrame([
                {
                    "brand": "Dermaviduals",
                    "visibility_score": 1,
                }
            ]),
            pd.DataFrame([
                {
                    "brand": "Dermaviduals",
                    "total_mentions": len(all_results),
                    "average_visibility_score": 1,
                    "prompts_visible": len(all_results),
                }
            ]),
        ),
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "calculate_share_of_voice",
        lambda summary_df: summary_df.assign(share_of_voice_percent=100),
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "generate_recommendations",
        lambda **kwargs: "Test recommendations",
    )
    monkeypatch.setattr(
        analysis_pipeline,
        "generate_action_plan",
        lambda **kwargs: "Test action plan",
    )


def run_test_analysis(prompt_limit, on_progress=None, competitors=None):
    return analysis_pipeline.run_visibility_analysis(
        brand="Dermaviduals",
        category="skincare products",
        market="Hong Kong",
        audience="skincare-conscious consumers in Hong Kong",
        answer_language="English",
        report_language="English",
        fixed_prompts=[
            {"category": "Fixed 1", "prompt": "Fixed prompt 1"},
            {"category": "Fixed 2", "prompt": "Fixed prompt 2"},
        ],
        on_progress=on_progress,
        prompt_limit=prompt_limit,
        competitors=competitors,
    )


def test_run_visibility_analysis_applies_prompt_limit(monkeypatch):
    patch_pipeline_dependencies(monkeypatch)
    progress_calls = []

    result = run_test_analysis(
        prompt_limit=1,
        on_progress=lambda index, total, category: progress_calls.append(
            (index, total, category)
        ),
    )

    assert len(result["prompts"]) == 1
    assert len(result["raw_answers"]) == 1
    assert progress_calls == [(0, 1, "Fixed 1")]


def test_run_visibility_analysis_uses_all_prompts_without_limit(monkeypatch):
    patch_pipeline_dependencies(monkeypatch)

    result = run_test_analysis(prompt_limit=None)

    assert len(result["prompts"]) == 4
    assert len(result["raw_answers"]) == 4


def test_run_visibility_analysis_uses_custom_competitors(monkeypatch):
    captured_prompt_kwargs = {}
    patch_pipeline_dependencies(monkeypatch, captured_prompt_kwargs)
    custom_competitors = ["Brand A", "Brand B"]

    result = run_test_analysis(
        prompt_limit=1,
        competitors=custom_competitors,
    )

    assert result["competitors"] == custom_competitors
    assert captured_prompt_kwargs["competitors"] == custom_competitors
