import json
import sys
from pathlib import Path
from geo_audit.source_evidence_payload import load_source_evidence_payload_from_csv

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from geo_audit.source_evidence_markdown import (  # noqa: E402
    render_source_evidence_demo_report,
    render_source_evidence_summary_section,
)

def test_source_evidence_summary_example_matches_renderer():
    payload_path = ROOT / "examples" / "source-evidence-demo.json"
    example_path = ROOT / "examples" / "source-evidence-summary.md"

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    expected = render_source_evidence_summary_section(payload).rstrip() + "\n"
    actual = example_path.read_text(encoding="utf-8")

    assert actual == expected

def test_source_evidence_demo_report_example_matches_renderer():
    payload_path = ROOT / "examples" / "source-evidence-demo.json"
    example_path = ROOT / "examples" / "source-evidence-demo-report.md"

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    expected = render_source_evidence_demo_report(payload).rstrip() + "\n"
    actual = example_path.read_text(encoding="utf-8")

    assert actual == expected

def test_skincare_source_evidence_summary_example_matches_renderer():
    payload_path = ROOT / "examples" / "skincare-source-evidence-demo.json"
    example_path = ROOT / "examples" / "skincare-source-evidence-summary.md"

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    expected = render_source_evidence_summary_section(payload).rstrip() + "\n"
    actual = example_path.read_text(encoding="utf-8")

    assert actual == expected

def test_skincare_source_evidence_csv_fixture_renders_summary():
    payload_path = ROOT / "examples" / "skincare-source-evidence-demo.csv"

    result = load_source_evidence_payload_from_csv(payload_path)

    assert result.ok

    summary = render_source_evidence_summary_section(result.payload.to_dict())

    assert summary.startswith("## Source-Grounded Evidence Summary")
    assert "Example Barrier Skincare" in summary
    assert "Clinical Derm Brand A" in summary
    assert "Target vs Retrieved Evidence Gap" in summary
    assert "First Source Evidence Assets to Build" in summary