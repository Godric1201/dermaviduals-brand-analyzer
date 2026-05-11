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
