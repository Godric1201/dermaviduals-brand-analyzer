import pandas as pd

from ui_formatters import df_to_markdown_table
from report_generator import (
    build_competitor_leader_sentence,
    build_measurement_plan_rows,
    create_roadmap_df,
    get_competitor_leaders,
    get_target_metrics,
    get_top_competitors,
    get_visibility_status,
    get_visibility_state_noun,
)
from prompts import format_audience_market_context
from output_quality import (
    OutputQualityContext,
    guard_generated_section_text,
    sanitize_report_text,
    validate_output_quality,
)


def _normalize_markdown_table_headers(df, column_map):
    if df is None:
        return df

    return df.copy().rename(columns={
        column: label
        for column, label in column_map.items()
        if column in df.columns
    })


def _append_section(parts, title, body):
    if not body:
        return

    parts.append(f"## {title}\n\n{body.strip()}")


def _build_measurement_plan_md(metrics):
    measurement_df = df_to_markdown_table(
        _normalize_markdown_table_headers(
            pd.DataFrame(build_measurement_plan_rows(metrics)),
            {},
        ),
        max_rows=10,
    )

    return (
        "The next benchmark should evaluate whether the visibility gap is beginning to close.\n\n"
        f"{measurement_df}"
    )


def _build_methodology_notes_md(category, prompt_categories):
    notes = [
        f"- The benchmark is based on fixed and AI-generated prompts designed to simulate {category} recommendation queries.",
        "- Visibility is calculated from brand mentions, estimated ranking, and prompt-level appearance.",
        "- Share of voice reflects the distribution of brand mentions among tracked competitors.",
        "- Scores reflect AI answer visibility, not market share, product performance, customer satisfaction, or broader business performance outcomes.",
        "- The output should be interpreted as an AI visibility benchmark, not as a consumer survey, sales performance report, or clinical evaluation.",
        "- Results should be re-run periodically to track whether content and visibility interventions improve AI recall.",
    ]

    if prompt_categories:
        notes.append("")
        notes.append("Query intent coverage included:")
        notes.extend(f"- {item}" for item in prompt_categories)

    return "\n".join(notes)


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
    tracked_competitors=None,
):
    is_quick_test_mode = run_mode == "Quick Test Mode"
    prompt_categories = prompt_categories or []
    brand_intelligence = brand_intelligence or {}
    if tracked_competitors is None and summary_df is not None and "brand" in summary_df.columns:
        tracked_competitors = [
            str(item)
            for item in summary_df["brand"].dropna().tolist()
            if str(item).strip().lower() != str(brand).strip().lower()
        ]
    context = OutputQualityContext(
        category=display_category or category,
        run_mode=run_mode,
        brand=display_brand or brand,
        market=display_market or market,
        audience=display_audience or audience,
        tracked_competitors=tracked_competitors,
    )

    recommendations = guard_generated_section_text(
        recommendations,
        context,
        "Strategic Priorities",
    )
    plan = guard_generated_section_text(
        plan,
        context,
        "AI Visibility Strategy Deep Dive",
    )
    geo_content_roadmap = guard_generated_section_text(
        geo_content_roadmap,
        context,
        "GEO Content Roadmap",
    )
    gap_analysis = guard_generated_section_text(
        gap_analysis,
        context,
        "Gap Analysis",
    )
    brand_win_explanation = guard_generated_section_text(
        brand_win_explanation,
        context,
        "AI Decision Explanation",
    )
    replacement_strategy = guard_generated_section_text(
        replacement_strategy,
        context,
        "Replacement Strategy",
    )
    if brand_intelligence:
        brand_intelligence = {
            key: (
                guard_generated_section_text(
                    value,
                    context,
                    f"Brand Intelligence {key}",
                )
                if isinstance(value, str)
                else value
            )
            for key, value in brand_intelligence.items()
        }

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
    summary_report_df = _normalize_markdown_table_headers(
        summary_report_df,
        {
            "brand": "Brand",
            "total_mentions": "Total Mentions",
            "average_visibility_score": "Average Visibility Score",
            "prompts_visible": "Prompts Visible",
            "share_of_voice_percent": "Share of Voice %",
        },
    )
    summary_report_md = df_to_markdown_table(summary_report_df, max_rows=15)
    trigger_report_md = df_to_markdown_table(
        _normalize_markdown_table_headers(
            detailed_pivot_df,
            {
                "prompt_category": "Query Type",
            },
        ),
        max_rows=25,
    )
    top_brands_report_md = (
        df_to_markdown_table(
            _normalize_markdown_table_headers(
                top_brands_df,
                {
                    "prompt_category": "Query Type",
                    "brand": "Brand",
                    "visibility_score": "Visibility Score",
                },
            ),
            max_rows=25,
        )
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
    metrics = get_target_metrics(summary_df, brand)
    top_competitors = get_top_competitors(summary_df, brand, limit=3)
    roadmap_df = create_roadmap_df(brand, category, top_competitors, metrics)
    roadmap_md = df_to_markdown_table(roadmap_df, max_rows=10)
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
    visibility_state_noun = get_visibility_state_noun(target_visibility_status)
    query_intent_md = "\n".join(
        f"- {item}" for item in prompt_categories
    ) or "_No query intent categories available._"
    report_audience_context = format_audience_market_context(
        display_audience,
        display_market,
    )
    visibility_gap_diagnosis = (
        f"{strategic_issue}\n\n"
        f"Competitive context:\n\n{top_competitor_text}"
    )
    geo_content_roadmap_body = None
    if geo_content_roadmap_done and geo_content_roadmap:
        geo_content_roadmap_body = (
            "> Strategic execution plan. Not part of visibility scoring or share of voice.\n\n"
            f"{geo_content_roadmap}"
        )

    recommended_next_step = (
        f"Build AI-citable content that connects {display_brand} with high-intent use cases, comparison queries, local intent, "
        f"decision-stage searches, and market-specific category queries for {display_category} in {display_market}. The next benchmark should track whether the brand "
        f"improves from its {visibility_state_noun} toward stronger inclusion in AI-generated recommendation lists."
    )

    parts = [
        f"# {display_brand} {display_market} AI Visibility Report",
        (
            "## 1. Report Overview\n\n"
            f"**Target Brand:** {display_brand}  \n"
            f"**Market:** {display_market}  \n"
            f"**Category:** {display_category}  \n"
            f"**Audience:** {display_audience}  \n"
            "**Report Type:** AI Visibility / Generative Engine Optimization Audit  \n"
            f"**Run Mode:** {run_mode}  \n"
            f"**Deliverable Status:** {deliverable_status}  \n\n"
            f'{"**TEST VERSION ONLY - Quick Test Mode. Not Client Deliverable.**" if is_quick_test_mode else ""}\n\n'
            f"This report evaluates how visible {display_brand} is in AI-generated {display_category} recommendations for {report_audience_context}.\n\n"
            "### Query Intent Coverage\n\n"
            "This benchmark covers the following AI recommendation contexts:\n\n"
            f"{query_intent_md}"
        ),
        (
            "## 2. Executive Summary\n\n"
            f"{executive_summary_sentence}\n\n"
            f"Key metrics for {display_brand}:\n\n"
            "| Metric | Value |\n"
            "|---|---:|\n"
            f"| Total Mentions | {target_mentions} |\n"
            f"| Average Visibility Score | {target_avg_score} |\n"
            f"| Prompts Visible | {target_prompts_visible} |\n"
            f"| Share of Voice | {target_sov}% |\n\n"
            "Top visible competitors in this benchmark:\n\n"
            f"{top_competitor_text}\n\n"
            f"{strategic_issue}"
        ),
        "## 3. Competitive Benchmark\n\n"
        "The table below summarizes brand-level AI visibility performance across all tested prompts.\n\n"
        f"{summary_report_md}",
        "## 4. Trigger-Level Visibility Findings\n\n"
        "The table below shows how each tracked brand performs across AI query categories.\n\n"
        f"{trigger_report_md}",
        "## 5. Top Brand Winners by Query Type\n\n"
        "The table below identifies which brand wins each query category based on visibility score.\n\n"
        f"{top_brands_report_md}",
        f"## 6. Visibility Gap Diagnosis\n\n{visibility_gap_diagnosis}",
        f"## 7. Strategic Priorities\n\n{recommendations}",
    ]

    if geo_content_roadmap_body:
        parts.append(f"## 8. GEO Content Roadmap\n\n{geo_content_roadmap_body}")
        roadmap_number = 9
        measurement_number = 10
        next_step_number = 11
        methodology_number = 12
    else:
        roadmap_number = 8
        measurement_number = 9
        next_step_number = 10
        methodology_number = 11

    parts.extend([
        f"## {roadmap_number}. 30 / 60 / 90 Day Roadmap\n\n{roadmap_md}",
        f"## {measurement_number}. Measurement Plan\n\n{_build_measurement_plan_md(metrics)}",
        f"## {next_step_number}. Recommended Next Step\n\n{recommended_next_step}",
        f"## {methodology_number}. Methodology Notes\n\n{_build_methodology_notes_md(display_category, prompt_categories)}",
    ])

    appendix_sections = []

    if brand_intelligence_done and brand_intelligence:
        appendix_sections.append(
            "## Appendix A: Brand Intelligence & Positioning Audit\n\n"
            "> Diagnostic insight. Tracked competitors are included in visibility scoring and share of voice. AI-discovered market signals are diagnostic references only and are not included in scoring unless selected as tracked competitors before the benchmark run.\n\n"
            "### Recommendation Drivers\n\n"
            f"{brand_intelligence['recommendation_drivers']}\n\n"
            "### AI-Inferred Target Brand Understanding\n\n"
            f"{brand_intelligence['target_brand_understanding']}\n\n"
            "### Positioning Gap Analysis\n\n"
            f"{brand_intelligence['positioning_gap_analysis']}"
        )

    if plan:
        appendix_sections.append(
            f"## Appendix B: AI Visibility Strategy Deep Dive\n\n{plan}"
        )

    if brand_win_explanation:
        appendix_sections.append(
            f"## Appendix C: AI Decision Explanation\n\n{brand_win_explanation}"
        )

    if replacement_strategy:
        appendix_sections.append(
            f"## Appendix D: Replacement Strategy\n\n{replacement_strategy}"
        )

    if gap_analysis:
        appendix_sections.append(
            f"## Appendix E: Gap Analysis\n\n{gap_analysis}"
        )

    final_report = "\n\n---\n\n".join(parts + appendix_sections)
    final_report = sanitize_report_text(final_report, context)
    validate_output_quality(
        final_report,
        context,
        content_type="final_markdown_report",
        strict=False,
    )
    return final_report
