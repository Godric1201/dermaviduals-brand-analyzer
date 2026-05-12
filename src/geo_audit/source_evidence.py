"""Source-grounded evidence data model and validation helpers.

This module defines the first deterministic data contract for future
source-grounded competitive/evidence research.

It does not perform web search, scraping, OpenAI calls, Streamlit UI work,
or report integration. It only models, normalizes, validates, groups, and
summarizes source evidence items.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


EVIDENCE_ENTITY = "Entity Evidence"
EVIDENCE_CATEGORY = "Category Evidence"
EVIDENCE_MARKET = "Market Evidence"
EVIDENCE_OFFERING_USE_CASE = "Offering / Use-Case Evidence"
EVIDENCE_PROOF_TRUST = "Proof / Trust Evidence"
EVIDENCE_COMPARISON = "Comparison Evidence"
EVIDENCE_THIRD_PARTY = "Third-Party Corroboration"
EVIDENCE_STRUCTURED_DATA = "Structured Data Evidence"
EVIDENCE_RECENCY = "Recency / Freshness Evidence"
EVIDENCE_AUTHORITY = "Authority / Association Evidence"

ALLOWED_EVIDENCE_TYPES = (
    EVIDENCE_ENTITY,
    EVIDENCE_CATEGORY,
    EVIDENCE_MARKET,
    EVIDENCE_OFFERING_USE_CASE,
    EVIDENCE_PROOF_TRUST,
    EVIDENCE_COMPARISON,
    EVIDENCE_THIRD_PARTY,
    EVIDENCE_STRUCTURED_DATA,
    EVIDENCE_RECENCY,
    EVIDENCE_AUTHORITY,
)


SOURCE_OWNED = "Owned Source"
SOURCE_SERVICE_PAGE = "Service / Category Page"
SOURCE_CASE_STUDY = "Case Study / Reference Project"
SOURCE_PARTNER = "Partner Page"
SOURCE_CERTIFICATION = "Certification / Award / Association"
SOURCE_DIRECTORY = "Third-Party Directory"
SOURCE_NEWS = "News / Press Mention"
SOURCE_STRUCTURED_DATA = "Structured Data"
SOURCE_REVIEW_COMMUNITY = "Review / Community Platform"
SOURCE_OTHER = "Other"

ALLOWED_SOURCE_TYPES = (
    SOURCE_OWNED,
    SOURCE_SERVICE_PAGE,
    SOURCE_CASE_STUDY,
    SOURCE_PARTNER,
    SOURCE_CERTIFICATION,
    SOURCE_DIRECTORY,
    SOURCE_NEWS,
    SOURCE_STRUCTURED_DATA,
    SOURCE_REVIEW_COMMUNITY,
    SOURCE_OTHER,
)


CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"
CONFIDENCE_INSUFFICIENT = "Insufficient"

ALLOWED_CONFIDENCE_LEVELS = (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    CONFIDENCE_INSUFFICIENT,
)


STATUS_OBSERVED = "Observed"
STATUS_NEEDS_REVIEW = "Needs Review"
STATUS_STALE = "Stale"
STATUS_CONFLICTING = "Conflicting"
STATUS_REJECTED = "Rejected"

ALLOWED_VALIDATION_STATUSES = (
    STATUS_OBSERVED,
    STATUS_NEEDS_REVIEW,
    STATUS_STALE,
    STATUS_CONFLICTING,
    STATUS_REJECTED,
)


_REQUIRED_FIELDS = (
    "brand",
    "evidence_type",
    "source_url",
    "source_title",
    "source_domain",
    "source_type",
    "excerpt_or_summary",
    "observed_claim",
    "supported_retrieval_driver",
    "confidence",
    "validation_status",
)


_EVIDENCE_TYPE_ALIASES = {
    "entity": EVIDENCE_ENTITY,
    "entity evidence": EVIDENCE_ENTITY,
    "category": EVIDENCE_CATEGORY,
    "category evidence": EVIDENCE_CATEGORY,
    "market": EVIDENCE_MARKET,
    "market evidence": EVIDENCE_MARKET,
    "offering": EVIDENCE_OFFERING_USE_CASE,
    "offering evidence": EVIDENCE_OFFERING_USE_CASE,
    "use case": EVIDENCE_OFFERING_USE_CASE,
    "use-case": EVIDENCE_OFFERING_USE_CASE,
    "offering / use-case evidence": EVIDENCE_OFFERING_USE_CASE,
    "proof": EVIDENCE_PROOF_TRUST,
    "trust": EVIDENCE_PROOF_TRUST,
    "proof / trust evidence": EVIDENCE_PROOF_TRUST,
    "comparison": EVIDENCE_COMPARISON,
    "comparison evidence": EVIDENCE_COMPARISON,
    "third party": EVIDENCE_THIRD_PARTY,
    "third-party": EVIDENCE_THIRD_PARTY,
    "third-party corroboration": EVIDENCE_THIRD_PARTY,
    "structured data": EVIDENCE_STRUCTURED_DATA,
    "structured data evidence": EVIDENCE_STRUCTURED_DATA,
    "recency": EVIDENCE_RECENCY,
    "freshness": EVIDENCE_RECENCY,
    "recency / freshness evidence": EVIDENCE_RECENCY,
    "authority": EVIDENCE_AUTHORITY,
    "association": EVIDENCE_AUTHORITY,
    "authority / association evidence": EVIDENCE_AUTHORITY,
}

_SOURCE_TYPE_ALIASES = {
    "owned": SOURCE_OWNED,
    "owned source": SOURCE_OWNED,
    "official": SOURCE_OWNED,
    "official website": SOURCE_OWNED,
    "service": SOURCE_SERVICE_PAGE,
    "category page": SOURCE_SERVICE_PAGE,
    "service / category page": SOURCE_SERVICE_PAGE,
    "case study": SOURCE_CASE_STUDY,
    "reference project": SOURCE_CASE_STUDY,
    "case study / reference project": SOURCE_CASE_STUDY,
    "partner": SOURCE_PARTNER,
    "partner page": SOURCE_PARTNER,
    "certification": SOURCE_CERTIFICATION,
    "award": SOURCE_CERTIFICATION,
    "association": SOURCE_CERTIFICATION,
    "certification / award / association": SOURCE_CERTIFICATION,
    "directory": SOURCE_DIRECTORY,
    "third-party directory": SOURCE_DIRECTORY,
    "news": SOURCE_NEWS,
    "press": SOURCE_NEWS,
    "news / press mention": SOURCE_NEWS,
    "schema": SOURCE_STRUCTURED_DATA,
    "structured data": SOURCE_STRUCTURED_DATA,
    "review": SOURCE_REVIEW_COMMUNITY,
    "community": SOURCE_REVIEW_COMMUNITY,
    "review / community platform": SOURCE_REVIEW_COMMUNITY,
    "other": SOURCE_OTHER,
}

_CONFIDENCE_ALIASES = {
    "high": CONFIDENCE_HIGH,
    "medium": CONFIDENCE_MEDIUM,
    "med": CONFIDENCE_MEDIUM,
    "low": CONFIDENCE_LOW,
    "insufficient": CONFIDENCE_INSUFFICIENT,
    "not enough evidence": CONFIDENCE_INSUFFICIENT,
}

_STATUS_ALIASES = {
    "observed": STATUS_OBSERVED,
    "needs review": STATUS_NEEDS_REVIEW,
    "needs_review": STATUS_NEEDS_REVIEW,
    "review": STATUS_NEEDS_REVIEW,
    "stale": STATUS_STALE,
    "conflicting": STATUS_CONFLICTING,
    "conflict": STATUS_CONFLICTING,
    "rejected": STATUS_REJECTED,
    "reject": STATUS_REJECTED,
}


@dataclass(frozen=True)
class EvidenceItem:
    """A normalized source-grounded evidence record."""

    brand: str
    evidence_type: str
    source_url: str
    source_title: str
    source_domain: str
    source_type: str
    excerpt_or_summary: str
    observed_claim: str
    supported_retrieval_driver: str
    confidence: str
    validation_status: str
    freshness_date: str = ""
    notes: str = ""


@dataclass(frozen=True)
class EvidenceValidationError:
    """Validation issue for one evidence item."""

    index: int
    field: str
    message: str


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _normalize_label(value: Any, aliases: dict[str, str], allowed_values: tuple[str, ...]) -> str:
    cleaned = _clean_text(value)
    if not cleaned:
        return ""

    key = cleaned.lower()
    if key in aliases:
        return aliases[key]

    for allowed_value in allowed_values:
        if key == allowed_value.lower():
            return allowed_value

    return cleaned


def _normalize_domain(value: Any) -> str:
    cleaned = _clean_text(value).lower()
    cleaned = cleaned.replace("https://", "").replace("http://", "")
    cleaned = cleaned.split("/", 1)[0]
    return cleaned


def _is_valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalize_evidence_item(raw: EvidenceItem | dict[str, Any]) -> EvidenceItem:
    """Normalize a raw evidence dict or EvidenceItem into an EvidenceItem.

    Normalization is intentionally conservative. It canonicalizes known labels
    and strips whitespace, but it does not silently accept invalid records.
    Use validate_evidence_item or validate_evidence_items for validation.
    """

    if isinstance(raw, EvidenceItem):
        raw_data: dict[str, Any] = raw.__dict__
    elif isinstance(raw, dict):
        raw_data = raw
    else:
        raise TypeError("raw evidence must be an EvidenceItem or dict")

    return EvidenceItem(
        brand=_clean_text(raw_data.get("brand")),
        evidence_type=_normalize_label(
            raw_data.get("evidence_type"),
            _EVIDENCE_TYPE_ALIASES,
            ALLOWED_EVIDENCE_TYPES,
        ),
        source_url=_clean_text(raw_data.get("source_url")),
        source_title=_clean_text(raw_data.get("source_title")),
        source_domain=_normalize_domain(raw_data.get("source_domain")),
        source_type=_normalize_label(
            raw_data.get("source_type"),
            _SOURCE_TYPE_ALIASES,
            ALLOWED_SOURCE_TYPES,
        ),
        excerpt_or_summary=_clean_text(raw_data.get("excerpt_or_summary")),
        observed_claim=_clean_text(raw_data.get("observed_claim")),
        supported_retrieval_driver=_clean_text(
            raw_data.get("supported_retrieval_driver")
        ),
        confidence=_normalize_label(
            raw_data.get("confidence") or CONFIDENCE_INSUFFICIENT,
            _CONFIDENCE_ALIASES,
            ALLOWED_CONFIDENCE_LEVELS,
        ),
        validation_status=_normalize_label(
            raw_data.get("validation_status") or STATUS_NEEDS_REVIEW,
            _STATUS_ALIASES,
            ALLOWED_VALIDATION_STATUSES,
        ),
        freshness_date=_clean_text(raw_data.get("freshness_date")),
        notes=_clean_text(raw_data.get("notes")),
    )


def validate_evidence_item(
    item: EvidenceItem | dict[str, Any],
    *,
    index: int = 0,
) -> list[EvidenceValidationError]:
    """Return validation errors for one evidence item."""

    normalized = normalize_evidence_item(item)
    errors: list[EvidenceValidationError] = []

    for field in _REQUIRED_FIELDS:
        if not getattr(normalized, field):
            errors.append(
                EvidenceValidationError(
                    index=index,
                    field=field,
                    message=f"{field} is required",
                )
            )

    if normalized.evidence_type and normalized.evidence_type not in ALLOWED_EVIDENCE_TYPES:
        errors.append(
            EvidenceValidationError(
                index=index,
                field="evidence_type",
                message=f"Unsupported evidence type: {normalized.evidence_type}",
            )
        )

    if normalized.source_type and normalized.source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(
            EvidenceValidationError(
                index=index,
                field="source_type",
                message=f"Unsupported source type: {normalized.source_type}",
            )
        )

    if normalized.confidence and normalized.confidence not in ALLOWED_CONFIDENCE_LEVELS:
        errors.append(
            EvidenceValidationError(
                index=index,
                field="confidence",
                message=f"Unsupported confidence level: {normalized.confidence}",
            )
        )

    if (
        normalized.validation_status
        and normalized.validation_status not in ALLOWED_VALIDATION_STATUSES
    ):
        errors.append(
            EvidenceValidationError(
                index=index,
                field="validation_status",
                message=f"Unsupported validation status: {normalized.validation_status}",
            )
        )

    if normalized.source_url and not _is_valid_http_url(normalized.source_url):
        errors.append(
            EvidenceValidationError(
                index=index,
                field="source_url",
                message="source_url must be an http(s) URL",
            )
        )

    return errors


def validate_evidence_items(
    items: list[EvidenceItem | dict[str, Any]],
) -> list[EvidenceValidationError]:
    """Return validation errors for a list of evidence items."""

    errors: list[EvidenceValidationError] = []
    for index, item in enumerate(items):
        errors.extend(validate_evidence_item(item, index=index))
    return errors


def normalize_evidence_items(
    items: list[EvidenceItem | dict[str, Any]],
) -> list[EvidenceItem]:
    """Normalize a list of evidence items."""

    return [normalize_evidence_item(item) for item in items]


def group_evidence_by_brand(
    items: list[EvidenceItem | dict[str, Any]],
) -> dict[str, list[EvidenceItem]]:
    """Group normalized evidence items by brand."""

    grouped: dict[str, list[EvidenceItem]] = {}
    for item in normalize_evidence_items(items):
        if not item.brand:
            continue
        grouped.setdefault(item.brand, []).append(item)
    return grouped


def _is_accepted_for_summary(item: EvidenceItem) -> bool:
    return item.validation_status in {
        STATUS_OBSERVED,
        STATUS_NEEDS_REVIEW,
        STATUS_STALE,
    }


def summarize_evidence_coverage(
    items: list[EvidenceItem | dict[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize evidence coverage by brand.

    Rejected and conflicting records are still counted in total_items but are
    excluded from accepted_items and evidence type coverage.
    """

    grouped = group_evidence_by_brand(items)
    summary_rows: list[dict[str, Any]] = []

    for brand in sorted(grouped):
        brand_items = grouped[brand]
        accepted_items = [
            item for item in brand_items
            if _is_accepted_for_summary(item)
        ]
        evidence_types = sorted({
            item.evidence_type
            for item in accepted_items
            if item.evidence_type
        })
        high_confidence_items = [
            item for item in accepted_items
            if item.confidence == CONFIDENCE_HIGH
        ]

        summary_rows.append({
            "brand": brand,
            "total_items": len(brand_items),
            "accepted_items": len(accepted_items),
            "high_confidence_items": len(high_confidence_items),
            "evidence_types": evidence_types,
            "evidence_type_count": len(evidence_types),
        })

    return summary_rows
