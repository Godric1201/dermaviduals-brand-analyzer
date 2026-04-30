from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from report_generator import create_executive_docx_report


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


def test_create_executive_docx_report_returns_docx_bytes():
    report_bytes = create_test_report()

    assert_valid_docx_bytes(report_bytes)


def test_create_executive_docx_report_supports_quick_test_mode_metadata():
    report_bytes = create_test_report(
        run_mode="Quick Test Mode",
        prompt_limit=1,
    )

    assert_valid_docx_bytes(report_bytes)

    with ZipFile(BytesIO(report_bytes)) as docx:
        document_xml = docx.read("word/document.xml").decode("utf-8")

    assert "TEST VERSION ONLY" in document_xml
    assert "Not Client Deliverable" in document_xml
