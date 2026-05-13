"""Markdown rendering helpers for source-grounded evidence summaries.

This module is deterministic and local-only. It does not perform web search,
scraping, OpenAI calls, Streamlit UI work, or DOCX export.
"""

from __future__ import annotations

from typing import Any

from geo_audit.source_evidence import (
    compare_target_vs_retrieved_evidence,
    group_evidence_by_brand,
    normalize_evidence_items,
    summarize_evidence_coverage,
    summarize_evidence_gap_rows,
    validate_evidence_items,
)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Render a simple Markdown table."""

    if not rows:
        return "_No rows available._"

    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = [
        "| " + " | ".join(str(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([header_line, divider_line, *row_lines])


def format_compact_list(items: list[str]) -> str:
    """Render a compact comma-separated list for Markdown tables."""

    if not items:
        return "None"
    return ", ".join(items)


def render_source_evidence_coverage_table(
    evidence_items: list[dict[str, Any]],
) -> str:
    """Render source evidence coverage by brand."""

    summary = summarize_evidence_coverage(evidence_items)
    rows = [
        [
            row["brand"],
            row["total_items"],
            row["accepted_items"],
            row["high_confidence_items"],
            row["evidence_type_count"],
            format_compact_list(row["evidence_types"]),
        ]
        for row in summary
    ]
    return markdown_table(
        [
            "Brand",
            "Total items",
            "Accepted items",
            "High-confidence items",
            "Evidence type count",
            "Evidence types",
        ],
        rows,
    )


def build_source_evidence_gap_summary(
    evidence_items: list[dict[str, Any]],
    *,
    target_brand: str,
    retrieved_brands: list[str],
) -> list[dict[str, Any]]:
    """Build aggregated source-evidence gap rows."""

    gap_rows = compare_target_vs_retrieved_evidence(
        evidence_items,
        target_brand=target_brand,
        retrieved_brands=retrieved_brands,
    )
    return summarize_evidence_gap_rows(gap_rows)


def render_source_evidence_gap_table(
    gap_summary: list[dict[str, Any]],
) -> str:
    """Render target-vs-retrieved evidence gaps."""

    rows = [
        [
            row["missing_evidence_type"],
            format_compact_list(row["retrieved_brands_with_evidence"]),
            row["retrieved_brand_source_count"],
            row["highest_confidence"],
            format_compact_list(row["supported_retrieval_drivers"]),
        ]
        for row in gap_summary
    ]

    return markdown_table(
        [
            "Missing evidence type",
            "Retrieved brands with evidence",
            "Source count",
            "Highest confidence",
            "Supported retrieval drivers",
        ],
        rows,
    )


def render_source_evidence_priority_assets(
    gap_summary: list[dict[str, Any]],
    *,
    limit: int = 3,
) -> str:
    """Render the first source-evidence assets to build."""

    if not gap_summary:
        return "_No missing evidence assets were identified._"

    blocks = []
    for index, row in enumerate(gap_summary[:limit], start=1):
        blocks.append(
            "\n".join([
                f"**Priority {index} - {row['missing_evidence_type']}**",
                "- Why it matters: Retrieved brands have source evidence for this type, while the target does not.",
                f"- Retrieved-brand signal: {format_compact_list(row['retrieved_brands_with_evidence'])}",
                f"- Supported retrieval drivers: {format_compact_list(row['supported_retrieval_drivers'])}",
                f"- Recommended asset: {row['evidence_asset_recommendation']}",
                "- Validation: Build or improve the evidence asset, then rerun comparable recommendation prompts to check for candidate-set inclusion.",
            ])
        )

    return "\n\n".join(blocks)


def render_source_evidence_appendix(
    evidence_items: list[dict[str, Any]],
) -> str:
    """Render source evidence appendix grouped by brand."""

    grouped = group_evidence_by_brand(evidence_items)
    blocks = []

    for brand in sorted(grouped):
        rows = [
            [
                item.evidence_type,
                item.source_type,
                item.confidence,
                item.validation_status,
                item.source_title,
                item.source_domain,
            ]
            for item in grouped[brand]
        ]
        blocks.append(
            f"### {brand}\n\n"
            + markdown_table(
                [
                    "Evidence type",
                    "Source type",
                    "Confidence",
                    "Status",
                    "Source title",
                    "Domain",
                ],
                rows,
            )
        )

    return "\n\n".join(blocks)


def render_source_evidence_demo_report(payload: dict[str, Any]) -> str:
    """Render a complete deterministic source-evidence demo report."""

    evidence_items = normalize_evidence_items(payload["evidence_items"])
    validation_errors = validate_evidence_items(evidence_items)
    if validation_errors:
        error_lines = [
            f"- item {error.index}, {error.field}: {error.message}"
            for error in validation_errors
        ]
        raise ValueError(
            "Source evidence fixture has validation errors:\n"
            + "\n".join(error_lines)
        )

    coverage_md = render_source_evidence_coverage_table(payload["evidence_items"])
    gap_summary = build_source_evidence_gap_summary(
        payload["evidence_items"],
        target_brand=payload["target_brand"],
        retrieved_brands=payload["retrieved_brands"],
    )
    gap_summary_md = render_source_evidence_gap_table(gap_summary)
    priority_assets_md = render_source_evidence_priority_assets(gap_summary)
    appendix_md = render_source_evidence_appendix(payload["evidence_items"])

    return f"""# Source Evidence Demo Report

> Fictional, deterministic demo output. This report is generated from local fixture data only.
> It does not use OpenAI, Streamlit, web search, scraping, or live client data.

## Demo Context

| Field | Value |
|---|---|
| Target brand | {payload["target_brand"]} |
| Category | {payload["category"]} |
| Market | {payload["market"]} |
| Audience | {payload["audience"]} |
| Retrieved brands | {format_compact_list(payload["retrieved_brands"])} |

## 1. Source Evidence Coverage

This section summarizes accepted source evidence available for the target and retrieved brands.

{coverage_md}

## 2. Target vs Retrieved Evidence Gap

This section identifies evidence types that appear for retrieved brands but are missing for the target brand.

{gap_summary_md}

These gaps are source-evidence gaps to validate. They are not proof that specific sources caused AI retrieval.

## 3. First Evidence Assets to Build

{priority_assets_md}

## 4. Source Evidence Appendix

{appendix_md}

## 5. Methodology Notes

This demo distinguishes observed source evidence from inference and recommended action.

- Observed source evidence: fixture records with source type, confidence, and validation status.
- Source-supported evidence gap: evidence type present for retrieved brands but missing for the target.
- Recommended action: evidence asset to build and validate in a future benchmark.
- Boundary: this report does not claim causality between a source and AI retrieval.
"""