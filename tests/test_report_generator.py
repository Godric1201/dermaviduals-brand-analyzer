from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd

from output_quality import FAILED_LLM_SECTION_PLACEHOLDER
from report_generator import create_executive_docx_report, parse_markdown_table


def create_fake_report_inputs():
    summary_df = pd.DataFrame([
        {
            "brand": "Dermaviduals",
            "total_mentions": 2,
            "average_visibility_score": 3.5,
            "prompts_visible": 1,
            "share_of_voice_percent": 20.0,
        },
        {
            "brand": "Competitor Brand",
            "total_mentions": 8,
            "average_visibility_score": 7.2,
            "prompts_visible": 3,
            "share_of_voice_percent": 80.0,
        },
    ])

    top_winners_df = pd.DataFrame([
        {
            "prompt_category": "Sensitive skin",
            "brand": "Competitor Brand",
            "visibility_score": 8.0,
        }
    ])

    return summary_df, top_winners_df


def create_all_zero_report_inputs():
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Einstein Kaffee",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
    ])

    return summary_df, pd.DataFrame()


def create_test_report(**kwargs):
    summary_df, top_winners_df = create_fake_report_inputs()

    report_kwargs = {
        "brand": "Dermaviduals",
        "category": "skincare products",
        "market": "Hong Kong",
        "audience": "skincare-conscious consumers in Hong Kong",
        "summary_df": summary_df,
        "top_brands_df": top_winners_df,
        "recommendations": "Test recommendations",
        "strategy_report": "Test strategy report",
        "gap_analysis": "Test gap analysis",
    }
    report_kwargs.update(kwargs)

    return create_executive_docx_report(**report_kwargs)


def assert_valid_docx_bytes(report_bytes):

    assert isinstance(report_bytes, bytes)
    assert len(report_bytes) > 0
    assert report_bytes.startswith(b"PK")


def read_document_xml(report_bytes):
    with ZipFile(BytesIO(report_bytes)) as docx:
        return docx.read("word/document.xml").decode("utf-8")


def read_document_text(report_bytes):
    document_xml = read_document_xml(report_bytes)
    root = ET.fromstring(document_xml)

    return "\n".join(
        node.text
        for node in root.iter()
        if node.tag.endswith("}t") and node.text
    )


def section_text_between(text, start, end):
    start_index = text.find(start)
    end_index = text.find(end, start_index)

    assert start_index != -1
    assert end_index != -1

    return text[start_index:end_index]


def test_create_executive_docx_report_returns_docx_bytes():
    report_bytes = create_test_report()

    assert_valid_docx_bytes(report_bytes)
    document_xml = read_document_xml(report_bytes)

    assert "Brand Intelligence" not in document_xml
    assert "GEO Content Roadmap" not in document_xml
    assert "Query intent coverage" not in document_xml


def test_create_executive_docx_report_supports_quick_test_mode_metadata():
    report_bytes = create_test_report(
        run_mode="Quick Test Mode",
        prompt_limit=1,
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)

    assert "TEST VERSION ONLY" in document_xml
    assert "Not Client Deliverable" in document_xml


def test_create_executive_docx_report_guards_raw_llm_errors_in_quick_test():
    report_bytes = create_test_report(
        run_mode="Quick Test Mode",
        prompt_limit=1,
        strategy_report="ERROR: Connection error.",
        gap_analysis="ERROR: Connection error.",
        brand_intelligence={
            "recommendation_drivers": "ERROR: Connection error.",
            "target_brand_understanding": "ERROR: Connection error.",
            "positioning_gap_analysis": "ERROR: Connection error.",
        },
        geo_content_roadmap="ERROR: Connection error.",
    )

    text = read_document_text(report_bytes)

    assert "ERROR:" not in text
    assert "Connection error" not in text
    assert FAILED_LLM_SECTION_PLACEHOLDER in text


def test_create_executive_docx_report_uses_generic_category_wording():
    report_bytes = create_test_report(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)

    blocked_terms = [
        "professional skincare",
        "sensitive skin",
        "barrier repair",
        "clinic-grade",
        "post-treatment",
        "Hong Kong clinic-grade skincare",
        "clinical performance",
        "professional third-party recommendation signals",
    ]

    for term in blocked_terms:
        assert term not in document_xml

    document_xml_lower = document_xml.lower()

    assert "cafes" in document_xml_lower
    assert "berlin" in document_xml_lower
    assert "best cafes options" not in document_xml_lower
    assert "decision-stage cafes searches" in document_xml_lower
    assert "third-party trust or recommendation signals" in document_xml_lower
    assert "business outcomes" in document_xml_lower


def test_create_executive_docx_report_handles_all_zero_visibility_without_fake_leaders():
    summary_df, top_winners_df = create_all_zero_report_inputs()

    report_bytes = create_test_report(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        summary_df=summary_df,
        top_brands_df=top_winners_df,
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)

    blocked_phrases = [
        "creating a stronger AI recall signal",
        "The highest mention brand is",
        "The highest average visibility brand is",
        "The highest share-of-voice brand is",
    ]

    for phrase in blocked_phrases:
        assert phrase not in document_xml

    assert "No benchmark competitor generated measurable" in document_xml
    assert "does not identify a stronger competitor leader" in document_xml

    document_text = read_document_text(report_bytes)
    priorities_text = section_text_between(
        document_text,
        "Strategic Priorities",
        "30 / 60 / 90 Day Roadmap",
    )
    roadmap_text = section_text_between(
        document_text,
        "30 / 60 / 90 Day Roadmap",
        "Measurement Plan",
    )

    assert "Coffee Fellows" not in priorities_text
    assert "Einstein Kaffee" not in priorities_text
    assert "Coffee Fellows" not in roadmap_text
    assert "Einstein Kaffee" not in roadmap_text

    assert "No measurable competitor leader" in priorities_text
    assert "Tracked competitors not measurably visible" in priorities_text
    assert "Category baseline" in roadmap_text
    assert "Market visibility baseline" in roadmap_text
    assert "Tracked competitor set" in roadmap_text


def test_create_executive_docx_report_includes_brand_intelligence_when_provided():
    report_bytes = create_test_report(
        brand_intelligence={
            "recommendation_drivers": (
                "### Recurring Recommendation Drivers\n"
                "Test recommendation drivers"
            ),
            "target_brand_understanding": (
                "#### AI-Inferred Strengths\n"
                "Test target brand understanding\n"
                "#### Weak Associations\n"
                "Test weak associations\n"
                "### Recommendation Likelihood\n"
                "Legacy heading that should be normalized"
            ),
            "positioning_gap_analysis": "Test positioning gap analysis",
        }
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)

    expected_terms = [
        "Appendix",
        "Brand Intelligence",
        "Recommendation Drivers",
        "AI-Inferred Target Brand Understanding",
        "Positioning Gap Analysis",
        "Diagnostic insight",
        "Tracked competitors",
        "AI-discovered market signals",
        "not included in scoring",
        "selected as tracked competitors before the benchmark run",
        "Recurring Recommendation Drivers",
        "AI-Inferred Strengths",
        "Weak Associations",
        "Prompted Diagnostic Fit",
        "Test recommendation drivers",
        "Test target brand understanding",
        "Test positioning gap analysis",
    ]

    for term in expected_terms:
        assert term in document_xml

    blocked_terms = [
        "### Recurring Recommendation Drivers",
        "#### Weak Associations",
        "### Recommendation Likelihood",
    ]

    for term in blocked_terms:
        assert term not in document_xml

    document_text = read_document_text(report_bytes)
    assert (
        document_text.find("Methodology Notes")
        < document_text.find("Appendix: Brand Intelligence & Positioning Audit")
    )


def test_create_executive_docx_report_includes_query_intent_coverage_when_provided():
    report_bytes = create_test_report(
        prompt_categories=[
            "Best Options",
            "Local Recommendations",
        ]
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)

    expected_terms = [
        "Query intent coverage",
        "Best Options",
        "Local Recommendations",
    ]

    for term in expected_terms:
        assert term in document_xml


def test_parse_markdown_table_returns_dataframe():
    roadmap = """
| Priority | Query Intent | Content Asset |
|---|---|---|
| 1 | Best Options | Comparison page |
"""

    df = parse_markdown_table(roadmap)

    assert df.to_dict(orient="records") == [
        {
            "Priority": "1",
            "Query Intent": "Best Options",
            "Content Asset": "Comparison page",
        }
    ]


def test_create_executive_docx_report_includes_geo_content_roadmap_when_provided():
    geo_content_roadmap = """
| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |
|---|---|---|---|---|---|---|---|
| 1 | Best Options | Comparison page | Category authority | Competitor review strength | Third-party reviews | Improve query intent visibility and prompts visible | 30 Days |
"""
    report_bytes = create_test_report(
        brand_intelligence={
            "recommendation_drivers": "Test recommendation drivers",
            "target_brand_understanding": "Test target brand understanding",
            "positioning_gap_analysis": "Test positioning gap analysis",
        },
        geo_content_roadmap=geo_content_roadmap,
    )

    assert_valid_docx_bytes(report_bytes)

    document_xml = read_document_xml(report_bytes)
    document_text = read_document_text(report_bytes)

    expected_terms = [
        "GEO Content Roadmap",
        "Strategic execution plan",
        "Query Intent",
        "Content Asset",
        "Evidence Needed",
        "Expected Metric Impact",
        "Suggested Timing",
        "Best Options",
        "Comparison page",
        "30 Days",
    ]

    for term in expected_terms:
        assert term in document_xml

    assert "| Priority |" not in document_text

    assert (
        document_text.find("GEO Content Roadmap")
        < document_text.find("30 / 60 / 90 Day Roadmap")
        < document_text.find("Methodology Notes")
        < document_text.find("Appendix: Brand Intelligence & Positioning Audit")
    )


def test_create_executive_docx_report_sanitizes_narrative_text_before_rendering():
    report_bytes = create_test_report(
        category="skincare products",
        brand_intelligence={
            "recommendation_drivers": (
                "AI-Discovered Brands Not Included in Scoring\n"
                "- Market Research\n"
                "- **Influencer Engagement**: Collaborate with local influencers to amplify brand credibility.\n"
                "Strong clinical backing."
            ),
            "target_brand_understanding": "clinical evidence",
            "positioning_gap_analysis": "Top Competitor-Owned Associations (Source: AI-discovered market signal)s)",
        },
        geo_content_roadmap=(
            "| Priority | Query Intent | Content Asset | Target Association | Competitor / Market Signal | Evidence Needed | Expected Metric Impact | Suggested Timing |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| 1 | Trust | Pollution Defense: How Dermaviduals Protects Your Skin | The Science Behind Dermaviduals for Skin Health | | Comparison table data showcasing ingredient efficacy | Intended benchmark influence: target-brand association | 30 Days |"
        ),
    )

    document_text = read_document_text(report_bytes)
    document_text_lower = document_text.lower()

    blocked_terms = [
        "market research",
        "influencer engagement",
        "clinical backing",
        "clinical evidence",
        "medical-grade efficacy",
        "ingredient efficacy",
        "protects your skin",
        "the science behind dermaviduals for skin health",
        "(source: ai-discovered market signal)s)",
    ]

    for term in blocked_terms:
        assert term not in document_text_lower

    assert "No additional non-tracked brands were identified." in document_text
    assert "Dermaviduals Ingredient Guide for Pollution-Exposed Skin" in document_text
    assert "Professional Trust Signals" in document_text
