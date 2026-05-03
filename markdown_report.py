from ui_formatters import df_to_markdown_table
from report_generator import (
    build_competitor_leader_sentence,
    get_competitor_leaders,
    get_visibility_status,
)


def build_executive_markdown_report(
    brand,
    display_brand,
    category,
    display_category,
    market,
    display_market,
    audience,
    display_audience,
    run_mode,
    prompt_limit,
    deliverable_status,
    summary_df,
    summary_display_df,
    detailed_pivot_df,
    top_brands_df,
    recommendations,
    plan,
    gap_analysis=None,
    brand_win_explanation=None,
    replacement_strategy=None,
    brand_intelligence=None,
    brand_intelligence_done=False,
    geo_content_roadmap=None,
    geo_content_roadmap_done=False,
    prompt_categories=None,
):
    is_quick_test_mode = run_mode == "Quick Test Mode"
    prompt_categories = prompt_categories or []
    brand_intelligence = brand_intelligence or {}

    summary_columns = [
        "brand",
        "total_mentions",
        "average_visibility_score",
        "prompts_visible",
        "share_of_voice_percent",
    ]
    available_summary_columns = [
        col for col in summary_columns
        if col in summary_display_df.columns
    ]
    summary_report_df = summary_display_df[available_summary_columns].sort_values(
        by="average_visibility_score",
        ascending=False,
    )
    summary_report_md = df_to_markdown_table(summary_report_df, max_rows=15)
    trigger_report_md = df_to_markdown_table(detailed_pivot_df, max_rows=25)
    top_brands_report_md = (
        df_to_markdown_table(top_brands_df, max_rows=25)
        if top_brands_df is not None and not top_brands_df.empty
        else "_No positive brand winners detected._"
    )

    target_summary = summary_df[
        summary_df["brand"].astype(str).str.lower() == str(brand).lower()
    ]

    if not target_summary.empty:
        target_mentions = target_summary.iloc[0].get("total_mentions", 0)
        target_avg_score = target_summary.iloc[0].get("average_visibility_score", 0)
        target_prompts_visible = target_summary.iloc[0].get("prompts_visible", 0)
        target_sov = target_summary.iloc[0].get("share_of_voice_percent", 0)
    else:
        target_mentions = 0
        target_avg_score = 0
        target_prompts_visible = 0
        target_sov = 0

    target_visibility_status = get_visibility_status(
        target_mentions,
        target_avg_score,
        target_sov,
    )
    competitor_leaders = get_competitor_leaders(summary_df, brand)
    top_competitor_text = build_competitor_leader_sentence(competitor_leaders)

    if target_mentions == 0:
        strategic_issue = (
            f"The main strategic issue is that AI systems have not produced measurable mentions for {display_brand} "
            f"in this benchmark, leaving the brand at {target_sov}% share of voice."
        )
    else:
        strategic_issue = (
            f"The main strategic issue is to improve from {target_mentions} mentions, "
            f"{target_avg_score} average visibility, and {target_sov}% share of voice by strengthening association "
            f"with high-intent use cases, comparison queries, local intent, decision-stage searches, "
            f"and market-specific category questions for {display_category} in {display_market}."
        )

    executive_summary_sentence = (
        f"{display_brand} is {target_visibility_status} across the tested AI search prompts, "
        f"with {target_mentions} total mentions, {target_avg_score} average visibility, "
        f"{target_prompts_visible} prompts visible, and {target_sov}% share of voice."
    )
    query_intent_md = "\n".join(
        f"- {item}" for item in prompt_categories
    ) or "_No query intent categories available._"

    brand_intelligence_md = ""
    if brand_intelligence_done and brand_intelligence:
        brand_intelligence_md = f"""

    ---

    ## Appendix: Brand Intelligence & Positioning Audit

    > Diagnostic insight. Not part of visibility scoring. Tracked competitors are included in visibility scoring and share of voice. Other brands mentioned here may be AI-discovered market signals and are not included in scoring unless added as tracked competitors.

    ### Recommendation Drivers

    {brand_intelligence["recommendation_drivers"]}

    ### AI-Inferred Target Brand Understanding

    {brand_intelligence["target_brand_understanding"]}

    ### Positioning Gap Analysis

    {brand_intelligence["positioning_gap_analysis"]}
    """

    geo_content_roadmap_md = ""
    if geo_content_roadmap_done and geo_content_roadmap:
        geo_content_roadmap_md = f"""

    ---

    ## GEO Content Roadmap

    > Strategic execution plan. Not part of visibility scoring or share of voice.

    {geo_content_roadmap}
    """

    return f"""
    # {display_brand} {display_market} AI Visibility Report

    ## 1. Report Overview

    **Target Brand:** {display_brand}  
    **Market:** {display_market}  
    **Category:** {display_category}  
    **Audience:** {display_audience}  
    **Report Type:** AI Visibility / Generative Engine Optimization Audit  
    **Run Mode:** {run_mode}  
    **Deliverable Status:** {deliverable_status}  

    {"**TEST VERSION ONLY - Quick Test Mode. Not Client Deliverable.**" if is_quick_test_mode else ""}

    This report evaluates how visible {display_brand} is in AI-generated {display_category} recommendations for {display_audience} in {display_market}.

    ### Query Intent Coverage

    This benchmark covers the following AI recommendation contexts:

    {query_intent_md}

    ---

    ## 2. Executive Summary

    {executive_summary_sentence}

    Key metrics for {display_brand}:

    | Metric | Value |
    |---|---:|
    | Total Mentions | {target_mentions} |
    | Average Visibility Score | {target_avg_score} |
    | Prompts Visible | {target_prompts_visible} |
    | Share of Voice | {target_sov}% |

    Top visible competitors in this benchmark:

    {top_competitor_text}

    {strategic_issue}

    ---

    ## 3. Competitive Benchmark

    The table below summarizes brand-level AI visibility performance across all tested prompts.

    {summary_report_md}

    ---

    ## 4. Trigger-Level Visibility Findings

    The table below shows how each tracked brand performs across AI query categories.

    {trigger_report_md}

    ---

    ## 5. Top Brand Winners by Query Type

    The table below identifies which brand wins each query category based on visibility score.

    {top_brands_report_md}

    ---

    ## 6. Strategic Diagnosis

    {gap_analysis or "_AI Association Gap analysis was not generated in this run._"}

    ---

    ## 7. Priority Strategic Recommendations

    {recommendations}

    ---

    ## 8. AI Visibility Strategy Report

    {plan}

    ---

    ## 9. Appendix: AI Decision Explanation

    {brand_win_explanation or "_Brand winner explanation was not generated in this run._"}

    ---

    ## 10. Appendix: Replacement Strategy

    {replacement_strategy or "_Replacement strategy was not generated in this run._"}
    {brand_intelligence_md}
    {geo_content_roadmap_md}
    """
