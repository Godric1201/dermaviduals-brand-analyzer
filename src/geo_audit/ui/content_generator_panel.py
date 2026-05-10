import streamlit as st

from geo_audit.app_constants import REPORT_LANGUAGE
from geo_audit.content_generator import generate_level_2_content_pack


def render_content_generator_panel(
    t,
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
):
    st.subheader(t["level_2"])
    st.caption(t["level_2_caption"])

    if st.button(t["generate_level_2"]):
        with st.spinner(t["generating_level_2"]):
            content_pack = generate_level_2_content_pack(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                competitors=competitors,
                summary_table=summary_df.to_string(index=False),
                detailed_table=detailed_df.head(40).to_string(index=False),
                report_language=REPORT_LANGUAGE
            )

        st.success(t["level_2_done"])

        with st.expander(t["seo_blog"]):
            st.write(content_pack["seo_blog"])

        with st.expander(t["review_strategy"]):
            st.write(content_pack["review_strategy"])

        with st.expander(t["social_posts"]):
            st.write(content_pack["social_posts"])

        with st.expander(t["faq_content"]):
            st.write(content_pack["faq_content"])

        with st.expander(t["comparison_outline"]):
            st.write(content_pack["comparison_outline"])
