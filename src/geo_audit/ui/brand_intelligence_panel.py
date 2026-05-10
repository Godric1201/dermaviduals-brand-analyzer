import streamlit as st


def render_brand_intelligence_panel(brand_intelligence):
    st.subheader("Brand Intelligence & Positioning Audit")
    st.info(
        "Diagnostic insight. Not part of visibility scoring. "
        "Tracked competitors are included in visibility scoring and share of voice. "
        "Other brands mentioned here may be AI-discovered market signals and are not included in scoring unless added as tracked competitors."
    )

    with st.expander("Recommendation Drivers", expanded=False):
        st.write(brand_intelligence["recommendation_drivers"])

    with st.expander("AI-Inferred Target Brand Understanding", expanded=False):
        st.write(brand_intelligence["target_brand_understanding"])

    with st.expander("Positioning Gap Analysis", expanded=False):
        st.write(brand_intelligence["positioning_gap_analysis"])

    with st.expander("Diagnostic Prompts / Answers", expanded=False):
        st.caption(brand_intelligence["validation_note"])
        for item in brand_intelligence["diagnostic_answers"]:
            st.markdown(f"**{item['category']}**")
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.write(item["answer"])
