import streamlit as st

from geo_audit.analyzer import ask_ai
from geo_audit.narrative_prompts import (
    build_ai_decision_explanation_prompt,
    build_replacement_strategy_prompt,
)
from geo_audit.output_quality import (
    OutputQualityContext,
    sanitize_narrative_appendix_text,
)


def render_brand_winners_explanation(
    brand,
    category,
    market,
    audience,
    competitors,
    run_mode,
    top_brands,
    detailed_df,
):
    with st.expander("Why These Brands Win (AI Decision Explanation)", expanded=False):
        if top_brands.empty:
            st.warning("No top brands to explain.")
        else:
            explain_prompt = build_ai_decision_explanation_prompt(
                brand=brand,
                category=category,
                market=market,
                top_brands_df=top_brands,
                detailed_df=detailed_df,
            )

            if "brand_win_explanation" not in st.session_state:
                st.session_state["brand_win_explanation"] = sanitize_narrative_appendix_text(
                    ask_ai(explain_prompt),
                    OutputQualityContext(
                        category=category,
                        run_mode=run_mode,
                        brand=brand,
                        market=market,
                        audience=audience,
                        tracked_competitors=competitors,
                    ),
                )

            st.write(st.session_state["brand_win_explanation"])


def render_replacement_strategy(
    brand,
    category,
    market,
    audience,
    competitors,
    run_mode,
    top_brands,
    summary_df,
    detailed_df,
    raw_answers,
):
    with st.expander(f"How {brand} Can Replace These Brands", expanded=False):
        if top_brands.empty:
            st.warning("No replacement strategy available because no positive brand winners were detected.")
        else:
            replace_prompt = build_replacement_strategy_prompt(
                brand=brand,
                category=category,
                market=market,
                audience=audience,
                top_brands_df=top_brands,
                summary_df=summary_df,
                detailed_df=detailed_df,
                raw_answers=raw_answers,
            )

            if "replacement_strategy" not in st.session_state:
                st.session_state["replacement_strategy"] = sanitize_narrative_appendix_text(
                    ask_ai(replace_prompt),
                    OutputQualityContext(
                        category=category,
                        run_mode=run_mode,
                        brand=brand,
                        market=market,
                        audience=audience,
                        tracked_competitors=competitors,
                    ),
                )

            st.write(st.session_state["replacement_strategy"])
