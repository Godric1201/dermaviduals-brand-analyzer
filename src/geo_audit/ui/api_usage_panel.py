from geo_audit.analyzer import DEFAULT_MODEL
from geo_audit.api_cost_estimator import format_usd
from geo_audit.benchmark_snapshot import normalize_api_usage_summary


API_USAGE_DISPLAY_NUMERIC_FIELDS = (
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "call_count",
    "calls_with_usage",
    "calls_without_usage",
)


def _safe_usage_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_usage_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def build_empty_api_usage_summary():
    return {
        "model_name": DEFAULT_MODEL,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "call_count": 0,
        "calls_with_usage": 0,
        "calls_without_usage": 0,
        "usage_available": False,
        "pricing_available": False,
        "estimated_actual_cost_usd": None,
        "pricing_label": None,
    }


def coerce_api_usage_summary(api_usage_summary):
    summary = build_empty_api_usage_summary()
    normalized = normalize_api_usage_summary(api_usage_summary)

    if normalized is None:
        return summary

    summary.update(normalized)
    for field in API_USAGE_DISPLAY_NUMERIC_FIELDS:
        summary[field] = _safe_usage_int(summary.get(field))

    summary["estimated_actual_cost_usd"] = _safe_usage_float(
        summary.get("estimated_actual_cost_usd")
    )
    summary["usage_available"] = bool(summary.get("usage_available"))
    summary["pricing_available"] = bool(summary.get("pricing_available"))
    return summary


def format_api_usage_cost(api_usage_summary):
    if (
        not api_usage_summary.get("usage_available")
        or not api_usage_summary.get("pricing_available")
        or api_usage_summary.get("estimated_actual_cost_usd") is None
    ):
        return "Unavailable"

    return format_usd(api_usage_summary["estimated_actual_cost_usd"])


def build_api_usage_display_rows(api_usage_summary):
    summary = coerce_api_usage_summary(api_usage_summary)
    return [
        {"Metric": "Model", "Value": summary.get("model_name") or "Unavailable"},
        {"Metric": "AI calls", "Value": summary["call_count"]},
        {"Metric": "Calls with usage", "Value": summary["calls_with_usage"]},
        {"Metric": "Calls without usage", "Value": summary["calls_without_usage"]},
        {"Metric": "Input tokens", "Value": summary["input_tokens"]},
        {"Metric": "Output tokens", "Value": summary["output_tokens"]},
        {"Metric": "Total tokens", "Value": summary["total_tokens"]},
        {
            "Metric": "Estimated actual API cost",
            "Value": format_api_usage_cost(summary),
        },
        {
            "Metric": "Pricing assumption",
            "Value": summary.get("pricing_label") or "Unavailable",
        },
    ]


def render_api_usage_summary(api_usage_summary):
    import pandas as pd
    import streamlit as st

    summary = coerce_api_usage_summary(api_usage_summary)

    st.subheader("API Usage From This Run")
    st.caption("Actual token usage when available.")
    st.table(pd.DataFrame(build_api_usage_display_rows(summary)))

    if summary["calls_without_usage"] > 0:
        st.info(
            "Token usage metadata was not available for all calls. Cost is "
            "estimated from available token metadata only."
        )

    if summary["usage_available"] and not summary["pricing_available"]:
        st.info(
            "Cost estimate unavailable for this configured model. Check current "
            "OpenAI API pricing."
        )
