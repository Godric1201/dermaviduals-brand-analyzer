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


def _load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a source-grounded evidence summary section from a JSON payload."
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to a source evidence JSON payload.",
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


def main() -> None:
    args = parse_args()
    payload = _load_payload(args.input_json)
    summary = render_source_evidence_summary_section(
        payload,
        include_appendix=args.include_appendix,
    )
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(summary + "\n", encoding="utf-8")
    print(f"Wrote {args.output_markdown}")


if __name__ == "__main__":
    main()