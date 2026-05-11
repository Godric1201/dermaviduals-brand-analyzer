import plotly.express as px
import streamlit as st


def render_benchmark_charts(t, summary_df):
    col_a, col_b = st.columns(2)

    with col_a:
        fig_score = px.bar(
            summary_df,
            x="brand",
            y="average_visibility_score",
            title=t["avg_visibility"],
            text="average_visibility_score",
            labels={
                "brand": t["brand_label"],
                "average_visibility_score": t["avg_visibility"]
            }
        )
        st.plotly_chart(fig_score, use_container_width=True)

    with col_b:
        fig_sov = px.pie(
            summary_df,
            names="brand",
            values="share_of_voice_percent",
            title=t["share_of_voice"]
        )
        st.plotly_chart(fig_sov, use_container_width=True)


def render_prompt_level_chart(t, detailed_df):
    fig_prompt = px.bar(
        detailed_df,
        x="prompt_category",
        y="visibility_score",
        color="brand",
        barmode="group",
        title=t["organic_visibility"],
        labels={
            "prompt_category": t["prompt_category_label"],
            "visibility_score": t["score_label"],
            "brand": t["brand_label"]
        }
    )
    st.plotly_chart(fig_prompt, use_container_width=True)
