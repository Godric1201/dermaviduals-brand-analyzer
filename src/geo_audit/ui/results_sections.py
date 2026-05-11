import streamlit as st
import pandas as pd

from geo_audit.app_constants import TRANSLATIONS
from geo_audit.ui_formatters import translate_dataframe_columns


def render_query_intent_coverage(prompt_categories):
    st.subheader("Query Intent Coverage")
    st.caption(
        "This benchmark covers multiple AI recommendation contexts, not only generic best-brand queries."
    )
    st.write(prompt_categories)


def render_run_status_messages(
    t,
    stored_context,
    current_analysis_context,
    is_quick_test_mode,
    prompt_limit,
):
    st.success(t["complete"])

    if stored_context and stored_context != current_analysis_context:
        st.warning(
            "Sidebar inputs have changed since this analysis was generated. "
            "Run the analysis again to refresh results."
        )

    if is_quick_test_mode:
        prompt_word = "prompt" if prompt_limit == 1 else "prompts"
        st.warning(
            f"TEST VERSION ONLY - Quick Test Mode: this report used only {prompt_limit} {prompt_word} "
            "and is for development only. Not client-deliverable."
        )


def render_run_input_summary(
    competitors,
    prompts,
    show_prompt_debug,
    ai_prompts,
):
    st.write("**Configured Competitors:**")
    st.write(", ".join(competitors))

    if show_prompt_debug:
        with st.expander("AI Generated Prompts Debug", expanded=False):
            st.write(ai_prompts)

    st.write(f"Total prompts: {len(prompts)}")


def build_executive_snapshot_metrics(summary_df, detailed_df, brand):
    target_detailed = detailed_df[
        detailed_df["brand"].str.lower() == brand.lower()
    ]

    organic_score = target_detailed["visibility_score"].mean()
    organic_score = 0 if pd.isna(organic_score) else round(organic_score, 2)

    target_row = summary_df[
        summary_df["brand"].str.lower() == brand.lower()
    ]

    if target_row.empty:
        return {
            "target_found": False,
            "organic_score": organic_score,
        }

    row = target_row.iloc[0]
    return {
        "target_found": True,
        "organic_score": organic_score,
        "target_score": row["average_visibility_score"],
        "target_mentions": row["total_mentions"],
        "target_sov": row["share_of_voice_percent"],
        "target_visible_prompts": row["prompts_visible"],
    }


def render_executive_snapshot(t, summary_df, detailed_df, brand, prompt_count):
    metrics = build_executive_snapshot_metrics(summary_df, detailed_df, brand)

    st.subheader(t["snapshot"])
    st.caption(
        f"Organic Visibility is measured from unbiased prompts that do not mention {brand}."
    )

    if metrics["target_found"]:
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(t["target_brand_metric"], brand)
        col2.metric(t["avg_visibility"], metrics["target_score"])
        col3.metric(t["organic_visibility"], metrics["organic_score"])
        col4.metric(t["total_mentions"], int(metrics["target_mentions"]))
        col5.metric(t["share_of_voice"], f"{metrics['target_sov']}%")

        st.write(
            f"{t['visible_in']} {int(metrics['target_visible_prompts'])} "
            f"{t['out_of']} {prompt_count} {t['prompts_word']}."
        )
    else:
        st.warning(f"{brand} was not detected in the AI answers.")


def build_prompt_matrix_display_df(prompts):
    prompt_table = pd.DataFrame(prompts)
    return translate_dataframe_columns(prompt_table)


def render_prompt_matrix(prompts):
    st.subheader(TRANSLATIONS["prompts"])
    st.dataframe(
        build_prompt_matrix_display_df(prompts),
        use_container_width=True
    )


def build_competitive_benchmark_display_df(summary_display_df):
    return translate_dataframe_columns(summary_display_df)


def render_competitive_benchmark(t, summary_display_df):
    st.subheader(t["benchmark"])
    st.dataframe(
        build_competitive_benchmark_display_df(summary_display_df),
        use_container_width=True
    )


def build_prompt_level_results_display_df(detailed_display_df):
    return translate_dataframe_columns(detailed_display_df)


def render_prompt_level_results(t, detailed_display_df):
    st.subheader(t["prompt_level"])
    st.dataframe(
        build_prompt_level_results_display_df(detailed_display_df),
        use_container_width=True
    )


def render_action_plan(t, plan):
    st.subheader(t["action_plan"])
    st.markdown(plan)


def render_geo_recommendations(t, recommendations):
    with st.expander(t["recommendations"], expanded=False):
        st.write(recommendations)


def render_geo_content_roadmap(geo_content_roadmap_done, geo_content_roadmap):
    if geo_content_roadmap_done:
        st.subheader("GEO Content Roadmap")
        st.caption(
            "Strategic execution plan. Not part of visibility scoring or share of voice."
        )
        st.markdown(geo_content_roadmap)
