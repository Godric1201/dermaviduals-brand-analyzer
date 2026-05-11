from datetime import date

import streamlit as st

from geo_audit.benchmark_snapshot import build_benchmark_snapshot
from geo_audit.ui_formatters import (
    format_display_text,
    format_brand_names_for_display,
    replace_target_brand_for_display,
)
from geo_audit.ui.api_usage_panel import (
    coerce_api_usage_summary,
    render_api_usage_summary,
)
from geo_audit.ui.analysis_controller import get_prompt_categories
from geo_audit.ui.benchmark_progress import render_benchmark_progress
from geo_audit.ui.brand_intelligence_panel import render_brand_intelligence_panel
from geo_audit.ui.charts import (
    render_benchmark_charts,
    render_prompt_level_chart,
)
from geo_audit.ui.content_generator_panel import render_content_generator_panel
from geo_audit.ui.export_section import render_export_reports_section
from geo_audit.ui.raw_answers_panel import render_raw_answers_panel
from geo_audit.ui.narrative_sections import (
    render_ai_association_gap,
    render_brand_winners_explanation,
    render_replacement_strategy,
)
from geo_audit.ui.results_sections import (
    render_action_plan,
    render_competitive_benchmark,
    render_executive_snapshot,
    render_geo_content_roadmap,
    render_geo_recommendations,
    render_prompt_level_results,
    render_prompt_matrix,
    render_query_intent_coverage,
    render_run_input_summary,
    render_run_status_messages,
    render_top_brands_by_query_type,
    render_trigger_level_visibility,
)


def display_results_controller(
    *,
    current_analysis_context,
    show_prompt_debug,
    translations,
    default_brand,
    default_category,
    default_market,
    default_audience,
    raw_answer_evidence_help,
):
    t = translations
    brand = st.session_state.get("brand", default_brand)
    category = st.session_state.get("category", default_category)
    market = st.session_state.get("market", default_market)
    audience = st.session_state.get("audience", default_audience)
    display_brand = st.session_state.get("display_brand", format_display_text(brand))
    display_category = st.session_state.get("display_category", format_display_text(category))
    display_market = st.session_state.get("display_market", format_display_text(market))
    display_audience = st.session_state.get("display_audience", format_display_text(audience))

    competitors = st.session_state["competitors"]
    prompts = st.session_state["prompts"]
    ai_prompts = st.session_state["ai_prompts"]
    detailed_df = st.session_state["detailed_df"]
    summary_df = st.session_state["summary_df"]
    raw_answer_df = st.session_state["raw_answer_df"]
    raw_answers = st.session_state["raw_answers"]
    recommendations = st.session_state["recommendations"]
    plan = st.session_state["plan"]
    api_usage_summary = coerce_api_usage_summary(
        st.session_state.get("api_usage_summary")
    )
    summary_display_df = replace_target_brand_for_display(
        format_brand_names_for_display(summary_df),
        raw_brand=brand,
        display_brand=display_brand
    )
    detailed_display_df = replace_target_brand_for_display(
        format_brand_names_for_display(detailed_df),
        raw_brand=brand,
        display_brand=display_brand
    )
    run_mode = st.session_state.get("run_mode", "Full Report Mode")
    prompt_limit = st.session_state.get("prompt_limit")
    prompt_categories = get_prompt_categories(prompts)
    is_quick_test_mode = run_mode == "Quick Test Mode"
    deliverable_status = "Client-deliverable full report"

    if is_quick_test_mode:
        deliverable_status = (
            "Development-only limited-prompt output. Not client-deliverable."
        )

    stored_context = st.session_state.get("analysis_context")
    render_run_status_messages(
        t=t,
        stored_context=stored_context,
        current_analysis_context=current_analysis_context,
        is_quick_test_mode=is_quick_test_mode,
        prompt_limit=prompt_limit,
    )

    render_run_input_summary(
        competitors=competitors,
        prompts=prompts,
        show_prompt_debug=show_prompt_debug,
        ai_prompts=ai_prompts,
    )

    render_api_usage_summary(api_usage_summary)

    render_query_intent_coverage(prompt_categories)

    # =========================
    # 1. Executive Snapshot
    # =========================
    render_executive_snapshot(
        t=t,
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand=brand,
        prompt_count=len(prompts),
    )

    # =========================
    # 2. Prompts
    # =========================
    render_prompt_matrix(prompts)

    # =========================
    # 3. Competitor Benchmark
    # =========================
    render_competitive_benchmark(t, summary_display_df)

    # =========================
    # 4. Trigger-Level Visibility
    # =========================
    pivot = render_trigger_level_visibility(detailed_df)

    # =========================
    # 5. Top Brands per Query Type
    # =========================
    top_brands = render_top_brands_by_query_type(
        detailed_df=detailed_df,
        brand=brand,
        display_brand=display_brand,
    )

    # =========================
    # 6. Why These Brands Win
    # =========================
    render_brand_winners_explanation(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        run_mode=run_mode,
        top_brands=top_brands,
        detailed_df=detailed_df,
    )

    # =========================
    # 7. How Target Brand Can Replace Winners
    # =========================
    render_replacement_strategy(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        run_mode=run_mode,
        top_brands=top_brands,
        summary_df=summary_df,
        detailed_df=detailed_df,
        raw_answers=raw_answers,
    )

    # =========================
    # 8. Benchmark Charts
    # =========================
    render_benchmark_charts(t, summary_df)

    # =========================
    # 9. Prompt-Level Results
    # =========================
    render_prompt_level_results(t, detailed_display_df)

    render_prompt_level_chart(t, detailed_df)

    # =========================
    # 10. Raw Answers
    # =========================
    render_raw_answers_panel(raw_answers)

    # =========================
    # 11. GEO Recommendations
    # =========================
    render_geo_recommendations(t, recommendations)

    # =========================
    # 12. AI Association Gap
    # =========================
    render_ai_association_gap(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        run_mode=run_mode,
        summary_df=summary_df,
        detailed_df=detailed_df,
    )

    if st.session_state.get("brand_intelligence_done", False):
        brand_intelligence = st.session_state["brand_intelligence"]

        render_brand_intelligence_panel(brand_intelligence)

    render_geo_content_roadmap(
        st.session_state.get("geo_content_roadmap_done", False),
        st.session_state.get("geo_content_roadmap"),
    )

    # =========================
    # 13. Level 3 Strategic Insight
    # =========================
    render_action_plan(t, plan)

    # =========================
    # 14. Level 2 Content Pack
    # =========================
    render_content_generator_panel(
        t=t,
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        summary_df=summary_df,
        detailed_df=detailed_df,
    )

    snapshot_brand_intelligence = None
    if st.session_state.get("brand_intelligence_done", False):
        snapshot_brand_intelligence = st.session_state.get("brand_intelligence")

    current_snapshot = build_benchmark_snapshot(
        brand=display_brand,
        market=display_market,
        category=display_category,
        audience=display_audience,
        report_date=date.today().isoformat(),
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        prompt_count=len(prompts),
        competitors=competitors,
        query_intent_categories=prompt_categories,
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence=snapshot_brand_intelligence,
        include_raw_answers=False,
        raw_answer_df=raw_answer_df,
        api_usage_summary=api_usage_summary,
    )

    # =========================
    # 15. Benchmark Progress
    # =========================
    render_benchmark_progress(current_snapshot)

    # =========================
    # 16. Export Reports
    # =========================
    render_export_reports_section(
        t=t,
        brand=brand,
        display_brand=display_brand,
        category=category,
        display_category=display_category,
        market=market,
        display_market=display_market,
        audience=audience,
        display_audience=display_audience,
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        deliverable_status=deliverable_status,
        summary_df=summary_df,
        summary_display_df=summary_display_df,
        detailed_df=detailed_df,
        raw_answer_df=raw_answer_df,
        pivot=pivot,
        top_brands=top_brands,
        recommendations=recommendations,
        gap_analysis=st.session_state.get("gap_analysis"),
        plan=plan,
        snapshot_brand_intelligence=snapshot_brand_intelligence,
        prompt_categories=prompt_categories,
        competitors=competitors,
        prompts=prompts,
        api_usage_summary=api_usage_summary,
        raw_answer_evidence_help=raw_answer_evidence_help,
        brand_win_explanation=st.session_state.get("brand_win_explanation"),
        replacement_strategy=st.session_state.get("replacement_strategy"),
        brand_intelligence=st.session_state.get("brand_intelligence"),
        brand_intelligence_done=st.session_state.get("brand_intelligence_done", False),
        geo_content_roadmap=st.session_state.get("geo_content_roadmap"),
        geo_content_roadmap_done=st.session_state.get("geo_content_roadmap_done", False),
        brand_understanding=st.session_state.get("brand_understanding"),
        brand_understanding_done=st.session_state.get("brand_understanding_done", False),
        market_relevance=st.session_state.get("market_relevance"),
        market_relevance_done=st.session_state.get("market_relevance_done", False),
    )
