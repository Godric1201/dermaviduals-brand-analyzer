import streamlit as st


def render_query_intent_coverage(prompt_categories):
    st.subheader("Query Intent Coverage")
    st.caption(
        "This benchmark covers multiple AI recommendation contexts, not only generic best-brand queries."
    )
    st.write(prompt_categories)
