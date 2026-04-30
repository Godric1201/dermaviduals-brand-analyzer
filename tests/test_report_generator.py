import pandas as pd

from report_generator import create_executive_docx_report


def test_create_executive_docx_report_returns_docx_bytes():
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

    report_bytes = create_executive_docx_report(
        brand="Dermaviduals",
        category="skincare products",
        market="Hong Kong",
        audience="skincare-conscious consumers in Hong Kong",
        summary_df=summary_df,
        top_brands_df=top_winners_df,
        recommendations="Test recommendations",
        strategy_report="Test strategy report",
        gap_analysis="Test gap analysis",
    )

    assert isinstance(report_bytes, bytes)
    assert len(report_bytes) > 0
    assert report_bytes.startswith(b"PK")
