import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from geo_audit.source_evidence_markdown import render_source_evidence_summary_section  # noqa: E402


def test_source_evidence_summary_example_matches_renderer():
    payload_path = ROOT / "examples" / "source-evidence-demo.json"
    example_path = ROOT / "examples" / "source-evidence-summary.md"

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    expected = render_source_evidence_summary_section(payload).rstrip() + "\n"
    actual = example_path.read_text(encoding="utf-8")

    assert actual == expected