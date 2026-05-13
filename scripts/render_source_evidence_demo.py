"""Render a fictional source-evidence demo report.

This script is intentionally local and deterministic:
- no Streamlit
- no OpenAI calls
- no web search
- no scraping
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from geo_audit.source_evidence_markdown import render_source_evidence_demo_report  # noqa: E402


INPUT_PATH = ROOT / "examples" / "source-evidence-demo.json"
OUTPUT_PATH = ROOT / "examples" / "source-evidence-demo-report.md"


def _load_demo_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def main() -> None:
    payload = _load_demo_payload()
    report = render_source_evidence_demo_report(payload)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()