import json
import re
from dataclasses import dataclass

from . import analyzer
from .api_usage import record_openai_usage


STATUS_CLEAR = "Clear"
STATUS_PARTIAL = "Partial"
STATUS_UNCLEAR = "Unclear"
STATUS_MISALIGNED = "Misaligned"
STATUS_NOT_ENOUGH_EVIDENCE = "Not Enough Evidence"

ALLOWED_STATUS_LABELS = (
    STATUS_CLEAR,
    STATUS_PARTIAL,
    STATUS_UNCLEAR,
    STATUS_MISALIGNED,
    STATUS_NOT_ENOUGH_EVIDENCE,
)

INTERPRETATION_ENTITY_UNDERSTANDING_GAP = "Entity understanding gap"
INTERPRETATION_RECOMMENDATION_RETRIEVAL_GAP = "Recommendation retrieval gap"
INTERPRETATION_MARKET_RELEVANCE_GAP = "Market relevance gap"
INTERPRETATION_EVIDENCE_GAP = "Evidence gap"
INTERPRETATION_MIXED_DIAGNOSIS = "Mixed diagnosis"

RECOMMENDED_INTERPRETATION_LABELS = (
    INTERPRETATION_ENTITY_UNDERSTANDING_GAP,
    INTERPRETATION_RECOMMENDATION_RETRIEVAL_GAP,
    INTERPRETATION_MARKET_RELEVANCE_GAP,
    INTERPRETATION_EVIDENCE_GAP,
    INTERPRETATION_MIXED_DIAGNOSIS,
)

VALIDATION_NOTE = (
    "AI-inferred brand understanding probe. Validate before using as client-facing fact."
)


@dataclass(frozen=True)
class BrandUnderstandingProbeResult:
    brand_known_status: str
    inferred_category: str
    category_alignment: str
    inferred_market: str
    market_alignment: str
    inferred_audience: str
    audience_alignment: str
    inferred_offerings: list[str]
    inferred_strengths: list[str]
    missing_or_uncertain_evidence: list[str]
    possible_hallucinations: list[str]
    diagnosis_summary: str
    recommended_interpretation: str
    validation_note: str


def build_brand_understanding_prompt(brand, category, market, audience):
    return f"""
You are running a Brand Understanding Probe before interpreting an AI visibility benchmark.

Target Brand:
{brand}

Target Category:
{category}

Target Market / Geography:
{market}

Target Audience:
{audience}

Task:
Evaluate what the model appears to understand about the target brand before interpreting recommendation visibility results.

Assess:
- What the brand is
- Inferred category or industry
- Inferred market or geography
- Inferred audience
- Inferred offerings or use cases
- Inferred strengths
- Missing or uncertain evidence
- Possible hallucinations or claims that would need verification
- Alignment with the target category, market, and audience
- Recommended interpretation for future visibility reporting

Return ONLY valid JSON with this exact schema:
{{
  "brand_known_status": "Clear | Partial | Unclear | Misaligned | Not Enough Evidence",
  "inferred_category": "string",
  "category_alignment": "Clear | Partial | Unclear | Misaligned | Not Enough Evidence",
  "inferred_market": "string",
  "market_alignment": "Clear | Partial | Unclear | Misaligned | Not Enough Evidence",
  "inferred_audience": "string",
  "audience_alignment": "Clear | Partial | Unclear | Misaligned | Not Enough Evidence",
  "inferred_offerings": ["string"],
  "inferred_strengths": ["string"],
  "missing_or_uncertain_evidence": ["string"],
  "possible_hallucinations": ["string"],
  "diagnosis_summary": "string",
  "recommended_interpretation": "Entity understanding gap | Recommendation retrieval gap | Market relevance gap | Evidence gap | Mixed diagnosis",
  "validation_note": "AI-inferred brand understanding probe. Validate before using as client-facing fact."
}}

Rules:
- Treat the result as AI-inferred, not verified fact.
- Do not claim external validation.
- If the brand is known but not strongly aligned with the target category, market, or audience, use Partial or Misaligned for the relevant alignment field.
- If the brand appears known but evidence is thin, prefer Partial or Not Enough Evidence.
- If the brand appears understood but may fail recommendation retrieval, use Recommendation retrieval gap, Market relevance gap, Evidence gap, or Mixed diagnosis as appropriate.
- If the brand is not understood as an entity, use Entity understanding gap.
- Keep each list compact with no more than five items.
- Do not include markdown, commentary, or text outside the JSON object.
""".strip()


def build_fallback_brand_understanding_result(
    brand=None,
    category=None,
    market=None,
    audience=None,
):
    brand_text = str(brand or "the target brand").strip() or "the target brand"
    return BrandUnderstandingProbeResult(
        brand_known_status=STATUS_NOT_ENOUGH_EVIDENCE,
        inferred_category="",
        category_alignment=STATUS_NOT_ENOUGH_EVIDENCE,
        inferred_market="",
        market_alignment=STATUS_NOT_ENOUGH_EVIDENCE,
        inferred_audience="",
        audience_alignment=STATUS_NOT_ENOUGH_EVIDENCE,
        inferred_offerings=[],
        inferred_strengths=[],
        missing_or_uncertain_evidence=[
            f"The Brand Understanding Probe did not return usable structured output for {brand_text}."
        ],
        possible_hallucinations=[],
        diagnosis_summary=(
            "Brand understanding could not be determined from the structured probe. "
            "Interpret recommendation visibility cautiously."
        ),
        recommended_interpretation=INTERPRETATION_MIXED_DIAGNOSIS,
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
        label_key = label.lower()
        if (
            normalized_key == label_key
            or normalized_key.replace(" ", "") == label_key.replace(" ", "")
        ):
            return label

    return default


def _normalize_status(value, default=STATUS_NOT_ENOUGH_EVIDENCE):
    return _normalize_label(value, ALLOWED_STATUS_LABELS, default)


def _normalize_interpretation(value):
    return _normalize_label(
        value,
        RECOMMENDED_INTERPRETATION_LABELS,
        INTERPRETATION_MIXED_DIAGNOSIS,
    )


def _normalize_text(value):
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _normalize_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        items = value
    elif isinstance(value, tuple):
        items = list(value)
    elif isinstance(value, str):
        items = [value]
    else:
        return []

    normalized_items = []
    for item in items:
        normalized_item = _normalize_text(item)
        if normalized_item:
            normalized_items.append(normalized_item)

    return normalized_items


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


def parse_brand_understanding_response(
    response_text,
    *,
    brand=None,
    category=None,
    market=None,
    audience=None,
):
    fallback = build_fallback_brand_understanding_result(
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

    return BrandUnderstandingProbeResult(
        brand_known_status=_normalize_status(data.get("brand_known_status")),
        inferred_category=_normalize_text(data.get("inferred_category")),
        category_alignment=_normalize_status(data.get("category_alignment")),
        inferred_market=_normalize_text(data.get("inferred_market")),
        market_alignment=_normalize_status(data.get("market_alignment")),
        inferred_audience=_normalize_text(data.get("inferred_audience")),
        audience_alignment=_normalize_status(data.get("audience_alignment")),
        inferred_offerings=_normalize_list(data.get("inferred_offerings")),
        inferred_strengths=_normalize_list(data.get("inferred_strengths")),
        missing_or_uncertain_evidence=_normalize_list(
            data.get("missing_or_uncertain_evidence")
        ),
        possible_hallucinations=_normalize_list(data.get("possible_hallucinations")),
        diagnosis_summary=(
            _normalize_text(data.get("diagnosis_summary"))
            or fallback.diagnosis_summary
        ),
        recommended_interpretation=_normalize_interpretation(
            data.get("recommended_interpretation")
        ),
        validation_note=_normalize_text(data.get("validation_note")) or VALIDATION_NOTE,
    )


def run_brand_understanding_probe(
    *,
    brand,
    category,
    market,
    audience,
    report_language="English",
    model=None,
):
    selected_model = model or getattr(analyzer, "DEFAULT_MODEL", "gpt-4o-mini")
    prompt = build_brand_understanding_prompt(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
    )

    try:
        response = analyzer.get_openai_client().chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Answer in {report_language}. You are a strict JSON-only "
                        "brand understanding evaluator. Return only a JSON object."
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
        return parse_brand_understanding_response(
            content,
            brand=brand,
            category=category,
            market=market,
            audience=audience,
        )
    except Exception:
        return build_fallback_brand_understanding_result(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
        )
