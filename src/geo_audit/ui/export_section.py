import streamlit as st

from geo_audit.markdown_report import build_executive_markdown_report
from geo_audit.report_generator import create_executive_docx_report
from geo_audit.ui.export_builders import (
    build_docx_top_brands_display_df,
    build_markdown_top_brands_display_df,
)
from geo_audit.ui.exports import (
    render_benchmark_snapshot_export,
    render_report_download_exports,
)
from geo_audit.ui.source_evidence_panel import SOURCE_EVIDENCE_SESSION_KEY

def get_source_evidence_payload_for_markdown_export():
    """Return the validated source evidence payload stored by the preview panel."""

    return st.session_state.get(SOURCE_EVIDENCE_SESSION_KEY)

def build_source_evidence_export_status_message(source_evidence_payload) -> str:
    """Build a user-facing export status message for source evidence."""

    if source_evidence_payload:
        return (
            "Source evidence loaded. Markdown and DOCX exports will include the "
            "Source-Grounded Evidence Summary."
        )

    return (
        "No source evidence loaded. Markdown and DOCX exports will use benchmark "
        "signals only."
    )

def render_export_reports_section(
    t,
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
    detailed_df,
    raw_answer_df,
    pivot,
    top_brands,
    recommendations,
    plan,
    snapshot_brand_intelligence,
    prompt_categories,
    competitors,
    prompts,
    api_usage_summary,
    raw_answer_evidence_help,
    gap_analysis,
    brand_win_explanation,
    replacement_strategy,
    brand_intelligence,
    brand_intelligence_done,
    geo_content_roadmap,
    geo_content_roadmap_done,
    brand_understanding=None,
    brand_understanding_done=False,
    market_relevance=None,
    market_relevance_done=False,
):
    st.subheader(t["exports"])

    top_brands_display_df = build_markdown_top_brands_display_df(
        top_brands,
        brand,
        display_brand,
    )

    source_evidence_payload = get_source_evidence_payload_for_markdown_export()

    executive_report = build_executive_markdown_report(
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
        detailed_pivot_df=pivot.reset_index(),
        top_brands_df=top_brands_display_df,
        recommendations=recommendations,
        plan=plan,
        gap_analysis=gap_analysis,
        brand_win_explanation=brand_win_explanation,
        replacement_strategy=replacement_strategy,
        brand_intelligence=brand_intelligence,
        brand_intelligence_done=brand_intelligence_done,
        brand_understanding=brand_understanding,
        brand_understanding_done=brand_understanding_done,
        market_relevance=market_relevance,
        market_relevance_done=market_relevance_done,
        geo_content_roadmap=geo_content_roadmap,
        geo_content_roadmap_done=geo_content_roadmap_done,
        prompt_categories=prompt_categories,
        tracked_competitors=competitors,
        source_evidence_payload=source_evidence_payload,
    )
    executive_docx = create_executive_docx_report(
        brand=display_brand,
        market=display_market,
        category=display_category,
        audience=display_audience,
        summary_df=summary_display_df,
        top_brands_df=build_docx_top_brands_display_df(
            top_brands,
            brand,
            display_brand,
        ),
        recommendations=recommendations,
        strategy_report=plan,
        gap_analysis=gap_analysis or "",
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        brand_intelligence=snapshot_brand_intelligence,
        prompt_categories=prompt_categories,
           geo_content_roadmap=(
            geo_content_roadmap
            if geo_content_roadmap_done
            else None
        ),
        source_evidence_payload=source_evidence_payload,
    )

    render_report_download_exports(
        t=t,
        summary_df=summary_df,
        detailed_df=detailed_df,
        raw_answer_df=raw_answer_df,
        executive_report=executive_report,
        executive_docx=executive_docx,
        display_brand=display_brand,
        display_market=display_market,
        run_mode=run_mode,
    )
    render_benchmark_snapshot_export(
        display_brand=display_brand,
        display_market=display_market,
        display_category=display_category,
        display_audience=display_audience,
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        prompt_count=len(prompts),
        competitors=competitors,
        prompt_categories=prompt_categories,
        summary_df=summary_df,
        detailed_df=detailed_df,
        snapshot_brand_intelligence=snapshot_brand_intelligence,
        raw_answer_df=raw_answer_df,
        api_usage_summary=api_usage_summary,
        raw_answer_evidence_help=raw_answer_evidence_help,
    )
