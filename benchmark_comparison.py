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
