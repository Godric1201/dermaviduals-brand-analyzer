"""Render a fictional source-evidence demo report.

This script is intentionally local and deterministic:
- no Streamlit
- no OpenAI calls
- no web search
- no scraping

It converts the fictional example fixture into a compact Markdown report that
shows how source evidence can support Recommendation Readiness Diagnosis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from geo_audit.source_evidence import (  # noqa: E402
    compare_target_vs_retrieved_evidence,
    group_evidence_by_brand,
    normalize_evidence_items,
    summarize_evidence_coverage,
    summarize_evidence_gap_rows,
    validate_evidence_items,
)


INPUT_PATH = ROOT / "examples" / "source-evidence-demo.json"
OUTPUT_PATH = ROOT / "examples" / "source-evidence-demo-report.md"


def _load_demo_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_No rows available._"

    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = [
        "| " + " | ".join(str(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([header_line, divider_line, *row_lines])


def _format_list(items: list[str]) -> str:
    if not items:
        return "None"
    return ", ".join(items)


def _render_evidence_coverage(payload: dict[str, Any]) -> str:
    summary = summarize_evidence_coverage(payload["evidence_items"])
    rows = [
        [
            row["brand"],
            row["total_items"],
            row["accepted_items"],
            row["high_confidence_items"],
            row["evidence_type_count"],
            _format_list(row["evidence_types"]),
        ]
        for row in summary
    ]
    return _markdown_table(
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


def _render_gap_summary(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    gap_rows = compare_target_vs_retrieved_evidence(
        payload["evidence_items"],
        target_brand=payload["target_brand"],
        retrieved_brands=payload["retrieved_brands"],
    )
    gap_summary = summarize_evidence_gap_rows(gap_rows)

    rows = [
        [
            row["missing_evidence_type"],
            _format_list(row["retrieved_brands_with_evidence"]),
            row["retrieved_brand_source_count"],
            row["highest_confidence"],
            _format_list(row["supported_retrieval_drivers"]),
        ]
        for row in gap_summary
    ]

    return (
        _markdown_table(
            [
                "Missing evidence type",
                "Retrieved brands with evidence",
                "Source count",
                "Highest confidence",
                "Supported retrieval drivers",
            ],
            rows,
        ),
        gap_summary,
    )


def _render_priority_assets(gap_summary: list[dict[str, Any]], limit: int = 3) -> str:
    if not gap_summary:
        return "_No missing evidence assets were identified in this demo fixture._"

    blocks = []
    for index, row in enumerate(gap_summary[:limit], start=1):
        blocks.append(
            "\n".join([
                f"**Priority {index} - {row['missing_evidence_type']}**",
                f"- Why it matters: Retrieved brands have source evidence for this type, while the target does not.",
                f"- Retrieved-brand signal: {_format_list(row['retrieved_brands_with_evidence'])}",
                f"- Supported retrieval drivers: {_format_list(row['supported_retrieval_drivers'])}",
                f"- Recommended asset: {row['evidence_asset_recommendation']}",
                "- Validation: Build or improve the evidence asset, then rerun comparable recommendation prompts to check for candidate-set inclusion.",
            ])
        )

    return "\n\n".join(blocks)


def _render_source_appendix(payload: dict[str, Any]) -> str:
    grouped = group_evidence_by_brand(payload["evidence_items"])
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
            + _markdown_table(
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


def render_demo_report(payload: dict[str, Any]) -> str:
    evidence_items = normalize_evidence_items(payload["evidence_items"])
    validation_errors = validate_evidence_items(evidence_items)
    if validation_errors:
        error_lines = [
            f"- item {error.index}, {error.field}: {error.message}"
            for error in validation_errors
        ]
        raise ValueError(
            "Demo evidence fixture has validation errors:\n"
            + "\n".join(error_lines)
        )

    coverage_md = _render_evidence_coverage(payload)
    gap_summary_md, gap_summary = _render_gap_summary(payload)
    priority_assets_md = _render_priority_assets(gap_summary)
    appendix_md = _render_source_appendix(payload)

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
| Retrieved brands | {_format_list(payload["retrieved_brands"])} |

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


def main() -> None:
    payload = _load_demo_payload()
    report = render_demo_report(payload)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()