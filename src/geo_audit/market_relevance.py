import json
import re
from dataclasses import dataclass

import pandas as pd

from . import analyzer
from .api_usage import record_openai_usage


MARKET_LOCK_MARKET_SPECIFIC = "Market-specific"
MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC = "Partially market-specific"
MARKET_LOCK_GLOBAL_DEFAULT_RISK = "Global-default risk"
MARKET_LOCK_INSUFFICIENT_EVIDENCE = "Insufficient evidence"

ALLOWED_MARKET_LOCK_STATUS_LABELS = (
    MARKET_LOCK_MARKET_SPECIFIC,
    MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC,
    MARKET_LOCK_GLOBAL_DEFAULT_RISK,
    MARKET_LOCK_INSUFFICIENT_EVIDENCE,
)

LOCAL_SIGNAL_CLEAR = "Clear"
LOCAL_SIGNAL_PARTIAL = "Partial"
LOCAL_SIGNAL_WEAK = "Weak"
LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE = "Not Enough Evidence"

ALLOWED_LOCAL_BRAND_PRESENCE_LABELS = (
    LOCAL_SIGNAL_CLEAR,
    LOCAL_SIGNAL_PARTIAL,
    LOCAL_SIGNAL_WEAK,
    LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE,
)

VISIBLE_FIT_MARKET_RELEVANT = "Market-relevant"
VISIBLE_FIT_GLOBAL_DEFAULT = "Global-default"
VISIBLE_FIT_UNCLEAR = "Unclear"

ALLOWED_VISIBLE_BRAND_FIT_LABELS = (
    VISIBLE_FIT_MARKET_RELEVANT,
    VISIBLE_FIT_GLOBAL_DEFAULT,
    VISIBLE_FIT_UNCLEAR,
)

INTERPRETATION_MARKET_EVIDENCE_GAP = "Market evidence gap"
INTERPRETATION_GLOBAL_DEFAULT_RETRIEVAL_RISK = "Global-default retrieval risk"
INTERPRETATION_MARKET_SPECIFIC_COMPETITIVE_GAP = "Market-specific competitive gap"
INTERPRETATION_INSUFFICIENT_EVIDENCE = "Insufficient evidence"
INTERPRETATION_MIXED_DIAGNOSIS = "Mixed diagnosis"

ALLOWED_RECOMMENDED_INTERPRETATION_LABELS = (
    INTERPRETATION_MARKET_EVIDENCE_GAP,
    INTERPRETATION_GLOBAL_DEFAULT_RETRIEVAL_RISK,
    INTERPRETATION_MARKET_SPECIFIC_COMPETITIVE_GAP,
    INTERPRETATION_INSUFFICIENT_EVIDENCE,
    INTERPRETATION_MIXED_DIAGNOSIS,
)

VALIDATION_NOTE = (
    "AI-inferred market relevance probe. Validate before using as client-facing fact."
)


@dataclass(frozen=True)
class MarketRelevanceProbeResult:
    market_lock_status: str
    local_brand_presence_signal: str
    visible_market_fit: list[dict]
    global_default_risk_reason: str
    market_evidence_gap_summary: str
    recommended_interpretation: str
    validation_note: str


def _coerce_number(value, default=0):
    try:
        numeric_value = pd.to_numeric(value, errors="coerce")
    except Exception:
        return default

    if pd.isna(numeric_value):
        return default

    return numeric_value.item() if hasattr(numeric_value, "item") else numeric_value


def build_top_visible_brands_context(summary_df, target_brand, limit=5):
    if summary_df is None or getattr(summary_df, "empty", True):
        return []
    if "brand" not in summary_df.columns:
        return []

    visible_df = summary_df.copy()
    for column in [
        "total_mentions",
        "average_visibility_score",
        "prompts_visible",
        "share_of_voice_percent",
    ]:
        if column not in visible_df.columns:
            visible_df[column] = 0
        visible_df[column] = pd.to_numeric(
            visible_df[column],
            errors="coerce",
        ).fillna(0)

    visible_df = visible_df[
        visible_df["brand"].astype(str).str.lower()
        != str(target_brand).lower()
    ].copy()
    visible_df = visible_df[
        (visible_df["total_mentions"] > 0)
        | (visible_df["average_visibility_score"] > 0)
        | (visible_df["prompts_visible"] > 0)
        | (visible_df["share_of_voice_percent"] > 0)
    ].copy()

    if visible_df.empty:
        return []

    visible_df = visible_df.sort_values(
        by=["average_visibility_score", "total_mentions", "share_of_voice_percent"],
        ascending=False,
    ).head(limit)

    return [
        {
            "brand": str(row.get("brand", "")).strip(),
            "total_mentions": int(_coerce_number(row.get("total_mentions", 0))),
            "average_visibility_score": float(
                _coerce_number(row.get("average_visibility_score", 0))
            ),
            "prompts_visible": int(_coerce_number(row.get("prompts_visible", 0))),
            "share_of_voice_percent": float(
                _coerce_number(row.get("share_of_voice_percent", 0))
            ),
        }
        for _, row in visible_df.iterrows()
        if str(row.get("brand", "")).strip()
    ]


def build_query_winners_context(detailed_df, limit=10):
    required_columns = {"prompt_category", "brand", "visibility_score"}
    if detailed_df is None or getattr(detailed_df, "empty", True):
        return []
    if not required_columns.issubset(set(detailed_df.columns)):
        return []

    winners_df = detailed_df.copy()
    winners_df["visibility_score"] = pd.to_numeric(
        winners_df["visibility_score"],
        errors="coerce",
    ).fillna(0)
    winners_df = winners_df[winners_df["visibility_score"] > 0].copy()

    if winners_df.empty:
        return []

    winners_df = (
        winners_df.sort_values("visibility_score", ascending=False)
        .groupby("prompt_category")
        .first()
        .reset_index()
        .head(limit)
    )

    return [
        {
            "prompt_category": str(row.get("prompt_category", "")).strip(),
            "brand": str(row.get("brand", "")).strip(),
            "visibility_score": float(_coerce_number(row.get("visibility_score", 0))),
        }
        for _, row in winners_df.iterrows()
        if str(row.get("prompt_category", "")).strip()
        and str(row.get("brand", "")).strip()
    ]


def _get_field(value, field, default=""):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)


def build_brand_understanding_context(brand_understanding):
    if not brand_understanding:
        return None

    return {
        "brand_known_status": _get_field(brand_understanding, "brand_known_status"),
        "category_alignment": _get_field(brand_understanding, "category_alignment"),
        "market_alignment": _get_field(brand_understanding, "market_alignment"),
        "audience_alignment": _get_field(brand_understanding, "audience_alignment"),
        "diagnosis_summary": _get_field(brand_understanding, "diagnosis_summary"),
        "recommended_interpretation": _get_field(
            brand_understanding,
            "recommended_interpretation",
        ),
    }


def build_market_relevance_prompt(
    *,
    brand,
    category,
    market,
    audience,
    visible_brands=None,
    query_winners=None,
    prompt_categories=None,
    brand_understanding=None,
):
    visible_brands = visible_brands or []
    query_winners = query_winners or []
    prompt_categories = prompt_categories or []
    brand_understanding_context = build_brand_understanding_context(
        brand_understanding
    )

    return f"""
You are running a Market Relevance Probe for an AI visibility benchmark.

Target Brand:
{brand}

Target Category:
{category}

Target Market / Geography:
{market}

Target Audience:
{audience}

Benchmark Context:
Top visible brands from the benchmark summary:
{json.dumps(visible_brands, ensure_ascii=False)}

Query winners by prompt category:
{json.dumps(query_winners, ensure_ascii=False)}

Prompt categories:
{json.dumps(prompt_categories, ensure_ascii=False)}

Brand Understanding Probe context, if available:
{json.dumps(brand_understanding_context, ensure_ascii=False)}

Task:
Evaluate whether the benchmark answer set appears to respect the target market constraint, or whether it may be defaulting to globally visible category leaders.

Return ONLY valid JSON with this exact schema:
{{
  "market_lock_status": "Market-specific | Partially market-specific | Global-default risk | Insufficient evidence",
  "local_brand_presence_signal": "Clear | Partial | Weak | Not Enough Evidence",
  "visible_market_fit": [
    {{
      "brand": "string",
      "market_fit": "Market-relevant | Global-default | Unclear",
      "rationale": "string"
    }}
  ],
  "global_default_risk_reason": "string",
  "market_evidence_gap_summary": "string",
  "recommended_interpretation": "Market evidence gap | Global-default retrieval risk | Market-specific competitive gap | Insufficient evidence | Mixed diagnosis",
  "validation_note": "AI-inferred market relevance probe. Validate before using as client-facing fact."
}}

Rules:
- Evaluate only the provided benchmark context and AI-inferred signals.
- Do not claim external verification or live market facts.
- Use cautious language.
- If visible brands are globally famous category leaders but the context does not show local, regional, or market-specific alternatives, use Global-default risk or Partially market-specific as appropriate.
- If visible brands appear genuinely relevant to the target market, use Market-specific or Partially market-specific.
- If the benchmark context is too thin, use Insufficient evidence.
- Keep visible_market_fit compact and include no more than five brands.
- Do not include markdown, commentary, or text outside the JSON object.
""".strip()


def build_fallback_market_relevance_result(
    brand=None,
    category=None,
    market=None,
    audience=None,
):
    market_text = str(market or "the target market").strip() or "the target market"
    return MarketRelevanceProbeResult(
        market_lock_status=MARKET_LOCK_INSUFFICIENT_EVIDENCE,
        local_brand_presence_signal=LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE,
        visible_market_fit=[],
        global_default_risk_reason=(
            "The Market Relevance Probe did not return usable structured output."
        ),
        market_evidence_gap_summary=(
            f"Market specificity for {market_text} could not be determined from the structured probe."
        ),
        recommended_interpretation=INTERPRETATION_INSUFFICIENT_EVIDENCE,
        validation_note=VALIDATION_NOTE,
    )


def _normalize_label(value, allowed_labels, default):
    normalized_value = " ".join(str(value or "").strip().split()).lower()
    if not normalized_value:
        return default

    for label in allowed_labels:
        if normalized_value == label.lower():
            return label

    normalized_key = normalized_value.replace("_", " ").replace("-", " ")
    normalized_key = " ".join(normalized_key.split())
    for label in allowed_labels:
        label_key = label.lower().replace("_", " ").replace("-", " ")
        label_key = " ".join(label_key.split())
        if (
            normalized_key == label_key
            or normalized_key.replace(" ", "") == label_key.replace(" ", "")
        ):
            return label

    return default


def _normalize_market_lock_status(value):
    return _normalize_label(
        value,
        ALLOWED_MARKET_LOCK_STATUS_LABELS,
        MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    )


def _normalize_local_signal(value):
    return _normalize_label(
        value,
        ALLOWED_LOCAL_BRAND_PRESENCE_LABELS,
        LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE,
    )


def _normalize_visible_fit(value):
    return _normalize_label(
        value,
        ALLOWED_VISIBLE_BRAND_FIT_LABELS,
        VISIBLE_FIT_UNCLEAR,
    )


def _normalize_recommended_interpretation(value):
    return _normalize_label(
        value,
        ALLOWED_RECOMMENDED_INTERPRETATION_LABELS,
        INTERPRETATION_INSUFFICIENT_EVIDENCE,
    )


def _normalize_text(value):
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _extract_json_object_text(text):
    raw_text = str(text or "").strip()
    if not raw_text:
        return ""

    fenced_match = re.search(
        r"```(?:json)?\s*(?P<body>.*?)```",
        raw_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fenced_match:
        raw_text = fenced_match.group("body").strip()

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return raw_text

    return raw_text[start:end + 1]


def _normalize_visible_market_fit(value):
    if not isinstance(value, list):
        return []

    normalized_rows = []
    for row in value:
        if not isinstance(row, dict):
            continue

        brand = _normalize_text(row.get("brand"))
        if not brand:
            continue

        normalized_rows.append({
            "brand": brand,
            "market_fit": _normalize_visible_fit(row.get("market_fit")),
            "rationale": _normalize_text(row.get("rationale")),
        })

    return normalized_rows


def parse_market_relevance_response(
    response_text,
    *,
    brand=None,
    category=None,
    market=None,
    audience=None,
):
    fallback = build_fallback_market_relevance_result(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
    )

    try:
        data = json.loads(_extract_json_object_text(response_text))
    except Exception:
        return fallback

    if not isinstance(data, dict):
        return fallback

    return MarketRelevanceProbeResult(
        market_lock_status=_normalize_market_lock_status(
            data.get("market_lock_status")
        ),
        local_brand_presence_signal=_normalize_local_signal(
            data.get("local_brand_presence_signal")
        ),
        visible_market_fit=_normalize_visible_market_fit(
            data.get("visible_market_fit")
        ),
        global_default_risk_reason=(
            _normalize_text(data.get("global_default_risk_reason"))
            or fallback.global_default_risk_reason
        ),
        market_evidence_gap_summary=(
            _normalize_text(data.get("market_evidence_gap_summary"))
            or fallback.market_evidence_gap_summary
        ),
        recommended_interpretation=_normalize_recommended_interpretation(
            data.get("recommended_interpretation")
        ),
        validation_note=_normalize_text(data.get("validation_note")) or VALIDATION_NOTE,
    )


def run_market_relevance_probe(
    *,
    brand,
    category,
    market,
    audience,
    summary_df=None,
    detailed_df=None,
    prompt_categories=None,
    brand_understanding=None,
    report_language="English",
    model=None,
):
    selected_model = model or getattr(analyzer, "DEFAULT_MODEL", "gpt-4o-mini")
    visible_brands = build_top_visible_brands_context(summary_df, brand)
    query_winners = build_query_winners_context(detailed_df)
    prompt = build_market_relevance_prompt(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        visible_brands=visible_brands,
        query_winners=query_winners,
        prompt_categories=prompt_categories,
        brand_understanding=brand_understanding,
    )

    try:
        response = analyzer.get_openai_client().chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Answer in {report_language}. You are a strict JSON-only "
                        "market relevance evaluator. Return only a JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=900,
        )
        record_openai_usage(response, fallback_model_name=selected_model)
        content = response.choices[0].message.content
        return parse_market_relevance_response(
            content,
            brand=brand,
            category=category,
            market=market,
            audience=audience,
        )
    except Exception:
        return build_fallback_market_relevance_result(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
        )
