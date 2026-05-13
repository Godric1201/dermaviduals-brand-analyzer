import pytest

from geo_audit.source_evidence_markdown import (
    build_source_evidence_gap_summary,
    markdown_table,
    render_source_evidence_appendix,
    render_source_evidence_coverage_table,
    render_source_evidence_demo_report,
    render_source_evidence_gap_table,
    render_source_evidence_priority_assets,
)


def make_demo_payload():
    return {
        "target_brand": "Example Infrastructure Co.",
        "retrieved_brands": ["Reference Brand A", "Reference Brand B"],
        "category": "Data center infrastructure consulting and project support",
        "market": "Germany",
        "audience": "Enterprise infrastructure buyers",
        "evidence_items": [
            {
                "brand": "Example Infrastructure Co.",
                "evidence_type": "Entity Evidence",
                "source_url": "https://example.test/about",
                "source_title": "About Example",
                "source_domain": "example.test",
                "source_type": "Owned Source",
                "excerpt_or_summary": "Identifies the target brand.",
                "observed_claim": "The target has entity evidence.",
                "supported_retrieval_driver": "Candidate-set inclusion",
                "confidence": "Medium",
                "validation_status": "Observed",
            },
            {
                "brand": "Reference Brand A",
                "evidence_type": "Comparison Evidence",
                "source_url": "https://reference-a.test/alternatives",
                "source_title": "Alternatives guide",
                "source_domain": "reference-a.test",
                "source_type": "Service / Category Page",
                "excerpt_or_summary": "Explains alternatives.",
                "observed_claim": "The reference brand has comparison evidence.",
                "supported_retrieval_driver": "Comparison anchor",
                "confidence": "High",
                "validation_status": "Observed",
            },
            {
                "brand": "Reference Brand B",
                "evidence_type": "Proof / Trust Evidence",
                "source_url": "https://reference-b.test/projects",
                "source_title": "Project proof",
                "source_domain": "reference-b.test",
                "source_type": "Case Study / Reference Project",
                "excerpt_or_summary": "Shows project proof.",
                "observed_claim": "The reference brand has proof evidence.",
                "supported_retrieval_driver": "Trust / premium reference",
                "confidence": "Medium",
                "validation_status": "Observed",
            },
        ],
    }


def test_markdown_table_renders_rows():
    table = markdown_table(["A", "B"], [["one", "two"]])

    assert "| A | B |" in table
    assert "| --- | --- |" in table
    assert "| one | two |" in table


def test_markdown_table_handles_empty_rows():
    assert markdown_table(["A"], []) == "_No rows available._"


def test_render_source_evidence_coverage_table():
    payload = make_demo_payload()

    table = render_source_evidence_coverage_table(payload["evidence_items"])

    assert "Example Infrastructure Co." in table
    assert "Reference Brand A" in table
    assert "Entity Evidence" in table
    assert "Comparison Evidence" in table


def test_build_and_render_source_evidence_gap_summary():
    payload = make_demo_payload()

    summary = build_source_evidence_gap_summary(
        payload["evidence_items"],
        target_brand=payload["target_brand"],
        retrieved_brands=payload["retrieved_brands"],
    )
    table = render_source_evidence_gap_table(summary)

    assert [row["missing_evidence_type"] for row in summary] == [
        "Comparison Evidence",
        "Proof / Trust Evidence",
    ]
    assert "Comparison anchor" in table
    assert "Trust / premium reference" in table


def test_render_source_evidence_priority_assets_limits_to_three():
    gap_summary = [
        {
            "missing_evidence_type": f"Evidence {index}",
            "retrieved_brands_with_evidence": ["Reference Brand"],
            "supported_retrieval_drivers": ["Driver"],
            "evidence_asset_recommendation": "Build evidence.",
        }
        for index in range(1, 5)
    ]

    markdown = render_source_evidence_priority_assets(gap_summary, limit=3)

    assert "Priority 1 - Evidence 1" in markdown
    assert "Priority 3 - Evidence 3" in markdown
    assert "Priority 4 - Evidence 4" not in markdown


def test_render_source_evidence_priority_assets_handles_empty_gaps():
    assert (
        render_source_evidence_priority_assets([])
        == "_No missing evidence assets were identified._"
    )


def test_render_source_evidence_appendix_groups_by_brand():
    payload = make_demo_payload()

    appendix = render_source_evidence_appendix(payload["evidence_items"])

    assert "### Example Infrastructure Co." in appendix
    assert "### Reference Brand A" in appendix
    assert "Alternatives guide" in appendix
    assert "reference-a.test" in appendix


def test_render_source_evidence_demo_report_contains_expected_sections():
    payload = make_demo_payload()

    report = render_source_evidence_demo_report(payload)

    assert "# Source Evidence Demo Report" in report
    assert "## 1. Source Evidence Coverage" in report
    assert "## 2. Target vs Retrieved Evidence Gap" in report
    assert "## 3. First Evidence Assets to Build" in report
    assert "## 4. Source Evidence Appendix" in report
    assert "does not claim causality" in report
    assert "Comparison Evidence" in report
    assert "Proof / Trust Evidence" in report


def test_render_source_evidence_demo_report_rejects_invalid_fixture():
    payload = make_demo_payload()
    payload["evidence_items"][0]["source_url"] = "not-a-url"

    with pytest.raises(ValueError, match="validation errors"):
        render_source_evidence_demo_report(payload)