from datetime import date
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
import pandas as pd

from geo_audit.app_constants import (
    ANSWER_LANGUAGE,
    AUDIENCE,
    BRAND,
    CATEGORY,
    CLIENT_PRESETS,
    MARKET,
    REPORT_LANGUAGE,
    TRANSLATIONS,
)
from geo_audit.analysis_pipeline import get_competitors, run_visibility_analysis
from geo_audit.api_cost_estimator import estimate_api_cost_range
from geo_audit.brand_intelligence import run_brand_intelligence_analysis
from geo_audit.brand_intelligence_prompts import (
    build_target_diagnostic_prompts,
    parse_user_brand_strengths,
)
from geo_audit.benchmark_snapshot import (
    build_benchmark_snapshot,
)
from geo_audit.competitor_suggestions import suggest_competitors_with_ai
from geo_audit.geo_roadmap import generate_geo_content_roadmap
from geo_audit.markdown_report import build_executive_markdown_report
from geo_audit.prompts import build_fixed_prompts
from geo_audit.run_progress import (
    build_progress_steps,
    format_progress_message,
    get_progress_mode_note,
)
from geo_audit.ui_formatters import (
    format_display_text,
    format_brand_names_for_display,
    replace_target_brand_for_display,
    translate_dataframe_columns,
)
from geo_audit.ui.api_usage_panel import (
    coerce_api_usage_summary,
    render_api_usage_summary,
)
from geo_audit.ui.benchmark_progress import render_benchmark_progress
from geo_audit.ui.brand_intelligence_panel import render_brand_intelligence_panel
from geo_audit.ui.charts import (
    render_benchmark_charts,
    render_prompt_level_chart,
)
from geo_audit.ui.content_generator_panel import render_content_generator_panel
from geo_audit.ui.export_builders import (
    build_docx_top_brands_display_df,
    build_markdown_top_brands_display_df,
)
from geo_audit.ui.exports import (
    render_benchmark_snapshot_export,
    render_report_download_exports,
)
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

from geo_audit.analyzer import DEFAULT_MODEL
from geo_audit.report_generator import (
    create_executive_docx_report,
)


st.set_page_config(
    page_title="AI Visibility Analyzer",
    layout="wide"
)

RAW_ANSWER_EVIDENCE_HELP = (
    "Raw answers are evidence logs for auditability. They may contain "
    "AI-generated content and should be reviewed before sharing externally."
)

ANALYSIS_OUTPUT_KEYS = [
    "competitors",
    "prompts",
    "ai_prompts",
    "detailed_df",
    "summary_df",
    "raw_answer_df",
    "raw_answers",
    "recommendations",
    "plan",
    "analysis_done",
    "analysis_context",
    "brand_win_explanation",
    "replacement_strategy",
    "gap_analysis",
    "content_pack",
    "strategy_report",
    "brand_intelligence",
    "brand_intelligence_done",
    "geo_content_roadmap",
    "geo_content_roadmap_done",
    "api_usage_summary",
]

def parse_competitors(text):
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def get_prompt_categories(prompts):
    categories = []
    seen = set()

    for item in prompts:
        if not isinstance(item, dict):
            continue

        category = normalize_context_text(item.get("category", ""))
        key = category.lower()

        if category and key not in seen:
            categories.append(category)
            seen.add(key)

    return categories


def build_competitor_suggestions_context(brand, category, market, audience):
    return {
        "brand": normalize_context_text(brand),
        "category": normalize_context_text(category),
        "market": normalize_context_text(market),
        "audience": normalize_context_text(audience),
    }


def get_competitor_suggestion_checkbox_key(index):
    return f"competitor_suggestion_selected_{index}"


def clear_competitor_suggestion_selections():
    for key in list(st.session_state):
        if key.startswith("competitor_suggestion_selected_"):
            st.session_state.pop(key, None)


def clear_competitor_suggestions():
    st.session_state.pop("competitor_suggestions", None)
    st.session_state.pop("competitor_suggestions_context", None)
    clear_competitor_suggestion_selections()


def add_selected_competitor_suggestions():
    suggestions = st.session_state.get("competitor_suggestions", [])
    existing_competitors = parse_competitors(
        st.session_state.get("competitors_input", "")
    )
    existing_keys = {
        competitor.lower()
        for competitor in existing_competitors
    }
    added_keys = set()
    additions = []

    for index, suggestion in enumerate(suggestions):
        selected = st.session_state.get(
            get_competitor_suggestion_checkbox_key(index),
            False
        )
        key = suggestion.lower()

        if selected and key not in existing_keys and key not in added_keys:
            additions.append(suggestion)
            added_keys.add(key)

    if additions:
        st.session_state["competitors_input"] = "\n".join(
            existing_competitors + additions
        )

    st.session_state["competitor_suggestions"] = [
        suggestion for suggestion in suggestions
        if suggestion.lower() not in added_keys
    ]
    clear_competitor_suggestion_selections()


def normalize_context_text(value):
    return " ".join(str(value).strip().split())


def normalize_competitors(competitors):
    return [
        normalized
        for normalized in [
            normalize_context_text(competitor)
            for competitor in competitors
        ]
        if normalized
    ]


def build_analysis_context(
    brand,
    category,
    market,
    audience,
    competitors,
    run_mode,
    prompt_limit,
    user_brand_strengths=None,
):
    return {
        "brand": normalize_context_text(brand),
        "category": normalize_context_text(category),
        "market": normalize_context_text(market),
        "audience": normalize_context_text(audience),
        "competitors": normalize_competitors(competitors),
        "run_mode": run_mode,
        "prompt_limit": prompt_limit,
        "user_brand_strengths": normalize_competitors(user_brand_strengths or []),
    }


def clear_analysis_results():
    for key in ANALYSIS_OUTPUT_KEYS:
        st.session_state.pop(key, None)


def validate_run_inputs(brand, category, market, audience, competitors):
    errors = []

    if not normalize_context_text(brand):
        errors.append("Target Brand is required.")
    if not normalize_context_text(category):
        errors.append("Category is required.")
    if not normalize_context_text(market):
        errors.append("Market is required.")
    if not normalize_context_text(audience):
        errors.append("Audience is required.")
    if not normalize_competitors(competitors):
        errors.append("At least one competitor is required.")

    return errors


def get_run_warnings(competitors, run_mode):
    warnings = []

    if (
        run_mode == "Full Report Mode"
        and len(normalize_competitors(competitors)) < 3
    ):
        warnings.append("Full Report Mode works best with at least 3 competitors.")

    return warnings


def estimate_api_calls(
    fixed_prompt_count,
    ai_generated_prompt_estimate,
    prompt_limit,
    run_mode,
    geo_content_roadmap_calls=1,
):
    estimated_total_prompts = (
        fixed_prompt_count + ai_generated_prompt_estimate
    )

    if run_mode == "Quick Test Mode" and prompt_limit is not None:
        effective_prompt_count = min(
            estimated_total_prompts,
            int(prompt_limit)
        )
    else:
        effective_prompt_count = estimated_total_prompts

    prompt_generation_calls = 1
    ai_answer_generation_calls = effective_prompt_count
    recommendation_calls = 1
    strategy_report_calls = 1

    return {
        "fixed_prompt_count": fixed_prompt_count,
        "ai_generated_prompt_estimate": ai_generated_prompt_estimate,
        "estimated_total_prompts": estimated_total_prompts,
        "effective_prompt_count": effective_prompt_count,
        "prompt_generation_calls": prompt_generation_calls,
        "ai_answer_generation_calls": ai_answer_generation_calls,
        "recommendation_calls": recommendation_calls,
        "strategy_report_calls": strategy_report_calls,
        "geo_content_roadmap_calls": geo_content_roadmap_calls,
        "estimated_pipeline_calls": (
            prompt_generation_calls
            + ai_answer_generation_calls
            + recommendation_calls
            + strategy_report_calls
            + geo_content_roadmap_calls
        ),
        "auto_result_narrative_calls_estimate": 3,
    }


def estimate_total_ai_calls(api_call_estimate, brand_intelligence_calls):
    return (
        api_call_estimate["estimated_pipeline_calls"]
        + brand_intelligence_calls
        + api_call_estimate["auto_result_narrative_calls_estimate"]
    )


def run_analysis():
    brand = target_brand
    category = target_category
    market = target_market
    audience = target_audience
    language = ANSWER_LANGUAGE
    report_language = REPORT_LANGUAGE
    fixed_prompts = build_fixed_prompts(
        category=category,
        market=market,
        audience=audience
    )

    default_competitors = get_competitors()
    competitors = parse_competitors(competitors_text)
    if not competitors:
        competitors = default_competitors

    st.subheader("Generating AI Visibility Report")
    progress_steps = build_progress_steps(run_mode)
    total_steps = len(progress_steps)

    ai_prompts_placeholder = None
    if show_prompt_debug:
        with st.expander("AI Generated Prompts Debug", expanded=False):
            ai_prompts_placeholder = st.empty()

    total_prompts_placeholder = st.empty()

    progress_bar = st.progress(0)
    status_text = st.empty()
    note_text = st.empty()
    note_text.info(get_progress_mode_note(run_mode))

    def set_progress_phase(step_number, label_suffix=""):
        label = progress_steps[step_number - 1]
        if label_suffix:
            label = f"{label} — {label_suffix}"
        status_text.write(
            format_progress_message(step_number, total_steps, label)
        )
        progress_bar.progress(step_number / total_steps)

    def on_progress(index, total_prompts, prompt_category):
        status_text.write(
            format_progress_message(
                3,
                total_steps,
                (
                    f"{progress_steps[2]} — "
                    f"{TRANSLATIONS['running_prompt']} {index + 1}/{total_prompts}: {prompt_category}"
                ),
            )
        )
        progress_bar.progress(
            (2 + ((index + 1) / total_prompts)) / total_steps
        )

    st.session_state["analysis_running"] = True

    try:
        set_progress_phase(1)
        set_progress_phase(2)

        with st.spinner(TRANSLATIONS["running"]):
            result = run_visibility_analysis(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                answer_language=language,
                report_language=report_language,
                fixed_prompts=fixed_prompts,
                on_progress=on_progress,
                prompt_limit=prompt_limit,
                competitors=competitors,
                run_mode=run_mode,
            )

        set_progress_phase(4)

        ai_prompts = result["ai_prompts"]
        prompts = result["prompts"]

        if show_prompt_debug and ai_prompts_placeholder is not None:
            ai_prompts_placeholder.write(ai_prompts)
        total_prompts_placeholder.write(f"Total prompts: {len(prompts)}")

        st.session_state["competitors"] = result["competitors"]
        st.session_state["prompts"] = result["prompts"]
        st.session_state["ai_prompts"] = result["ai_prompts"]
        st.session_state["detailed_df"] = result["detailed_df"]
        st.session_state["summary_df"] = result["summary_df"]
        st.session_state["raw_answer_df"] = result["raw_answer_df"]
        st.session_state["raw_answers"] = result["raw_answers"]
        st.session_state["recommendations"] = result["recommendations"]
        st.session_state["plan"] = result["plan"]
        st.session_state["api_usage_summary"] = coerce_api_usage_summary(
            result.get("api_usage_summary")
        )
        st.session_state["brand"] = brand
        st.session_state["category"] = category
        st.session_state["market"] = market
        st.session_state["audience"] = audience
        st.session_state["display_brand"] = display_brand
        st.session_state["display_category"] = display_category
        st.session_state["display_market"] = display_market
        st.session_state["display_audience"] = display_audience
        st.session_state["run_mode"] = run_mode
        st.session_state["prompt_limit"] = prompt_limit

        set_progress_phase(5)
        with st.spinner("Running Brand Intelligence diagnostics..."):
            brand_intelligence_result = run_brand_intelligence_analysis(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                competitors=competitors,
                raw_answers=result["raw_answers"],
                summary_df=result["summary_df"],
                detailed_df=result["detailed_df"],
                user_brand_strengths=parsed_user_brand_strengths,
                answer_language=language,
                report_language=report_language,
                on_progress=lambda step: status_text.write(
                    format_progress_message(
                        5,
                        total_steps,
                        (
                            f"{progress_steps[4]} — "
                            f"{step.replace('_', ' ').title()}"
                        ),
                    )
                ),
            )
        st.session_state["brand_intelligence"] = brand_intelligence_result
        st.session_state["brand_intelligence_done"] = True

        set_progress_phase(6)
        with st.spinner("Generating GEO Content Roadmap..."):
            status_text.write(
                format_progress_message(
                    6,
                    total_steps,
                    f"{progress_steps[5]} — Building execution plan",
                )
            )
            geo_content_roadmap = generate_geo_content_roadmap(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                competitors=competitors,
                summary_df=result["summary_df"],
                detailed_df=result["detailed_df"],
                brand_intelligence=brand_intelligence_result,
                query_intent_categories=get_prompt_categories(result["prompts"]),
                report_language=report_language,
            )
        st.session_state["geo_content_roadmap"] = geo_content_roadmap
        st.session_state["geo_content_roadmap_done"] = True

        set_progress_phase(7)
        st.session_state["analysis_context"] = build_analysis_context(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            competitors=competitors,
            run_mode=run_mode,
            prompt_limit=prompt_limit,
            user_brand_strengths=parsed_user_brand_strengths,
        )
        st.session_state["analysis_done"] = True

        set_progress_phase(8)
    finally:
        st.session_state["analysis_running"] = False
        progress_bar.empty()
        status_text.empty()
        note_text.empty()


def display_results():
    t = TRANSLATIONS
    brand = st.session_state.get("brand", BRAND)
    category = st.session_state.get("category", CATEGORY)
    market = st.session_state.get("market", MARKET)
    audience = st.session_state.get("audience", AUDIENCE)
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
    st.subheader(t["exports"])

    top_brands_display_df = build_markdown_top_brands_display_df(
        top_brands,
        brand,
        display_brand,
    )

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
        gap_analysis=st.session_state.get("gap_analysis"),
        brand_win_explanation=st.session_state.get("brand_win_explanation"),
        replacement_strategy=st.session_state.get("replacement_strategy"),
        brand_intelligence=st.session_state.get("brand_intelligence"),
        brand_intelligence_done=st.session_state.get("brand_intelligence_done", False),
        geo_content_roadmap=st.session_state.get("geo_content_roadmap"),
        geo_content_roadmap_done=st.session_state.get("geo_content_roadmap_done", False),
        prompt_categories=prompt_categories,
        tracked_competitors=competitors,
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
        gap_analysis=st.session_state.get("gap_analysis", ""),
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        brand_intelligence=snapshot_brand_intelligence,
        prompt_categories=prompt_categories,
        geo_content_roadmap=(
            st.session_state.get("geo_content_roadmap")
            if st.session_state.get("geo_content_roadmap_done", False)
            else None
        )
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
        raw_answer_evidence_help=RAW_ANSWER_EVIDENCE_HELP,
    )

# =========================
# Main UI
# =========================

t = TRANSLATIONS

st.sidebar.header("Analysis Setup")

preset_options = ["Custom"] + list(CLIENT_PRESETS)
selected_preset = st.sidebar.selectbox(
    "Client Preset",
    preset_options,
    index=0
)

load_preset = st.sidebar.button("Load Preset")

if load_preset:
    if selected_preset == "Custom":
        st.sidebar.info("Select a preset to load.")
    else:
        preset = CLIENT_PRESETS[selected_preset]
        st.session_state["target_brand_input"] = preset["brand"]
        st.session_state["target_category_input"] = preset["category"]
        st.session_state["target_market_input"] = preset["market"]
        st.session_state["target_audience_input"] = preset["audience"]
        st.session_state["competitors_input"] = "\n".join(preset["competitors"])
        st.rerun()

target_brand = st.sidebar.text_input(
    "Target Brand",
    value=BRAND,
    key="target_brand_input"
)
target_category = st.sidebar.text_input(
    "Category",
    value=CATEGORY,
    key="target_category_input"
)
target_market = st.sidebar.text_input(
    "Market",
    value=MARKET,
    key="target_market_input"
)
target_audience = st.sidebar.text_area(
    "Audience",
    value=AUDIENCE,
    key="target_audience_input"
)
competitors_text = st.sidebar.text_area(
    "Competitors",
    value="\n".join(get_competitors()),
    help="Enter one competitor per line.",
    key="competitors_input"
)
parsed_competitors = parse_competitors(competitors_text)
configured_competitors = parsed_competitors if parsed_competitors else get_competitors()
st.sidebar.caption(f"Configured competitors: {len(configured_competitors)}")

competitor_suggestions_context = build_competitor_suggestions_context(
    target_brand,
    target_category,
    target_market,
    target_audience,
)
stored_suggestions_context = st.session_state.get(
    "competitor_suggestions_context"
)

if (
    stored_suggestions_context
    and stored_suggestions_context != competitor_suggestions_context
):
    clear_competitor_suggestions()

required_competitor_context_exists = all(
    competitor_suggestions_context.values()
)

st.sidebar.markdown("**Competitor Discovery**")
find_competitors = st.sidebar.button(
    "Find AI-suggested competitors",
    disabled=not required_competitor_context_exists
)

if find_competitors:
    with st.spinner("Finding relevant competitors..."):
        suggestions = suggest_competitors_with_ai(
            brand=target_brand,
            category=target_category,
            market=target_market,
            audience=target_audience,
            existing_competitors=parsed_competitors,
            max_suggestions=8,
            answer_language=ANSWER_LANGUAGE,
        )

    st.session_state["competitor_suggestions"] = suggestions
    st.session_state["competitor_suggestions_context"] = (
        competitor_suggestions_context
    )
    clear_competitor_suggestion_selections()

suggestions = st.session_state.get("competitor_suggestions", [])
if suggestions:
    for index, suggestion in enumerate(suggestions):
        st.sidebar.checkbox(
            suggestion,
            key=get_competitor_suggestion_checkbox_key(index)
        )

    st.sidebar.button(
        "Add selected competitors",
        on_click=add_selected_competitor_suggestions
    )
elif find_competitors:
    st.sidebar.info("No new competitor suggestions found.")

brand_strengths_text = st.sidebar.text_area(
    "Brand Strengths / Positioning Notes",
    help=(
        "Optional. Enter one strength, proof point, or positioning note per line. "
        "These notes are not used for visibility scoring."
    ),
    key="brand_strengths_input"
)
display_brand = format_display_text(target_brand)
display_category = format_display_text(target_category)
display_market = format_display_text(target_market)
display_audience = format_display_text(target_audience)

parsed_user_brand_strengths = parse_user_brand_strengths(brand_strengths_text)
if parsed_user_brand_strengths:
    st.sidebar.caption(f"Brand strengths / notes: {len(parsed_user_brand_strengths)}")
    st.sidebar.write(parsed_user_brand_strengths)

st.sidebar.write("**Prompt Mode:** Fixed + AI Generated")

with st.sidebar.expander("Advanced / Developer Options"):
    show_prompt_debug = st.checkbox(
        "Show prompt debug details",
        value=False
    )

st.title(f"{display_brand} {display_market} AI Visibility Analyzer")
st.caption(
    f"AI visibility, competitor recall, and positioning gap analysis for {display_category}."
)
st.markdown(
    f"""
Benchmark how AI systems recall {display_brand}, compare competitor visibility, and surface positioning opportunities in {display_market}.
"""
)

run_mode = st.sidebar.radio(
    "Run Mode",
    ["Full Report Mode", "Quick Test Mode"],
    index=0
)

prompt_limit = None
if run_mode == "Quick Test Mode":
    prompt_limit = st.sidebar.number_input(
        "Prompt Limit",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

current_competitors = configured_competitors
current_analysis_context = build_analysis_context(
    brand=target_brand,
    category=target_category,
    market=target_market,
    audience=target_audience,
    competitors=current_competitors,
    run_mode=run_mode,
    prompt_limit=prompt_limit,
    user_brand_strengths=parsed_user_brand_strengths,
)

validation_errors = validate_run_inputs(
    brand=target_brand,
    category=target_category,
    market=target_market,
    audience=target_audience,
    competitors=current_competitors
)
validation_warnings = get_run_warnings(
    competitors=current_competitors,
    run_mode=run_mode
)
fixed_prompt_count = len(build_fixed_prompts(
    category=target_category,
    market=target_market,
    audience=target_audience
))
api_call_estimate = estimate_api_calls(
    fixed_prompt_count=fixed_prompt_count,
    ai_generated_prompt_estimate=10,
    prompt_limit=prompt_limit,
    run_mode=run_mode
)
brand_intelligence_estimated_calls = len(build_target_diagnostic_prompts(
    brand=target_brand,
    category=target_category,
    market=target_market,
    audience=target_audience,
    competitors=current_competitors,
    user_brand_strengths=parsed_user_brand_strengths,
)) + 3
estimated_total_ai_calls = estimate_total_ai_calls(
    api_call_estimate,
    brand_intelligence_estimated_calls,
)
api_cost_estimate = estimate_api_cost_range(
    estimated_total_ai_calls,
    DEFAULT_MODEL,
)

for error in validation_errors:
    st.sidebar.error(error)

for warning in validation_warnings:
    st.sidebar.warning(warning)

review_button = st.sidebar.button(
    "Review & Run Analysis",
    disabled=bool(validation_errors)
)
reset_button = st.sidebar.button(t["reset"])

if reset_button:
    st.session_state.clear()
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("""
### What This Analysis Measures

- Brand mentions
- First appearance position
- Estimated ranking inside AI answers
- Visibility score
- Organic visibility
- Share of voice
- Competitor benchmark
- GEO recommendations
- Level 3 action plan
""")

st.sidebar.markdown("""
### Report Sections

1. Executive Snapshot  
2. Prompt Matrix  
3. Competitor Benchmark  
4. Trigger-Level Heatmap  
5. Top Brand Winners  
6. AI Decision Explanation  
7. Replacement Strategy  
8. Strategic Insight  
9. Export Reports  
""")

with st.expander("How the scoring works"):
    st.markdown("""
Visibility scoring uses three signals from AI answers:

1. Brand mentions
2. First appearance position
3. Estimated rank

Visibility and share of voice are calculated from discovery prompts only.
""")

if review_button:
    st.session_state["pending_run_confirmation"] = True

if st.session_state.get("pending_run_confirmation", False):
    confirmation_panel = st.empty()

    with confirmation_panel.container():
        st.info("Confirm this setup before generating the report. This may call the OpenAI API.")
        st.subheader("Review Analysis Setup")
        st.write(f"**Target Brand:** {display_brand}")
        st.write(f"**Category:** {display_category}")
        st.write(f"**Market:** {display_market}")
        st.write(f"**Audience:** {display_audience}")
        st.write(f"**Run Mode:** {run_mode}")
        st.write("**Brand Intelligence:** Included")

        if run_mode == "Quick Test Mode":
            st.write(f"**Prompt Limit:** {prompt_limit}")

        if parsed_user_brand_strengths:
            st.write("**Brand Strengths / Positioning Notes:**")
            st.write(parsed_user_brand_strengths)

        display_competitors = [
            format_display_text(competitor)
            for competitor in current_competitors
        ]
        st.write(f"**Competitors:** {len(display_competitors)}")
        st.write(display_competitors)

        st.markdown("**Approximate API Usage Estimate**")
        st.write(
            f"**Estimated AI calls:** ~{api_cost_estimate['estimated_calls']}"
        )
        if api_cost_estimate["pricing_available"]:
            st.write(
                "**Estimated API cost:** "
                f"{api_cost_estimate['formatted_cost_range']}"
            )
            st.write(
                "**Pricing assumption:** "
                f"{api_cost_estimate['pricing_label']}"
            )
        else:
            st.write(
                "Cost estimate unavailable for this configured model. "
                "Check current OpenAI API pricing."
            )
        st.caption(
            "Actual billing may vary by model, prompt length, output length, "
            "and current OpenAI pricing."
        )

        with st.expander("View API call breakdown", expanded=False):
            st.write(
                "**Effective prompts to run:** "
                f"{api_call_estimate['effective_prompt_count']}"
            )
            st.write(
                "**Estimated initial API calls:** "
                f"{api_call_estimate['estimated_pipeline_calls']}"
            )
            st.write(
                "**Brand Intelligence calls:** "
                f"{brand_intelligence_estimated_calls}"
            )
            st.write(
                "**GEO Content Roadmap call:** "
                f"{api_call_estimate['geo_content_roadmap_calls']}"
            )
            st.write(
                "**Additional narrative calls:** up to "
                f"{api_call_estimate['auto_result_narrative_calls_estimate']}"
            )
            st.write(f"**Fixed prompts:** {api_call_estimate['fixed_prompt_count']}")
            st.write(
                "**AI-generated prompts estimate:** "
                f"{api_call_estimate['ai_generated_prompt_estimate']}"
            )
            st.write(
                "**AI answer generation calls:** "
                f"{api_call_estimate['ai_answer_generation_calls']}"
            )
            st.write(
                "**Prompt generation call:** "
                f"{api_call_estimate['prompt_generation_calls']}"
            )
            st.write(
                "**Recommendation call:** "
                f"{api_call_estimate['recommendation_calls']}"
            )
            st.write(
                "**Strategy report call:** "
                f"{api_call_estimate['strategy_report_calls']}"
            )
            st.write(
                "**GEO Content Roadmap call:** "
                f"{api_call_estimate['geo_content_roadmap_calls']}"
            )
            st.caption(
                "Content Asset Generator calls are excluded until the user explicitly "
                "generates a content pack."
            )

        col_confirm, col_cancel = st.columns(2)

        with col_confirm:
            confirm_run = st.button("Confirm & Run")

        with col_cancel:
            cancel_run = st.button("Cancel")

    if confirm_run:
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            st.session_state["pending_run_confirmation"] = False
            confirmation_panel.empty()
            st.session_state["analysis_running"] = True
            try:
                clear_analysis_results()
                run_analysis()
            finally:
                st.session_state["analysis_running"] = False

    if cancel_run:
        st.session_state["pending_run_confirmation"] = False
        st.rerun()

if st.session_state.get("analysis_done", False):
    display_results()
