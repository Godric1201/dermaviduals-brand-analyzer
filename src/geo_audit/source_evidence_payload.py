"""Load and validate source evidence payloads.

This module provides a stable input layer for source evidence JSON payloads.
It is used by local CLI tools now and can be reused by Streamlit upload flows
later.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from .source_evidence import (
    normalize_evidence_items,
    validate_evidence_items,
)


@dataclass(frozen=True)
class SourceEvidencePayload:
    """Normalized source evidence payload."""

    target_brand: str
    retrieved_brands: list[str]
    category: str
    market: str
    audience: str
    evidence_items: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Return the payload shape expected by Markdown renderers."""

        return {
            "target_brand": self.target_brand,
            "retrieved_brands": self.retrieved_brands,
            "category": self.category,
            "market": self.market,
            "audience": self.audience,
            "evidence_items": self.evidence_items,
        }


@dataclass(frozen=True)
class SourceEvidencePayloadResult:
    """Result of loading and validating a source evidence payload."""

    payload: SourceEvidencePayload | None
    errors: list[str]

    @property
    def ok(self) -> bool:
        return self.payload is not None and not self.errors


def _as_non_empty_string(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
CSV_TOP_LEVEL_FIELDS = [
    "target_brand",
    "retrieved_brands",
    "category",
    "market",
    "audience",
]

CSV_EVIDENCE_ITEM_FIELDS = [
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
    "freshness_date",
    "validation_status",
    "notes",
]


def _first_non_empty_csv_value(rows: list[dict[str, Any]], field: str) -> str:
    for row in rows:
        value = _as_non_empty_string(row.get(field))
        if value:
            return value
    return ""


def _parse_csv_retrieved_brands(value: str) -> list[str]:
    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def _csv_row_has_evidence_item(row: dict[str, Any]) -> bool:
    return any(
        _as_non_empty_string(row.get(field))
        for field in CSV_EVIDENCE_ITEM_FIELDS
    )


def _csv_rows_to_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    retrieved_brands_value = _first_non_empty_csv_value(rows, "retrieved_brands")

    evidence_items = [
        {
            field: _as_non_empty_string(row.get(field))
            for field in CSV_EVIDENCE_ITEM_FIELDS
        }
        for row in rows
        if _csv_row_has_evidence_item(row)
    ]

    return {
        "target_brand": _first_non_empty_csv_value(rows, "target_brand"),
        "retrieved_brands": _parse_csv_retrieved_brands(retrieved_brands_value),
        "category": _first_non_empty_csv_value(rows, "category"),
        "market": _first_non_empty_csv_value(rows, "market"),
        "audience": _first_non_empty_csv_value(rows, "audience"),
        "evidence_items": evidence_items,
    }

def validate_source_evidence_payload(raw: Any) -> SourceEvidencePayloadResult:
    """Validate and normalize a raw source evidence payload object."""

    errors: list[str] = []

    if not isinstance(raw, dict):
        return SourceEvidencePayloadResult(
            payload=None,
            errors=["payload: expected JSON object"],
        )

    target_brand = _as_non_empty_string(raw.get("target_brand"))
    retrieved_brands = _normalize_string_list(raw.get("retrieved_brands"))
    category = _as_non_empty_string(raw.get("category"))
    market = _as_non_empty_string(raw.get("market"))
    audience = _as_non_empty_string(raw.get("audience"))

    if not target_brand:
        errors.append("target_brand: required")
    if not retrieved_brands:
        errors.append("retrieved_brands: must contain at least one brand")

    raw_evidence_items = raw.get("evidence_items")
    if not isinstance(raw_evidence_items, list):
        errors.append("evidence_items: expected list")
        raw_evidence_items = []

    evidence_items = normalize_evidence_items(raw_evidence_items)
    validation_errors = validate_evidence_items(evidence_items)
    errors.extend(
        f"evidence_items[{error.index}].{error.field}: {error.message}"
        for error in validation_errors
    )

    if errors:
        return SourceEvidencePayloadResult(payload=None, errors=errors)

    payload = SourceEvidencePayload(
        target_brand=target_brand,
        retrieved_brands=retrieved_brands,
        category=category,
        market=market,
        audience=audience,
        evidence_items=evidence_items,
    )
    return SourceEvidencePayloadResult(payload=payload, errors=[])


def load_source_evidence_payload_from_text(text: str) -> SourceEvidencePayloadResult:
    """Load and validate a source evidence payload from JSON text."""

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=[f"json: {exc.msg} at line {exc.lineno}, column {exc.colno}"],
        )

    return validate_source_evidence_payload(raw)

def load_source_evidence_payload_from_csv_text(text: str) -> SourceEvidencePayloadResult:
    """Load and validate a source evidence payload from CSV text."""

    try:
        reader = csv.DictReader(StringIO(text))
        if not reader.fieldnames:
            return SourceEvidencePayloadResult(
                payload=None,
                errors=["csv: expected header row"],
            )
        rows = list(reader)
    except csv.Error as exc:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=[f"csv: {exc}"],
        )

    if not rows:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=["csv: expected at least one evidence row"],
        )

    raw_payload = _csv_rows_to_payload(rows)
    return validate_source_evidence_payload(raw_payload)

def load_source_evidence_payload(path: Path) -> SourceEvidencePayloadResult:
    """Load and validate a source evidence payload from a JSON file."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=[f"file: {exc}"],
        )

    return load_source_evidence_payload_from_text(text)

def load_source_evidence_payload_from_csv(path: Path) -> SourceEvidencePayloadResult:
    """Load and validate a source evidence payload from a CSV file."""

    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=[f"file: {exc}"],
        )

    return load_source_evidence_payload_from_csv_text(text)

def format_source_evidence_payload_errors(errors: list[str]) -> str:
    """Format payload validation errors for CLI or UI display."""

    if not errors:
        return ""

    return "Source evidence payload has validation errors:\n" + "\n".join(
        f"- {error}" for error in errors
    )