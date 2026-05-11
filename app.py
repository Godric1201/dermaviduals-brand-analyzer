from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st

from geo_audit.app_constants import (
    ANSWER_LANGUAGE,
    AUDIENCE,
    BRAND,
    CATEGORY,
    CLIENT_PRESETS,
    MARKET,
    REPORT_LANGUAGE,
    TRANSLATIONS,
)
from geo_audit.analysis_pipeline import get_competitors
from geo_audit.brand_intelligence_prompts import (
    parse_user_brand_strengths,
)
from geo_audit.run_setup import build_run_setup, parse_competitor_input
from geo_audit.ui_formatters import format_display_text
from geo_audit.ui.analysis_controller import run_analysis_controller
from geo_audit.ui.results_controller import display_results_controller
from geo_audit.ui.sidebar_sections import (
    render_advanced_developer_options,
    render_brand_strengths_input,
    render_brand_strengths_summary,
    render_competitor_discovery_section,
    render_page_header,
    render_prompt_mode_label,
    render_run_mode_controls,
    render_sidebar_base_inputs,
    render_sidebar_preset_loader,
    render_sidebar_report_info,
    render_sidebar_run_buttons,
    render_sidebar_validation_messages,
    render_run_confirmation_flow,
)

from geo_audit.analyzer import DEFAULT_MODEL


st.set_page_config(
    page_title="AI Visibility Analyzer",
    layout="wide"
)

RAW_ANSWER_EVIDENCE_HELP = (
    "Raw answers are evidence logs for auditability. They may contain "
    "AI-generated content and should be reviewed before sharing externally."
)

ANALYSIS_OUTPUT_KEYS = [
    "competitors",
    "prompts",
    "ai_prompts",
    "detailed_df",
    "summary_df",
    "raw_answer_df",
    "raw_answers",
    "recommendations",
    "plan",
    "analysis_done",
    "analysis_context",
    "brand_win_explanation",
    "replacement_strategy",
    "gap_analysis",
    "content_pack",
    "strategy_report",
    "brand_intelligence",
    "brand_intelligence_done",
    "brand_understanding",
    "brand_understanding_done",
    "market_relevance",
    "market_relevance_done",
    "geo_content_roadmap",
    "geo_content_roadmap_done",
    "api_usage_summary",
]

def parse_competitors(text):
    return parse_competitor_input(text)


def build_competitor_suggestions_context(brand, category, market, audience):
    return {
        "brand": normalize_context_text(brand),
        "category": normalize_context_text(category),
        "market": normalize_context_text(market),
        "audience": normalize_context_text(audience),
    }


def get_competitor_suggestion_checkbox_key(index):
    return f"competitor_suggestion_selected_{index}"


def clear_competitor_suggestion_selections():
    for key in list(st.session_state):
        if key.startswith("competitor_suggestion_selected_"):
            st.session_state.pop(key, None)


def clear_competitor_suggestions():
    st.session_state.pop("competitor_suggestions", None)
    st.session_state.pop("competitor_suggestions_context", None)
    clear_competitor_suggestion_selections()


def add_selected_competitor_suggestions():
    suggestions = st.session_state.get("competitor_suggestions", [])
    existing_competitors = parse_competitors(
        st.session_state.get("competitors_input", "")
    )
    existing_keys = {
        competitor.lower()
        for competitor in existing_competitors
    }
    added_keys = set()
    additions = []

    for index, suggestion in enumerate(suggestions):
        selected = st.session_state.get(
            get_competitor_suggestion_checkbox_key(index),
            False
        )
        key = suggestion.lower()

        if selected and key not in existing_keys and key not in added_keys:
            additions.append(suggestion)
            added_keys.add(key)

    if additions:
        st.session_state["competitors_input"] = "\n".join(
            existing_competitors + additions
        )

    st.session_state["competitor_suggestions"] = [
        suggestion for suggestion in suggestions
        if suggestion.lower() not in added_keys
    ]
    clear_competitor_suggestion_selections()


def normalize_context_text(value):
    return " ".join(str(value).strip().split())


def clear_analysis_results():
    for key in ANALYSIS_OUTPUT_KEYS:
        st.session_state.pop(key, None)


def run_analysis():
    run_analysis_controller(
        target_brand=target_brand,
        target_category=target_category,
        target_market=target_market,
        target_audience=target_audience,
        display_brand=display_brand,
        display_category=display_category,
        display_market=display_market,
        display_audience=display_audience,
        answer_language=ANSWER_LANGUAGE,
        report_language=REPORT_LANGUAGE,
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        competitors=current_competitors,
        parsed_user_brand_strengths=parsed_user_brand_strengths,
        show_prompt_debug=show_prompt_debug,
        translations=TRANSLATIONS,
    )


def display_results():
    display_results_controller(
        current_analysis_context=current_analysis_context,
        show_prompt_debug=show_prompt_debug,
        translations=TRANSLATIONS,
        default_brand=BRAND,
        default_category=CATEGORY,
        default_market=MARKET,
        default_audience=AUDIENCE,
        raw_answer_evidence_help=RAW_ANSWER_EVIDENCE_HELP,
    )

# =========================
# Main UI
# =========================

t = TRANSLATIONS

render_sidebar_preset_loader(CLIENT_PRESETS)

target_brand, target_category, target_market, target_audience, competitors_text = (
    render_sidebar_base_inputs(
        brand_default=BRAND,
        category_default=CATEGORY,
        market_default=MARKET,
        audience_default=AUDIENCE,
        competitors_default=get_competitors(),
    )
)
parsed_competitors = parse_competitors(competitors_text)
configured_competitors = parsed_competitors if parsed_competitors else get_competitors()
st.sidebar.caption(f"Configured competitors: {len(configured_competitors)}")

competitor_suggestions_context = build_competitor_suggestions_context(
    target_brand,
    target_category,
    target_market,
    target_audience,
)
render_competitor_discovery_section(
    target_brand=target_brand,
    target_category=target_category,
    target_market=target_market,
    target_audience=target_audience,
    parsed_competitors=parsed_competitors,
    competitor_suggestions_context=competitor_suggestions_context,
    answer_language=ANSWER_LANGUAGE,
    clear_competitor_suggestions_fn=clear_competitor_suggestions,
    clear_competitor_suggestion_selections_fn=clear_competitor_suggestion_selections,
    get_competitor_suggestion_checkbox_key_fn=get_competitor_suggestion_checkbox_key,
    add_selected_competitor_suggestions_fn=add_selected_competitor_suggestions,
)

brand_strengths_text = render_brand_strengths_input()
display_brand = format_display_text(target_brand)
display_category = format_display_text(target_category)
display_market = format_display_text(target_market)
display_audience = format_display_text(target_audience)

parsed_user_brand_strengths = parse_user_brand_strengths(brand_strengths_text)
render_brand_strengths_summary(parsed_user_brand_strengths)
render_prompt_mode_label()

show_prompt_debug = render_advanced_developer_options()

render_page_header(display_brand, display_market, display_category)

run_mode, prompt_limit = render_run_mode_controls()

run_setup = build_run_setup(
    target_brand=target_brand,
    target_category=target_category,
    target_market=target_market,
    target_audience=target_audience,
    configured_competitors=configured_competitors,
    run_mode=run_mode,
    prompt_limit=prompt_limit,
    parsed_user_brand_strengths=parsed_user_brand_strengths,
    model_name=DEFAULT_MODEL,
)

current_competitors = run_setup.current_competitors
current_analysis_context = run_setup.current_analysis_context
validation_errors = run_setup.validation_errors
validation_warnings = run_setup.validation_warnings
api_call_estimate = run_setup.api_call_estimate
brand_intelligence_estimated_calls = run_setup.brand_intelligence_estimated_calls
api_cost_estimate = run_setup.api_cost_estimate

render_sidebar_validation_messages(validation_errors, validation_warnings)

review_button = render_sidebar_run_buttons(t, validation_errors)

render_sidebar_report_info()

render_run_confirmation_flow(
    review_button=review_button,
    display_brand=display_brand,
    display_category=display_category,
    display_market=display_market,
    display_audience=display_audience,
    run_mode=run_mode,
    prompt_limit=prompt_limit,
    parsed_user_brand_strengths=parsed_user_brand_strengths,
    current_competitors=current_competitors,
    api_cost_estimate=api_cost_estimate,
    api_call_estimate=api_call_estimate,
    brand_intelligence_estimated_calls=brand_intelligence_estimated_calls,
    validation_errors=validation_errors,
    format_display_text_fn=format_display_text,
    clear_analysis_results_fn=clear_analysis_results,
    run_analysis_fn=run_analysis,
)

if st.session_state.get("analysis_done", False):
    display_results()
