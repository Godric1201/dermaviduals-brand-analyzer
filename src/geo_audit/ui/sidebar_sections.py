import streamlit as st


def render_sidebar_preset_loader(client_presets):
    st.sidebar.header("Analysis Setup")

    preset_options = ["Custom"] + list(client_presets)
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
            preset = client_presets[selected_preset]
            st.session_state["target_brand_input"] = preset["brand"]
            st.session_state["target_category_input"] = preset["category"]
            st.session_state["target_market_input"] = preset["market"]
            st.session_state["target_audience_input"] = preset["audience"]
            st.session_state["competitors_input"] = "\n".join(preset["competitors"])
            st.rerun()


def render_sidebar_base_inputs(
    brand_default,
    category_default,
    market_default,
    audience_default,
    competitors_default,
):
    target_brand = st.sidebar.text_input(
        "Target Brand",
        value=brand_default,
        key="target_brand_input"
    )
    target_category = st.sidebar.text_input(
        "Category",
        value=category_default,
        key="target_category_input"
    )
    target_market = st.sidebar.text_input(
        "Market",
        value=market_default,
        key="target_market_input"
    )
    target_audience = st.sidebar.text_area(
        "Audience",
        value=audience_default,
        key="target_audience_input"
    )
    competitors_text = st.sidebar.text_area(
        "Competitors",
        value="\n".join(competitors_default),
        help="Enter one competitor per line.",
        key="competitors_input"
    )

    return (
        target_brand,
        target_category,
        target_market,
        target_audience,
        competitors_text,
    )


def render_page_header(display_brand, display_market, display_category):
    st.title(f"{display_brand} {display_market} AI Visibility Analyzer")
    st.caption(
        f"AI visibility, competitor recall, and positioning gap analysis for {display_category}."
    )
    st.markdown(
        f"""
Benchmark how AI systems recall {display_brand}, compare competitor visibility, and surface positioning opportunities in {display_market}.
"""
    )


def render_advanced_developer_options():
    with st.sidebar.expander("Advanced / Developer Options"):
        show_prompt_debug = st.checkbox(
            "Show prompt debug details",
            value=False
        )

    return show_prompt_debug


def render_run_mode_controls():
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

    return run_mode, prompt_limit


def render_sidebar_validation_messages(validation_errors, validation_warnings):
    for error in validation_errors:
        st.sidebar.error(error)

    for warning in validation_warnings:
        st.sidebar.warning(warning)


def render_sidebar_run_buttons(t, validation_errors):
    review_button = st.sidebar.button(
        "Review & Run Analysis",
        disabled=bool(validation_errors)
    )
    reset_button = st.sidebar.button(t["reset"])

    if reset_button:
        st.session_state.clear()
        st.rerun()

    return review_button


def render_sidebar_methodology_info():
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


def render_sidebar_report_info():
    render_sidebar_methodology_info()

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


def render_run_confirmation_flow(
    review_button,
    display_brand,
    display_category,
    display_market,
    display_audience,
    run_mode,
    prompt_limit,
    parsed_user_brand_strengths,
    current_competitors,
    api_cost_estimate,
    api_call_estimate,
    brand_intelligence_estimated_calls,
    validation_errors,
    format_display_text_fn,
    clear_analysis_results_fn,
    run_analysis_fn,
):
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
                format_display_text_fn(competitor)
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
                    clear_analysis_results_fn()
                    run_analysis_fn()
                finally:
                    st.session_state["analysis_running"] = False

        if cancel_run:
            st.session_state["pending_run_confirmation"] = False
            st.rerun()
