import re
from io import BytesIO

import pandas as pd
from docx import Document

from geo_audit.markdown_report import build_executive_markdown_report
from geo_audit.report_generator import create_executive_docx_report


FORBIDDEN_OVERCLAIM_PATTERNS = [
    r"\bguarantees\b",
    r"\bwill\s+increase\s+sales\b",
    r"\bwill\s+drive\s+revenue\b",
    r"\bconsumers\s+prefer\b",
    r"\bmarket\s+leader\b",
    r"\bdominates\s+the\s+market\b",
    r"\bAI\s+knows\b",
    r"\bAI\s+trusts\b",
]


def assert_has_phrase_family(text, phrases):
    normalized = str(text).lower()

    assert any(phrase.lower() in normalized for phrase in phrases)


def assert_forbidden_overclaims_absent(text):
    for pattern in FORBIDDEN_OVERCLAIM_PATTERNS:
        assert not re.search(pattern, str(text), flags=re.IGNORECASE)


def sample_summary_df():
    return pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 2,
            "average_visibility_score": 3.5,
            "prompts_visible": 2,
            "share_of_voice_percent": 20.0,
        },
        {
            "brand": "Coffee Fellows",
            "total_mentions": 8,
            "average_visibility_score": 7.2,
            "prompts_visible": 4,
            "share_of_voice_percent": 80.0,
        },
    ])


def sample_top_brands_df():
    return pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Coffee Fellows",
            "visibility_score": 7.0,
        },
    ])


def markdown_report(**overrides):
    summary_df = sample_summary_df()
    inputs = {
        "brand": "Espresso House",
        "display_brand": "Espresso House",
        "category": "cafes",
        "display_category": "Cafes",
        "market": "Berlin",
        "display_market": "Berlin",
        "audience": "remote workers",
        "display_audience": "Remote Workers",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "deliverable_status": "Client-deliverable full report",
        "summary_df": summary_df,
        "summary_display_df": summary_df.copy(),
        "detailed_pivot_df": pd.DataFrame([
            {
                "prompt_category": "Best Options",
                "Espresso House": 2.0,
                "Coffee Fellows": 7.0,
            },
        ]),
        "top_brands_df": sample_top_brands_df(),
        "recommendations": "Prioritize AI-citable category evidence.",
        "plan": "Use future benchmark cycles to validate progress.",
        "gap_analysis": "The tested answers suggest limited prompt-level visibility.",
        "brand_win_explanation": None,
        "replacement_strategy": None,
        "brand_intelligence": {
            "recommendation_drivers": "Diagnostic inference from benchmark answers.",
            "target_brand_understanding": "AI-inferred target brand understanding.",
            "positioning_gap_analysis": "Positioning gaps require validation.",
        },
        "brand_intelligence_done": True,
        "geo_content_roadmap": None,
        "geo_content_roadmap_done": False,
        "prompt_categories": ["Best Options", "Local Recommendations"],
        "tracked_competitors": ["Coffee Fellows"],
    }
    inputs.update(overrides)

    return build_executive_markdown_report(**inputs)


def docx_report(**overrides):
    inputs = {
        "brand": "Espresso House",
        "market": "Berlin",
        "category": "cafes",
        "audience": "remote workers",
        "summary_df": sample_summary_df(),
        "top_brands_df": sample_top_brands_df(),
        "recommendations": "Prioritize AI-citable category evidence.",
        "strategy_report": "Use future benchmark cycles to validate progress.",
        "gap_analysis": "The tested answers suggest limited prompt-level visibility.",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "brand_intelligence": {
            "recommendation_drivers": "Diagnostic inference from benchmark answers.",
            "target_brand_understanding": "AI-inferred target brand understanding.",
            "positioning_gap_analysis": "Positioning gaps require validation.",
        },
        "prompt_categories": ["Best Options", "Local Recommendations"],
        "geo_content_roadmap": None,
    }
    inputs.update(overrides)

    return create_executive_docx_report(**inputs)


def extract_docx_text(docx_bytes):
    document = Document(BytesIO(docx_bytes))
    text_parts = []

    text_parts.extend(paragraph.text for paragraph in document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                text_parts.extend(paragraph.text for paragraph in cell.paragraphs)

    return "\n".join(part for part in text_parts if part)


def test_markdown_quick_test_report_is_not_client_deliverable():
    report = markdown_report(
        run_mode="Quick Test Mode",
        prompt_limit=1,
        deliverable_status="Development-only limited-prompt output. Not client-deliverable.",
    )

    assert_has_phrase_family(report, ["test version only", "quick test mode"])
    assert_has_phrase_family(report, ["not client-deliverable", "not client deliverable"])


def test_markdown_report_preserves_methodology_limitations():
    report = markdown_report()

    assert_has_phrase_family(report, ["ai visibility benchmark"])
    assert_has_phrase_family(report, ["not market share"])
    assert_has_phrase_family(report, ["sales performance report", "business performance outcomes"])
    assert_has_phrase_family(report, ["clinical evaluation"])


def test_markdown_report_uses_benchmark_safe_framing():
    report = markdown_report()

    assert_has_phrase_family(report, ["tested prompt set", "benchmark"])


def test_markdown_report_avoids_forbidden_overclaim_phrases():
    assert_forbidden_overclaims_absent(markdown_report())


def test_markdown_brand_intelligence_keeps_diagnostic_separation():
    report = markdown_report()

    assert_has_phrase_family(
        report,
        [
            "diagnostic",
            "not part of visibility scoring",
            "not included in scoring",
        ],
    )


def test_docx_quick_test_report_is_not_client_deliverable():
    report_text = extract_docx_text(
        docx_report(run_mode="Quick Test Mode", prompt_limit=1)
    )

    assert_has_phrase_family(report_text, ["test version only", "quick test mode"])
    assert_has_phrase_family(report_text, ["not client-deliverable", "not client deliverable"])


def test_docx_report_preserves_methodology_limitations():
    report_text = extract_docx_text(docx_report())

    assert_has_phrase_family(report_text, ["ai visibility benchmark"])
    assert_has_phrase_family(report_text, ["not market share"])
    assert_has_phrase_family(report_text, ["sales performance report", "business performance outcomes"])
    assert_has_phrase_family(report_text, ["clinical evaluation"])


def test_docx_report_avoids_forbidden_overclaim_phrases():
    assert_forbidden_overclaims_absent(extract_docx_text(docx_report()))


def test_docx_brand_intelligence_keeps_diagnostic_separation():
    report_text = extract_docx_text(docx_report())

    assert_has_phrase_family(
        report_text,
        [
            "diagnostic",
            "not part of visibility scoring",
            "not included in scoring",
        ],
    )
