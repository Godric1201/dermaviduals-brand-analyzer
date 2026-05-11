import streamlit as st

from geo_audit.analysis_pipeline import run_visibility_analysis
from geo_audit.brand_intelligence import run_brand_intelligence_analysis
from geo_audit.brand_understanding import run_brand_understanding_probe
from geo_audit.geo_roadmap import generate_geo_content_roadmap
from geo_audit.prompts import build_fixed_prompts
from geo_audit.run_progress import (
    build_progress_steps,
    format_progress_message,
    get_progress_mode_note,
)
from geo_audit.run_setup import build_analysis_context, normalize_context_text
from geo_audit.ui.api_usage_panel import coerce_api_usage_summary


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


def run_analysis_controller(
    *,
    target_brand,
    target_category,
    target_market,
    target_audience,
    display_brand,
    display_category,
    display_market,
    display_audience,
    answer_language,
    report_language,
    run_mode,
    prompt_limit,
    competitors,
    parsed_user_brand_strengths,
    show_prompt_debug,
    translations,
):
    brand = target_brand
    category = target_category
    market = target_market
    audience = target_audience
    language = answer_language
    is_full_report_mode = run_mode == "Full Report Mode"
    fixed_prompts = build_fixed_prompts(
        category=category,
        market=market,
        audience=audience
    )

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
                    f"{translations['running_prompt']} {index + 1}/{total_prompts}: {prompt_category}"
                ),
            )
        )
        progress_bar.progress(
            (2 + ((index + 1) / total_prompts)) / total_steps
        )

    st.session_state["analysis_running"] = True

    try:
        set_progress_phase(1)
        if is_full_report_mode:
            set_progress_phase(1, "Brand Understanding Probe")
            brand_understanding_result = run_brand_understanding_probe(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                report_language=report_language,
            )
            st.session_state["brand_understanding"] = brand_understanding_result
            st.session_state["brand_understanding_done"] = True
        else:
            st.session_state.pop("brand_understanding", None)
            st.session_state["brand_understanding_done"] = False

        set_progress_phase(2)

        with st.spinner(translations["running"]):
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
