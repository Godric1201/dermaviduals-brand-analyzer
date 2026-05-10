import json
import os

import pandas as pd
from .output_quality import OutputQualityContext, sanitize_snapshot_payload
DEFAULT_MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_PROMPT_SET_VERSION = os.getenv("PROMPT_SET_VERSION", "v1")
DEFAULT_REPEAT_COUNT = int(os.getenv("PROMPT_REPEAT_COUNT", "1"))

def _json_safe_value(value):
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, TypeError, ValueError):
            pass

    return value


def dataframe_to_records(df):
    if df is None:
        return []

    records = df.to_dict(orient="records")

    return [
        {
            key: _json_safe_value(value)
            for key, value in record.items()
        }
        for record in records
    ]

def build_run_metadata(
    report_date,
    run_mode,
    prompt_limit,
    prompt_count,
    include_raw_answers,
    model_name=None,
    prompt_set_version=None,
    repeat_count=None,
):
    """Build reproducibility metadata for a benchmark snapshot."""
    return {
        "model_name": model_name or DEFAULT_MODEL_NAME,
        "prompt_set_version": prompt_set_version or DEFAULT_PROMPT_SET_VERSION,
        "repeat_count": repeat_count or DEFAULT_REPEAT_COUNT,
        "run_mode": run_mode,
        "prompt_limit": prompt_limit,
        "prompt_count": prompt_count,
        "raw_answers_included": bool(include_raw_answers),
        "generated_at": report_date,
    }

def build_benchmark_snapshot(
    brand,
    market,
    category,
    audience,
    report_date,
    run_mode,
    prompt_limit,
    prompt_count,
    competitors,
    query_intent_categories,
    summary_df,
    detailed_df,
    brand_intelligence=None,
    include_raw_answers=False,
    raw_answer_df=None,
    model_name=None,
    prompt_set_version=None,
    repeat_count=None,
):
    brand_intelligence = brand_intelligence or {}

    snapshot = {
        "schema_version": "1.0",
        "generated_at": report_date,
        "metadata": {
        "brand": brand,
        "market": market,
        "category": category,
        "audience": audience,
        "report_date": report_date,
        "run_mode": run_mode,
        "prompt_limit": prompt_limit,
        "prompt_count": prompt_count,
        "competitors": list(competitors or []),
        "query_intent_categories": list(query_intent_categories or []),
        "run_metadata": build_run_metadata(
            report_date=report_date,
            run_mode=run_mode,
            prompt_limit=prompt_limit,
            prompt_count=prompt_count,
            include_raw_answers=include_raw_answers,
            model_name=model_name,
            prompt_set_version=prompt_set_version,
            repeat_count=repeat_count,
    ),
},
        "summary_records": dataframe_to_records(summary_df),
        "detailed_records": dataframe_to_records(detailed_df),
        "brand_intelligence": {
            "recommendation_drivers": brand_intelligence.get("recommendation_drivers"),
            "target_brand_understanding": brand_intelligence.get("target_brand_understanding"),
            "positioning_gap_analysis": brand_intelligence.get("positioning_gap_analysis"),
        },
        "notes": {
            "quick_test_mode": (
                "Quick Test Mode output is not client-deliverable."
                if run_mode == "Quick Test Mode"
                else None
            ),
            "brand_intelligence": (
                "Brand Intelligence diagnostic output is not part of visibility scoring or share of voice."
            ),
        },
    }

    if include_raw_answers:
        snapshot["raw_answer_records"] = dataframe_to_records(raw_answer_df)

    return sanitize_snapshot_payload(
        snapshot,
        OutputQualityContext(
            category=category,
            run_mode=run_mode,
            brand=brand,
            market=market,
            audience=audience,
            tracked_competitors=list(competitors or []),
        ),
    )


def serialize_benchmark_snapshot(snapshot):
    return json.dumps(
        snapshot,
        ensure_ascii=False,
        indent=2,
        default=str,
    )
