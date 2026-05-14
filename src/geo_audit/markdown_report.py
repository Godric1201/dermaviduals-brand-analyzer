from .ui_formatters import df_to_markdown_table
from .prompts import format_audience_market_context
from .output_quality import (
    OutputQualityContext,
    guard_generated_section_text,
    sanitize_narrative_appendix_text,
    sanitize_report_text,
    validate_output_quality,
)
from .brand_understanding import (
    STATUS_CLEAR,
    STATUS_MISALIGNED,
    STATUS_PARTIAL,
    STATUS_UNCLEAR,
    STATUS_NOT_ENOUGH_EVIDENCE,
)
from .market_relevance import (
    MARKET_LOCK_GLOBAL_DEFAULT_RISK,
    MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    MARKET_LOCK_MARKET_SPECIFIC,
    MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC,
)
from .markdown_report_helpers import (
    build_visible_market_fit_bullets,
    format_key_value_bullets,
    get_probe_field,
    normalize_markdown_table_headers,
)
from .markdown_visibility_report import _build_visibility_markdown_report
from .markdown_zero_visibility_report import _build_zero_visibility_markdown_report
from .report_diagnosis import (
    classify_visibility_state,
    get_target_visibility_metrics,
    is_zero_visibility,
    select_strategy_mode,
)


def _append_section(parts, title, body):
    if not body:
        return

    parts.append(f"## {title}\n\n{body.strip()}")


def _build_task_roadmap_cards_md(tasks):
    cards = []

    for index, row in enumerate(tasks, start=1):
        cards.append(
            f"**{index}. {row.get('Action', '')}**\n"
            f"- Gap addressed: {row.get('Gap Addressed', '')}\n"
            f"- Evidence type: {row.get('Evidence Type', '')}\n"
            f"- Why it matters: {row.get('Why It Matters', '')}\n"
            f"- Where it should live: {row.get('Where Evidence Should Live', '')}\n"
            f"- Validation: {row.get('Benchmark Validation Method', '')}\n"
            f"- Expected influence: {row.get('Expected Influence', '')}"
        )

    return "\n\n".join(cards)


def _build_brand_understanding_probe_md(brand_understanding, display_brand):
    if not brand_understanding:
        return ""

    brand_known_status = get_probe_field(
        brand_understanding,
        "brand_known_status",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    category_alignment = get_probe_field(
        brand_understanding,
        "category_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    market_alignment = get_probe_field(
        brand_understanding,
        "market_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    audience_alignment = get_probe_field(
        brand_understanding,
        "audience_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    recommended_interpretation = get_probe_field(
        brand_understanding,
        "recommended_interpretation",
        "Mixed diagnosis",
    )
    diagnosis_summary = get_probe_field(
        brand_understanding,
        "diagnosis_summary",
        "",
    )
    validation_note = get_probe_field(
        brand_understanding,
        "validation_note",
        "AI-inferred brand understanding probe. Validate before using as client-facing fact.",
    )
    misaligned_fields = [
        label
        for label, value in [
            ("category", category_alignment),
            ("market", market_alignment),
            ("audience", audience_alignment),
        ]
        if value == STATUS_MISALIGNED
    ]
    if len(misaligned_fields) == 1:
        misaligned_context = f"{misaligned_fields[0]} context"
    elif len(misaligned_fields) == 2:
        misaligned_context = (
            f"{misaligned_fields[0]} and {misaligned_fields[1]} contexts"
        )
    else:
        misaligned_context = (
            f"{', '.join(misaligned_fields[:-1])}, and {misaligned_fields[-1]} contexts"
            if misaligned_fields
            else ""
        )

    if misaligned_fields:
        interpretation = (
            "AI-inferred alignment signals suggest the non-visibility may reflect "
            f"an alignment problem in {misaligned_context}, not only a lack of evidence. "
            "This requires validation before being treated as fact."
        )
    elif brand_known_status in {STATUS_CLEAR, STATUS_PARTIAL}:
        interpretation = (
            f"The AI-inferred probe suggests {display_brand} appears to be recognized at least partially. "
            "Because the benchmark still recorded zero recommendation visibility, the issue appears more likely "
            "to involve recommendation retrieval, evidence depth, or market relevance than basic brand recognition. "
            "This requires validation."
        )
    elif brand_known_status in {STATUS_UNCLEAR, STATUS_NOT_ENOUGH_EVIDENCE}:
        interpretation = (
            "The AI-inferred probe did not provide enough confidence that the model understands the brand as a clear entity. "
            "Treat the zero-visibility result as a possible entity understanding gap until validated."
        )
    else:
        interpretation = (
            "The AI-inferred probe is inconclusive. Treat the visibility diagnosis as provisional and validate before acting on it."
        )

    probe_bullets = format_key_value_bullets([
        ("Brand understanding", brand_known_status),
        ("Category alignment", category_alignment),
        ("Market alignment", market_alignment),
        ("Audience alignment", audience_alignment),
        ("Recommended interpretation", recommended_interpretation),
    ])

    body = (
        "### Brand Understanding Probe\n\n"
        f"{interpretation}\n\n"
        f"{probe_bullets}"
    )

    if diagnosis_summary:
        body += f"\n\n**Probe summary:** {diagnosis_summary}"

    body += f"\n\n_{validation_note}_"

    return body


def _build_market_relevance_probe_md(market_relevance):
    if not market_relevance:
        return ""

    market_lock_status = get_probe_field(
        market_relevance,
        "market_lock_status",
        MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    )
    local_brand_presence_signal = get_probe_field(
        market_relevance,
        "local_brand_presence_signal",
        "Not Enough Evidence",
    )
    recommended_interpretation = get_probe_field(
        market_relevance,
        "recommended_interpretation",
        "Insufficient evidence",
    )
    global_default_risk_reason = get_probe_field(
        market_relevance,
        "global_default_risk_reason",
        "",
    )
    market_evidence_gap_summary = get_probe_field(
        market_relevance,
        "market_evidence_gap_summary",
        "",
    )
    validation_note = get_probe_field(
        market_relevance,
        "validation_note",
        "AI-inferred market relevance probe. Validate before using as client-facing fact.",
    )
    visible_market_fit = get_probe_field(
        market_relevance,
        "visible_market_fit",
        [],
    )

    if market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests the answer set appears to lean toward globally visible category leaders. "
            "This may indicate a market evidence gap, but it requires validation and is not a verified market fact."
        )
    elif market_lock_status == MARKET_LOCK_MARKET_SPECIFIC:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests visible brands appear to have market relevance. "
            "In this case, non-visibility is less likely to be only a global-default artifact, but this requires validation."
        )
    elif market_lock_status == MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests the answer set shows mixed market adherence. "
            "Some retrieved brands may fit the target market while others may reflect broader category visibility."
        )
    else:
        interpretation = (
            "The AI-inferred Market Relevance Probe cannot determine market lock confidently from the benchmark context. "
            "Treat this as insufficient evidence, not verified market fact."
        )

    probe_bullets = format_key_value_bullets([
        ("Market lock status", market_lock_status),
        ("Local brand presence", local_brand_presence_signal),
        ("Recommended interpretation", recommended_interpretation),
    ])
    body = (
        "### Market Relevance Probe\n\n"
        f"{interpretation}\n\n"
        f"{probe_bullets}"
    )

    if visible_market_fit:
        fit_bullets = build_visible_market_fit_bullets(visible_market_fit)
        if fit_bullets:
            body += (
                "\n\nVisible brand market-fit signals:\n\n"
                f"{fit_bullets}"
            )

    if global_default_risk_reason:
        body += f"\n\n**Global-default risk reason:** {global_default_risk_reason}"
    if market_evidence_gap_summary:
        body += f"\n\n**Market evidence gap summary:** {market_evidence_gap_summary}"

    body += f"\n\n_{validation_note}_"

    return body


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
    brand_understanding=None,
    brand_understanding_done=False,
    market_relevance=None,
    market_relevance_done=False,
    geo_content_roadmap=None,
    geo_content_roadmap_done=False,
    prompt_categories=None,
    tracked_competitors=None,
    source_evidence_payload=None,
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
    if plan:
        plan = sanitize_narrative_appendix_text(plan, context)
    if gap_analysis:
        gap_analysis = sanitize_narrative_appendix_text(gap_analysis, context)
    if brand_win_explanation:
        brand_win_explanation = sanitize_narrative_appendix_text(
            brand_win_explanation,
            context,
        )
    if replacement_strategy:
        replacement_strategy = sanitize_narrative_appendix_text(
            replacement_strategy,
            context,
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
    summary_report_df = normalize_markdown_table_headers(
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
        normalize_markdown_table_headers(
            detailed_pivot_df,
            {
                "prompt_category": "Query Type",
            },
        ),
        max_rows=25,
    )
    top_brands_report_md = (
        df_to_markdown_table(
            normalize_markdown_table_headers(
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

    target_metrics = get_target_visibility_metrics(summary_df, brand)
    target_mentions = target_metrics.total_mentions
    target_avg_score = target_metrics.average_visibility_score
    target_prompts_visible = target_metrics.prompts_visible
    target_sov = target_metrics.share_of_voice_percent
    report_audience_context = format_audience_market_context(
        display_audience,
        display_market,
    )

    if is_zero_visibility(target_metrics):
        parts = _build_zero_visibility_markdown_report(
            display_brand=display_brand,
            display_category=display_category,
            display_market=display_market,
            display_audience=display_audience,
            run_mode=run_mode,
            deliverable_status=deliverable_status,
            is_quick_test_mode=is_quick_test_mode,
            prompt_categories=prompt_categories,
            report_audience_context=report_audience_context,
            target_mentions=target_mentions,
            target_avg_score=target_avg_score,
            target_prompts_visible=target_prompts_visible,
            target_sov=target_sov,
            visibility_state=classify_visibility_state(target_metrics),
            strategy_mode=select_strategy_mode(target_metrics),
            summary_report_md=summary_report_md,
            trigger_report_md=trigger_report_md,
            top_brands_report_md=top_brands_report_md,
            summary_df=summary_df,
            top_brands_df=top_brands_df,
            detailed_pivot_df=detailed_pivot_df,
            brand=brand,
            brand_understanding=brand_understanding,
            brand_understanding_done=brand_understanding_done,
            market_relevance=market_relevance,
            market_relevance_done=market_relevance_done,
            source_evidence_payload=source_evidence_payload,
        )
        final_report = "\n\n---\n\n".join(parts)
        final_report = sanitize_report_text(final_report, context)
        validate_output_quality(
            final_report,
            context,
            content_type="final_markdown_report",
            strict=False,
        )
        return final_report

    parts = _build_visibility_markdown_report(
        brand=brand,
        display_brand=display_brand,
        category=category,
        display_category=display_category,
        display_market=display_market,
        display_audience=display_audience,
        run_mode=run_mode,
        deliverable_status=deliverable_status,
        is_quick_test_mode=is_quick_test_mode,
        prompt_categories=prompt_categories,
        report_audience_context=report_audience_context,
        target_mentions=target_mentions,
        target_avg_score=target_avg_score,
        target_prompts_visible=target_prompts_visible,
        target_sov=target_sov,
        summary_report_md=summary_report_md,
        trigger_report_md=trigger_report_md,
        top_brands_report_md=top_brands_report_md,
        summary_df=summary_df,
        recommendations=recommendations,
        plan=plan,
        gap_analysis=gap_analysis,
        brand_win_explanation=brand_win_explanation,
        replacement_strategy=replacement_strategy,
        brand_intelligence=brand_intelligence,
        brand_intelligence_done=brand_intelligence_done,
        geo_content_roadmap=geo_content_roadmap,
        geo_content_roadmap_done=geo_content_roadmap_done,
    )
    final_report = "\n\n---\n\n".join(parts)
    final_report = sanitize_report_text(final_report, context)
    validate_output_quality(
        final_report,
        context,
        content_type="final_markdown_report",
        strict=False,
    )
    return final_report
