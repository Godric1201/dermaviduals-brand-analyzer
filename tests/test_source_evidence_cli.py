import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_source_evidence_summary.py"


def make_payload():
    return {
        "target_brand": "Example Infrastructure Co.",
        "retrieved_brands": ["Reference Brand A"],
        "category": "Data center infrastructure consulting",
        "market": "Germany",
        "audience": "Enterprise buyers",
        "evidence_items": [
            {
                "brand": "Example Infrastructure Co.",
                "evidence_type": "Entity Evidence",
                "source_url": "https://example-infrastructure.test/about",
                "source_title": "About Example Infrastructure Co.",
                "source_domain": "example-infrastructure.test",
                "source_type": "Owned Source",
                "excerpt_or_summary": "Identifies the target brand.",
                "observed_claim": "The target has basic entity evidence.",
                "supported_retrieval_driver": "Candidate-set inclusion",
                "confidence": "Medium",
                "validation_status": "Observed",
            },
            {
                "brand": "Reference Brand A",
                "evidence_type": "Comparison Evidence",
                "source_url": "https://reference-a.test/alternatives",
                "source_title": "Reference Brand A Alternatives Guide",
                "source_domain": "reference-a.test",
                "source_type": "Owned Source",
                "excerpt_or_summary": "Compares Reference Brand A with alternatives.",
                "observed_claim": "Reference Brand A has comparison-oriented public evidence.",
                "supported_retrieval_driver": "Comparison anchor",
                "confidence": "High",
                "validation_status": "Observed",
            },
        ],
    }


def test_render_source_evidence_summary_cli_writes_markdown(tmp_path):
    input_path = tmp_path / "source-evidence.json"
    output_path = tmp_path / "source-evidence-summary.md"
    input_path.write_text(json.dumps(make_payload()), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Wrote" in result.stdout
    rendered = output_path.read_text(encoding="utf-8")
    assert rendered.startswith("## Source-Grounded Evidence Summary")
    assert "### Source Evidence Coverage" in rendered
    assert "### Target vs Retrieved Evidence Gap" in rendered
    assert "Comparison Evidence" in rendered
    assert "not proof that specific sources caused AI retrieval" in rendered
    assert "### Source Evidence Appendix" not in rendered


def test_render_source_evidence_summary_cli_can_include_appendix(tmp_path):
    input_path = tmp_path / "source-evidence.json"
    output_path = tmp_path / "source-evidence-summary.md"
    input_path.write_text(json.dumps(make_payload()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(input_path),
            str(output_path),
            "--include-appendix",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    rendered = output_path.read_text(encoding="utf-8")
    assert "### Source Evidence Appendix" in rendered
    assert "### Example Infrastructure Co." in rendered


def test_render_source_evidence_summary_cli_rejects_invalid_payload(tmp_path):
    input_path = tmp_path / "source-evidence.json"
    output_path = tmp_path / "source-evidence-summary.md"
    payload = make_payload()
    payload["evidence_items"][0]["source_url"] = "not-a-url"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "validation errors" in result.stderr
    assert not output_path.exists()

def test_render_source_evidence_summary_cli_accepts_csv_input(tmp_path):
    input_path = ROOT / "examples" / "skincare-source-evidence-demo.csv"
    output_path = tmp_path / "source-evidence-summary.md"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert output_path.exists()

    output = output_path.read_text(encoding="utf-8")
    assert output.startswith("## Source-Grounded Evidence Summary")
    assert "Example Barrier Skincare" in output
    assert "Clinical Derm Brand A" in output
    assert "Target vs Retrieved Evidence Gap" in output    