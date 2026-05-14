"""Render a source-evidence summary section from a JSON payload.

This script is intentionally local and deterministic:
- no Streamlit
- no OpenAI calls
- no web search
- no scraping
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from geo_audit.source_evidence_markdown import render_source_evidence_summary_section  # noqa: E402
from geo_audit.source_evidence_payload import (  # noqa: E402
    format_source_evidence_payload_errors,
    load_source_evidence_payload,
    load_source_evidence_payload_from_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a source-grounded evidence summary section from a JSON or CSV payload."
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Source evidence JSON or CSV input path."
    )
    parser.add_argument(
        "output_markdown",
        type=Path,
        help="Path where the rendered Markdown summary should be written.",
    )
    parser.add_argument(
        "--include-appendix",
        action="store_true",
        help="Include the source evidence appendix in the rendered Markdown.",
    )
    return parser.parse_args()


def load_source_evidence_payload_for_path(path: Path):
    """Load source evidence payload from JSON or CSV based on file extension."""

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return load_source_evidence_payload_from_csv(path)

    return load_source_evidence_payload(path)


def main() -> None:
    args = parse_args()
    result = load_source_evidence_payload_for_path(args.input_json)
    if not result.ok:
        print(format_source_evidence_payload_errors(result.errors), file=sys.stderr)
        raise SystemExit(1)

    summary = render_source_evidence_summary_section(
        result.payload.to_dict(),
        include_appendix=args.include_appendix,
    )
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(summary + "\n", encoding="utf-8")
    print(f"Wrote {args.output_markdown}")


if __name__ == "__main__":
    main()