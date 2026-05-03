import pandas as pd

from narrative_prompts import (
    build_ai_decision_explanation_prompt,
    build_gap_analysis_prompt,
    build_narrative_detailed_context,
    build_narrative_summary_context,
    build_narrative_top_brands_context,
    build_replacement_strategy_prompt,
)


def create_narrative_inputs():
    summary_df = pd.DataFrame([
        {
            "brand": "The Barn",
            "total_mentions": 3,
            "average_visibility_score": 63.33,
            "prompts_visible": 2,
            "share_of_voice_percent": 25.0,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 6,
            "average_visibility_score": 75.0,
            "prompts_visible": 4,
            "share_of_voice_percent": 50.0,
        },
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "prompt": "Best cafes in Berlin",
            "brand": "The Barn",
            "mentions": 3,
            "visibility_score": 63.33,
            "visibility_level": "high",
            "is_target_brand": True,
            "first_position": 320,
            "estimated_rank": 1,
        }
    ])
    top_brands_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "The Barn",
            "visibility_score": 63.33,
            "first_position": 320,
        }
    ])

    return summary_df, detailed_df, top_brands_df


def test_narrative_context_tables_use_grounded_fields_only():
    summary_df, detailed_df, top_brands_df = create_narrative_inputs()

    summary_context = build_narrative_summary_context(summary_df)
    detailed_context = build_narrative_detailed_context(detailed_df)
    top_brands_context = build_narrative_top_brands_context(top_brands_df)

    assert "Total Mentions" in summary_context
    assert "Average Visibility Score" in summary_context
    assert "Prompts Visible" in summary_context
    assert "Share of Voice %" in summary_context
    assert "first_position" not in summary_context

    assert "Query Type" in detailed_context
    assert "Visibility Score" in detailed_context
    assert "first_position" not in detailed_context
    assert "estimated_rank" not in detailed_context

    assert "Winning Brand" in top_brands_context
    assert "Visibility Score" in top_brands_context
    assert "first_position" not in top_brands_context


def test_ai_decision_explanation_prompt_includes_numeric_grounding_guard():
    _, detailed_df, top_brands_df = create_narrative_inputs()

    prompt = build_ai_decision_explanation_prompt(
        brand="The Barn",
        category="cafes",
        market="Berlin",
        top_brands_df=top_brands_df,
        detailed_df=detailed_df,
    )

    assert "Use only numeric metrics explicitly provided" in prompt
    assert "Do not invent mention counts" in prompt
    assert "Do not treat character positions, first_position" in prompt
    assert "If a metric is not provided, describe it qualitatively" in prompt
    assert "mention count 320" in prompt
    assert "visibility score of 320" in prompt
    assert "first_position" not in build_narrative_detailed_context(detailed_df)


def test_replacement_and_gap_prompts_include_numeric_grounding_guard():
    summary_df, detailed_df, top_brands_df = create_narrative_inputs()

    replacement_prompt = build_replacement_strategy_prompt(
        brand="The Barn",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        top_brands_df=top_brands_df,
        summary_df=summary_df,
        detailed_df=detailed_df,
        raw_answers=[{"answer": "The Barn is often recommended."}],
    )
    gap_prompt = build_gap_analysis_prompt(
        brand="The Barn",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["Coffee Fellows"],
        summary_df=summary_df,
        detailed_df=detailed_df,
    )

    for prompt in [replacement_prompt, gap_prompt]:
        assert "Use only numeric metrics explicitly provided" in prompt
        assert "Do not invent mention counts" in prompt
        assert "Do not treat character positions, first_position" in prompt
        assert "If a metric is not provided, describe it qualitatively" in prompt
