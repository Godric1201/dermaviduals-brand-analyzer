import streamlit as st


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
