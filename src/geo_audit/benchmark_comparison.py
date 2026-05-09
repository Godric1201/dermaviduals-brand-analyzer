import json
import math


TARGET_METRICS = [
    ("total_mentions", "Total Mentions"),
    ("average_visibility_score", "Average Visibility Score"),
    ("prompts_visible", "Prompts Visible"),
    ("share_of_voice_percent", "Share of Voice %"),
]


def load_snapshot_json(uploaded_file):
    try:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        raw_content = uploaded_file.read()
        if isinstance(raw_content, bytes):
            raw_content = raw_content.decode("utf-8")

        snapshot = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError) as exc:
        raise ValueError(
            "Invalid benchmark snapshot JSON. Please upload a valid benchmark_snapshot.json file."
        ) from exc

    if not isinstance(snapshot, dict):
        raise ValueError(
            "Invalid benchmark snapshot JSON. Expected a JSON object."
        )

    return snapshot


def normalize_brand_name(value):
    return " ".join(str(value or "").strip().split()).lower()


def _normalize_text(value):
    return " ".join(str(value or "").strip().split())


def find_brand_summary_record(snapshot, brand):
    target_brand = normalize_brand_name(brand)

    for record in snapshot.get("summary_records", []) or []:
        if not isinstance(record, dict):
            continue

        if normalize_brand_name(record.get("brand")) == target_brand:
            return record

    return None


def _metric_value(record, metric_key):
    if not record:
        return 0

    value = record.get(metric_key, 0)
    if value in (None, ""):
        return 0

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0

    if math.isnan(numeric_value):
        return 0

    if numeric_value.is_integer():
        return int(numeric_value)

    return numeric_value


def compare_target_brand_metrics(previous_snapshot, current_snapshot):
    previous_metadata = previous_snapshot.get("metadata", {}) or {}
    current_metadata = current_snapshot.get("metadata", {}) or {}
    current_brand = current_metadata.get("brand", "")
    previous_brand = previous_metadata.get("brand", "")
    warnings = []

    if (
        previous_brand
        and current_brand
        and normalize_brand_name(previous_brand) != normalize_brand_name(current_brand)
    ):
        warnings.append(
            "Previous snapshot target brand does not match the current analysis context."
        )

    previous_record = find_brand_summary_record(previous_snapshot, current_brand)
    current_record = find_brand_summary_record(current_snapshot, current_brand)

    if previous_record is None:
        warnings.append(
            "Previous snapshot does not contain a matching target brand row; previous values are treated as 0."
        )

    if current_record is None:
        warnings.append(
            "Current snapshot does not contain a matching target brand row; current values are treated as 0."
        )

    rows = []
    for metric_key, metric_label in TARGET_METRICS:
        previous_value = _metric_value(previous_record, metric_key)
        current_value = _metric_value(current_record, metric_key)

        rows.append({
            "Metric": metric_label,
            "Previous": previous_value,
            "Current": current_value,
            "Change": current_value - previous_value,
        })

    return {
        "metrics": rows,
        "warnings": warnings,
    }


def _get_prompt_category(record):
    return _normalize_text(
        record.get("prompt_category") or record.get("category") or ""
    )


def _get_visibility_value(record):
    if "visibility_score" in record:
        return _metric_value(record, "visibility_score")

    return _metric_value(record, "average_visibility_score")


def _aggregate_query_intent_visibility(snapshot, brand):
    target_brand = normalize_brand_name(brand)
    grouped = {}

    for record in snapshot.get("detailed_records", []) or []:
        if not isinstance(record, dict):
            continue

        if normalize_brand_name(record.get("brand")) != target_brand:
            continue

        prompt_category = _get_prompt_category(record)
        if not prompt_category:
            continue

        visibility_score = _get_visibility_value(record)
        mentions = _metric_value(record, "mentions")
        is_visible = 1 if visibility_score > 0 else 0

        if prompt_category not in grouped:
            grouped[prompt_category] = {
                "visibility_scores": [],
                "mentions": 0,
                "visible_count": 0,
            }

        grouped[prompt_category]["visibility_scores"].append(visibility_score)
        grouped[prompt_category]["mentions"] += mentions
        grouped[prompt_category]["visible_count"] += is_visible

    aggregated = {}
    for prompt_category, values in grouped.items():
        visibility_scores = values["visibility_scores"]
        avg_visibility = (
            sum(visibility_scores) / len(visibility_scores)
            if visibility_scores
            else 0
        )

        aggregated[prompt_category] = {
            "avg_visibility": avg_visibility,
            "mentions": values["mentions"],
            "visible_count": values["visible_count"],
        }

    return aggregated


def _ordered_categories(previous_categories, current_categories):
    categories = []
    seen = set()

    for category in list(previous_categories) + list(current_categories):
        key = category.lower()
        if key not in seen:
            categories.append(category)
            seen.add(key)

    return categories


def compare_query_intent_visibility(previous_snapshot, current_snapshot):
    current_metadata = current_snapshot.get("metadata", {}) or {}
    current_brand = current_metadata.get("brand", "")
    previous_aggregation = _aggregate_query_intent_visibility(
        previous_snapshot,
        current_brand,
    )
    current_aggregation = _aggregate_query_intent_visibility(
        current_snapshot,
        current_brand,
    )
    categories = _ordered_categories(
        previous_aggregation.keys(),
        current_aggregation.keys(),
    )

    rows = []
    for category in categories:
        previous_values = previous_aggregation.get(category, {})
        current_values = current_aggregation.get(category, {})
        previous_avg = previous_values.get("avg_visibility", 0)
        current_avg = current_values.get("avg_visibility", 0)
        previous_mentions = previous_values.get("mentions", 0)
        current_mentions = current_values.get("mentions", 0)
        previous_visible_count = previous_values.get("visible_count", 0)
        current_visible_count = current_values.get("visible_count", 0)

        rows.append({
            "Query Intent": category,
            "Previous Avg Visibility": previous_avg,
            "Current Avg Visibility": current_avg,
            "Change": current_avg - previous_avg,
            "Previous Mentions": previous_mentions,
            "Current Mentions": current_mentions,
            "Mentions Change": current_mentions - previous_mentions,
            "Previous Visible Count": previous_visible_count,
            "Current Visible Count": current_visible_count,
            "Visible Count Change": current_visible_count - previous_visible_count,
        })

    return rows
