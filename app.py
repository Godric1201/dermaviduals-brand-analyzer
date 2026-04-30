import streamlit as st
import pandas as pd
import plotly.express as px
from app_constants import (
    ANSWER_LANGUAGE,
    AUDIENCE,
    BRAND,
    CATEGORY,
    MARKET,
    REPORT_LANGUAGE,
    TRANSLATIONS,
)
from analysis_pipeline import get_competitors, run_visibility_analysis
from prompts import build_fixed_prompts
from ui_formatters import df_to_markdown_table, translate_dataframe_columns

from analyzer import ask_ai
from content_generator import generate_level_2_content_pack
from report_generator import (
    build_competitor_leader_sentence,
    create_executive_docx_report,
    get_competitor_leaders,
    get_visibility_status,
)
from utils import convert_df_to_csv


st.set_page_config(
    page_title="Dermaviduals Hong Kong AI Visibility Analyzer",
    layout="wide"
)


def parse_competitors(text):
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


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

    st.info("Using configured professional skincare competitors...")

    default_competitors = get_competitors()
    competitors = parse_competitors(competitors_text)
    if not competitors:
        competitors = default_competitors

    st.write("**Competitors:**")
    st.write(", ".join(competitors))

    with st.expander("AI Generated Prompts Debug"):
        ai_prompts_placeholder = st.empty()

    total_prompts_placeholder = st.empty()

    progress_bar = st.progress(0)
    status_text = st.empty()

    def on_progress(index, total_prompts, prompt_category):
        status_text.write(
            f"{TRANSLATIONS['running_prompt']} {index + 1}/{total_prompts}: {prompt_category}"
        )
        progress_bar.progress((index + 1) / total_prompts)

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
        )

    progress_bar.progress(1.0)
    status_text.write(TRANSLATIONS["complete_status"])

    ai_prompts = result["ai_prompts"]
    prompts = result["prompts"]

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
    st.session_state["brand"] = brand
    st.session_state["category"] = category
    st.session_state["market"] = market
    st.session_state["audience"] = audience
    st.session_state["run_mode"] = run_mode
    st.session_state["prompt_limit"] = prompt_limit
    st.session_state["analysis_done"] = True


def display_results():
    t = TRANSLATIONS
    brand = st.session_state.get("brand", BRAND)
    category = st.session_state.get("category", CATEGORY)
    market = st.session_state.get("market", MARKET)
    audience = st.session_state.get("audience", AUDIENCE)

    competitors = st.session_state["competitors"]
    prompts = st.session_state["prompts"]
    ai_prompts = st.session_state["ai_prompts"]
    detailed_df = st.session_state["detailed_df"]
    summary_df = st.session_state["summary_df"]
    raw_answer_df = st.session_state["raw_answer_df"]
    raw_answers = st.session_state["raw_answers"]
    recommendations = st.session_state["recommendations"]
    plan = st.session_state["plan"]
    run_mode = st.session_state.get("run_mode", "Full Report Mode")
    prompt_limit = st.session_state.get("prompt_limit")
    is_quick_test_mode = run_mode == "Quick Test Mode"
    deliverable_status = "Client-deliverable full report"

    if is_quick_test_mode:
        deliverable_status = (
            "Development-only limited-prompt output. Not client-deliverable."
        )

    st.success(t["complete"])

    if is_quick_test_mode:
        prompt_word = "prompt" if prompt_limit == 1 else "prompts"
        st.warning(
            f"TEST VERSION ONLY - Quick Test Mode: this report used only {prompt_limit} {prompt_word} "
            "and is for development only. Not client-deliverable."
        )

    st.write("**Hong Kong Professional Competitors:**")
    st.write(", ".join(competitors))

    with st.expander("AI Generated Prompts Debug"):
        st.write(ai_prompts)

    st.write(f"Total prompts: {len(prompts)}")

    # =========================
    # 1. Executive Snapshot
    # =========================
    target_detailed = detailed_df[
        detailed_df["brand"].str.lower() == brand.lower()
    ]

    organic_score = target_detailed["visibility_score"].mean()
    organic_score = 0 if pd.isna(organic_score) else round(organic_score, 2)

    target_row = summary_df[
        summary_df["brand"].str.lower() == brand.lower()
    ]

    st.subheader(t["snapshot"])
    st.caption(t["caption"])

    if not target_row.empty:
        target_score = target_row.iloc[0]["average_visibility_score"]
        target_mentions = target_row.iloc[0]["total_mentions"]
        target_sov = target_row.iloc[0]["share_of_voice_percent"]
        target_visible_prompts = target_row.iloc[0]["prompts_visible"]

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(t["target_brand_metric"], brand)
        col2.metric(t["avg_visibility"], target_score)
        col3.metric(t["organic_visibility"], organic_score)
        col4.metric(t["total_mentions"], int(target_mentions))
        col5.metric(t["share_of_voice"], f"{target_sov}%")

        st.write(
            f"{t['visible_in']} {int(target_visible_prompts)} "
            f"{t['out_of']} {len(prompts)} {t['prompts_word']}."
        )
    else:
        st.warning(f"{brand} was not detected in the AI answers.")

    # =========================
    # 2. Prompts
    # =========================
    st.subheader(t["prompts"])
    prompt_table = pd.DataFrame(prompts)
    st.dataframe(
        translate_dataframe_columns(prompt_table),
        use_container_width=True
    )

    # =========================
    # 3. Competitor Benchmark
    # =========================
    st.subheader(t["benchmark"])
    st.dataframe(
        translate_dataframe_columns(summary_df),
        use_container_width=True
    )

    # =========================
    # 4. Trigger-Level Visibility
    # =========================
    st.subheader("Trigger-Level Brand Visibility (Core Insight)")

    pivot = detailed_df.pivot_table(
        index="prompt_category",
        columns="brand",
        values="visibility_score",
        aggfunc="mean"
    ).fillna(0)

    st.dataframe(pivot, use_container_width=True)

    if not pivot.empty:
        fig_heatmap = px.imshow(
            pivot,
            text_auto=True,
            aspect="auto",
            title="AI Brand Visibility Heatmap (by Query Type)"
    )

        fig_heatmap.update_layout(height=650)
        fig_heatmap.update_xaxes(tickangle=45)

        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No data available for heatmap.")

    # =========================
    # 5. Top Brands per Query Type
    # =========================
    st.subheader("Top Performing Brands per Query Type")
    st.caption("This table identifies which brand wins each AI query category based on visibility score.")

    positive_df = detailed_df[detailed_df["visibility_score"] > 0].copy()

    if not positive_df.empty:
        top_brands = (
            positive_df.sort_values("visibility_score", ascending=False)
            .groupby("prompt_category")
            .first()
            .reset_index()
        )

        st.dataframe(
            top_brands[["prompt_category", "brand", "visibility_score"]],
            use_container_width=True
        )
    else:
        top_brands = pd.DataFrame(
            columns=["prompt_category", "brand", "visibility_score"]
        )
        st.warning("No brands received positive visibility scores.")

    # =========================
    # 6. Why These Brands Win
    # =========================

    with st.expander("Why These Brands Win (AI Decision Explanation)", expanded=False):
        if top_brands.empty:
            st.warning("No top brands to explain.")
        else:
            explain_prompt = f"""
    You are analyzing AI-generated professional skincare brand recommendations.

    Based on the data below, explain WHY each top brand is selected by AI.

    Focus on:
    - What signal triggers the brand
    - What authority the brand has
    - What makes it preferred over others
    - What query type it wins

    Top brands per category:
    {top_brands.to_string(index=False)}

    Detailed data:
    {detailed_df.head(50).to_string(index=False)}

    Explain in this format:

    - Category: X
    - Winning Brand: Y
    - Why AI selects it:
    - What signal it owns:
    - Strategic implication for Dermaviduals:
    """

            if "brand_win_explanation" not in st.session_state:
                st.session_state["brand_win_explanation"] = ask_ai(explain_prompt)

            st.write(st.session_state["brand_win_explanation"])

    # =========================
    # 7. How Dermaviduals Can Replace Winners
    # =========================
    with st.expander("How Dermaviduals Can Replace These Brands", expanded=False):
        if top_brands.empty:
            st.warning("No replacement strategy available because no positive brand winners were detected.")
        else:
            replace_prompt = f"""
    You are a senior GEO strategist.

    Based on the AI visibility data below, explain how Dermaviduals can replace the currently dominant brands in AI-generated recommendations.

    Target brand:
    Dermaviduals

    Dominant brands per category:
    {top_brands.to_string(index=False)}

    Summary data:
    {summary_df.to_string(index=False)}

    Detailed data:
    {detailed_df.head(50).to_string(index=False)}

    Raw AI answers:
    {str(raw_answers[:10])}

    For each major dominant brand, explain:

    1. What the competitor currently owns in AI perception
    2. Why AI recommends that competitor
    3. What Dermaviduals should do to compete
    4. What content should be created
    5. What query or keyword cluster Dermaviduals should target

    Use this format:

    ## Competitor: [Brand Name]

    - AI-owned territory:
    - Why it wins:
    - Weakness or opening:
    - Dermaviduals replacement strategy:
    - Content to create:
    - Target queries:

    Be specific. Avoid generic SEO advice.
    """

            if "replacement_strategy" not in st.session_state:
                st.session_state["replacement_strategy"] = ask_ai(replace_prompt)

            st.write(st.session_state["replacement_strategy"])

    # =========================
    # 8. Benchmark Charts
    # =========================
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

    # =========================
    # 9. Prompt-Level Results
    # =========================
    st.subheader(t["prompt_level"])
    st.dataframe(
        translate_dataframe_columns(detailed_df),
        use_container_width=True
    )

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

    # =========================
    # 10. Raw Answers
    # =========================
    st.subheader("5. Raw AI Answers / Evidence Log")
    st.caption("Open each item to inspect the original AI answer used for scoring.")

    for item in raw_answers:
        with st.expander(f"{item['prompt_category']}"):
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.write(item["answer"])

    # =========================
    # 11. GEO Recommendations
    # =========================
    with st.expander(t["recommendations"], expanded=False):
        st.write(recommendations)

    # =========================
    # 12. AI Association Gap
    # =========================
    with st.expander("AI Association Gap (Why You Are Not Recommended)", expanded=False):
        gap_prompt = f"""
    You are analyzing AI brand association patterns.

    Based on the data below, explain:

    1. What concepts each competitor is associated with
    2. What concepts Dermaviduals is missing
    3. Why AI does not recommend Dermaviduals

    Competitors:
    {", ".join(competitors)}

    Summary:
    {summary_df.to_string(index=False)}

    Detailed:
    {detailed_df.head(50).to_string(index=False)}

    Answer in structured bullet points.
    """

        if "gap_analysis" not in st.session_state:
            st.session_state["gap_analysis"] = ask_ai(gap_prompt)

    st.write(st.session_state["gap_analysis"])
    # =========================
    # 13. Level 3 Strategic Insight
    # =========================
    st.subheader(t["action_plan"])
    st.markdown(plan)

    # =========================
    # 14. Level 2 Content Pack
    # =========================
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

    # =========================
    # 15. Export Reports
    # =========================
    st.subheader(t["exports"])

    # Build clean executive report tables
    summary_report_df = summary_df.copy()

    summary_columns = [
        "brand",
        "total_mentions",
        "average_visibility_score",
        "prompts_visible",
        "share_of_voice_percent"
    ]

    summary_columns = [
        col for col in summary_columns
        if col in summary_report_df.columns
    ]

    summary_report_df = summary_report_df[summary_columns].sort_values(
        by="average_visibility_score",
        ascending=False
    )

    summary_report_md = df_to_markdown_table(
        translate_dataframe_columns(summary_report_df),
        max_rows=15
    )

    trigger_report_md = df_to_markdown_table(
        pivot.reset_index(),
        max_rows=25
    )

    top_brands_report_md = df_to_markdown_table(
        top_brands[["prompt_category", "brand", "visibility_score"]],
        max_rows=25
    ) if not top_brands.empty else "_No positive brand winners detected._"

    target_summary = summary_df[
        summary_df["brand"].str.lower() == brand.lower()
    ]

    if not target_summary.empty:
        target_mentions = target_summary.iloc[0].get("total_mentions", 0)
        target_avg_score = target_summary.iloc[0].get("average_visibility_score", 0)
        target_prompts_visible = target_summary.iloc[0].get("prompts_visible", 0)
        target_sov = target_summary.iloc[0].get("share_of_voice_percent", 0)
    else:
        target_mentions = 0
        target_avg_score = 0
        target_prompts_visible = 0
        target_sov = 0

    target_visibility_status = get_visibility_status(
        target_mentions,
        target_avg_score,
        target_sov
    )

    top_competitors = summary_df[
        summary_df["brand"].str.lower() != brand.lower()
    ].sort_values(
        by="average_visibility_score",
        ascending=False
    ).head(3)

    competitor_leaders = get_competitor_leaders(summary_df, brand)
    top_competitor_text = build_competitor_leader_sentence(
        competitor_leaders
    )

    if target_mentions == 0:
        strategic_issue = (
            f"The main strategic issue is that AI systems have not produced measurable mentions for {brand} "
            f"in this benchmark, leaving the brand at {target_sov}% share of voice."
        )
    else:
        strategic_issue = (
            f"The main strategic issue is to improve from {target_mentions} mentions, "
            f"{target_avg_score} average visibility, and {target_sov}% share of voice by strengthening association "
            "with high-value professional skincare query territories such as sensitive skin, barrier repair, "
            "post-treatment care, clinic-grade skincare, and Hong Kong professional skincare."
        )

    executive_summary_sentence = (
        f"{brand} is {target_visibility_status} across the tested AI search prompts, "
        f"with {target_mentions} total mentions, {target_avg_score} average visibility, "
        f"{target_prompts_visible} prompts visible, and {target_sov}% share of voice."
    )

    executive_report = f"""
    # {brand} {market} AI Visibility Report

    ## 1. Report Overview

    **Target Brand:** {brand}  
    **Market:** {market}  
    **Category:** {category}  
    **Audience:** {audience}  
    **Report Type:** AI Visibility / Generative Engine Optimization Audit  
    **Run Mode:** {run_mode}  
    **Deliverable Status:** {deliverable_status}  

    {"**TEST VERSION ONLY - Quick Test Mode. Not Client Deliverable.**" if is_quick_test_mode else ""}

    This report evaluates how visible {brand} is in AI-generated skincare recommendations for the {market} professional skincare market.

    ---

    ## 2. Executive Summary

    {executive_summary_sentence}

    Key metrics for {brand}:

    | Metric | Value |
    |---|---:|
    | Total Mentions | {target_mentions} |
    | Average Visibility Score | {target_avg_score} |
    | Prompts Visible | {target_prompts_visible} |
    | Share of Voice | {target_sov}% |

    Top visible competitors in this benchmark:

    {top_competitor_text}

    {strategic_issue}

    ---

    ## 3. Competitive Benchmark

    The table below summarizes brand-level AI visibility performance across all tested prompts.

    {summary_report_md}

    ---

    ## 4. Trigger-Level Visibility Findings

    The table below shows how each tracked brand performs across AI query categories.

    {trigger_report_md}

    ---

    ## 5. Top Brand Winners by Query Type

    The table below identifies which brand wins each query category based on visibility score.

    {top_brands_report_md}

    ---

    ## 6. Strategic Diagnosis

    {st.session_state.get("gap_analysis", "_AI Association Gap analysis was not generated in this run._")}

    ---

    ## 7. Priority Strategic Recommendations

    {recommendations}

    ---

    ## 8. AI Visibility Strategy Report

    {plan}

    ---

    ## 9. Appendix: AI Decision Explanation

    {st.session_state.get("brand_win_explanation", "_Brand winner explanation was not generated in this run._")}

    ---

    ## 10. Appendix: Replacement Strategy

    {st.session_state.get("replacement_strategy", "_Replacement strategy was not generated in this run._")}
    """

    executive_docx = create_executive_docx_report(
        brand=brand,
        market=market,
        category=category,
        audience=audience,
        summary_df=summary_df,
        top_brands_df=top_brands,
        recommendations=recommendations,
        strategy_report=plan,
        gap_analysis=st.session_state.get("gap_analysis", ""),
        run_mode=run_mode,
        prompt_limit=prompt_limit
    )


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.download_button(
            label=t["summary_csv"],
            data=convert_df_to_csv(summary_df),
            file_name="dermaviduals_hk_summary_visibility_report.csv",
            mime="text/csv",
            key="summary_download",
            on_click="ignore",
        )

    with col2:
        st.download_button(
            label=t["detailed_csv"],
            data=convert_df_to_csv(detailed_df),
            file_name="dermaviduals_hk_detailed_prompt_report.csv",
            mime="text/csv",
            key="detailed_download",
            on_click="ignore",
        )

    with col3:
        st.download_button(
            label=t["raw_csv"],
            data=convert_df_to_csv(raw_answer_df),
            file_name="dermaviduals_hk_raw_ai_answers.csv",
            mime="text/csv",
            key="raw_download",
            on_click="ignore",
        )

    with col4:
        st.download_button(
            label="Download Executive Report MD",
            data=executive_report.encode("utf-8-sig"),
            file_name="dermaviduals_hk_executive_report.md",
            mime="text/markdown",
            key="executive_report_download",
            on_click="ignore",
        )

    with col5:
        st.download_button(
            label="Download Client Report DOCX",
            data=executive_docx,
            file_name="dermaviduals_hk_client_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="client_report_docx_download",
            on_click="ignore",
        )

# =========================
# Main UI
# =========================

t = TRANSLATIONS

st.title(t["title"])
st.caption(t["subtitle"])
st.markdown(t["description"])

st.sidebar.header("Analysis Setup")
target_brand = st.sidebar.text_input("Target Brand", value=BRAND)
target_category = st.sidebar.text_input("Category", value=CATEGORY)
target_market = st.sidebar.text_input("Market", value=MARKET)
target_audience = st.sidebar.text_area("Audience", value=AUDIENCE)
competitors_text = st.sidebar.text_area(
    "Competitors",
    value="\n".join(get_competitors()),
    help="Enter one competitor per line."
)
st.sidebar.write("**Prompt Mode:** Fixed + AI Generated")

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

run_button = st.sidebar.button(t["run"])
reset_button = st.sidebar.button(t["reset"])

if reset_button:
    st.session_state.clear()
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("""
### What this prototype measures

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
### Report Structure

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
The visibility score is based on three signals:

1. **Mentions**
2. **First appearance position**
3. **Estimated rank**

Organic Visibility is measured from unbiased prompts that do not mention the target brand.
""")

if run_button:
    st.session_state.clear()
    run_analysis()

if st.session_state.get("analysis_done", False):
    display_results()
