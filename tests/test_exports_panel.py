import json

import pandas as pd

from geo_audit.ui.exports import (
    build_benchmark_snapshot_export,
    build_report_download_payloads,
)


def build_export_fixture(**kwargs):
    summary_df = pd.DataFrame([
        {
            "brand": "Espresso House",
            "total_mentions": 2,
            "average_visibility_score": 1.5,
        }
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Espresso House",
            "visibility_score": 1,
        }
    ])
    raw_answer_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        }
    ])
    defaults = {
        "display_brand": "Espresso House",
        "display_market": "Berlin",
        "display_category": "cafes",
        "display_audience": "remote workers",
        "run_mode": "Full Report Mode",
        "prompt_limit": None,
        "prompt_count": 20,
        "competitors": ["Coffee Fellows", "Einstein Kaffee"],
        "prompt_categories": ["Best Options", "Local Recommendations"],
        "summary_df": summary_df,
        "detailed_df": detailed_df,
        "snapshot_brand_intelligence": None,
        "include_raw_answers": False,
        "raw_answer_df": raw_answer_df,
        "api_usage_summary": None,
        "report_date": "2026-05-02",
    }
    defaults.update(kwargs)

    return build_benchmark_snapshot_export(**defaults)


def build_report_payload_fixture(**kwargs):
    summary_df = pd.DataFrame([
        {"brand": "Espresso House", "average_visibility_score": 1.5}
    ])
    detailed_df = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Espresso House",
            "visibility_score": 1,
        }
    ])
    raw_answer_df = pd.DataFrame([
        {
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        }
    ])
    defaults = {
        "summary_df": summary_df,
        "detailed_df": detailed_df,
        "raw_answer_df": raw_answer_df,
        "executive_report": "# Executive Report\n\nMeasured visibility.",
        "executive_docx": b"docx-bytes",
        "display_brand": "Espresso House",
        "display_market": "Berlin",
        "run_mode": "Full Report Mode",
    }
    defaults.update(kwargs)

    return build_report_download_payloads(**defaults)


def test_benchmark_snapshot_export_excludes_raw_answers_by_default():
    export = build_export_fixture()

    assert "raw_answer_records" not in export.snapshot
    assert export.snapshot["metadata"]["run_metadata"]["raw_answers_included"] is False


def test_benchmark_snapshot_export_includes_raw_answers_when_requested():
    export = build_export_fixture(include_raw_answers=True)

    assert export.snapshot["raw_answer_records"] == [
        {
            "prompt_category": "Best Options",
            "prompt": "Which cafes are best for remote work?",
            "answer": "AI-generated answer mentioning Espresso House.",
        }
    ]
    assert export.snapshot["metadata"]["run_metadata"]["raw_answers_included"] is True


def test_benchmark_snapshot_export_includes_api_usage_metadata():
    export = build_export_fixture(
        api_usage_summary={
            "model_name": "gpt-4o-mini",
            "input_tokens": 1200,
            "output_tokens": 450,
            "total_tokens": 1650,
            "call_count": 3,
            "calls_with_usage": 2,
            "calls_without_usage": 1,
            "usage_available": True,
            "pricing_available": True,
            "estimated_actual_cost_usd": 0.00045,
            "pricing_label": "gpt-4o-mini text token pricing",
        }
    )

    api_usage = export.snapshot["metadata"]["run_metadata"]["api_usage"]

    assert api_usage["model_name"] == "gpt-4o-mini"
    assert api_usage["total_tokens"] == 1650
    assert api_usage["estimated_actual_cost_usd"] == 0.00045


def test_benchmark_snapshot_export_json_bytes_decode_as_utf8_json():
    export = build_export_fixture()
    parsed = json.loads(export.json_bytes.decode("utf-8"))

    assert parsed["metadata"]["brand"] == "Espresso House"
    assert parsed["metadata"]["run_metadata"]["generated_at"] == "2026-05-02"


def test_benchmark_snapshot_export_filename_uses_snapshot_json_export_name():
    export = build_export_fixture()

    assert "benchmark_snapshot" in export.file_name
    assert export.file_name.endswith(".json")


def test_benchmark_snapshot_export_excludes_raw_api_payload_fields():
    export = build_export_fixture(
        api_usage_summary={
            "model_name": "gpt-4o-mini",
            "input_tokens": 1200,
            "output_tokens": 450,
            "total_tokens": 1650,
            "call_count": 3,
            "calls_with_usage": 2,
            "calls_without_usage": 1,
            "usage_available": True,
            "pricing_available": True,
            "estimated_actual_cost_usd": 0.00045,
            "pricing_label": "gpt-4o-mini text token pricing",
            "prompt": "SECRET PROMPT",
            "answer": "SECRET ANSWER",
            "raw_response": {"id": "raw-response-id"},
        }
    )
    serialized = export.json_bytes.decode("utf-8")

    assert "SECRET PROMPT" not in serialized
    assert "SECRET ANSWER" not in serialized
    assert "raw-response-id" not in serialized


def test_report_download_payloads_use_utf8_sig_for_markdown():
    payloads = build_report_payload_fixture()

    assert payloads["markdown"].data.startswith(b"\xef\xbb\xbf")
    assert b"# Executive Report" in payloads["markdown"].data
    assert payloads["markdown"].mime == "text/markdown"


def test_report_download_payloads_pass_docx_bytes_through_unchanged():
    payloads = build_report_payload_fixture(executive_docx=b"original-docx")

    assert payloads["docx"].data == b"original-docx"
    assert payloads["docx"].mime == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_report_download_payload_filenames_use_expected_export_slugs():
    payloads = build_report_payload_fixture()

    assert "summary" in payloads["summary"].file_name
    assert payloads["summary"].file_name.endswith(".csv")
    assert "detailed_results" in payloads["detailed"].file_name
    assert payloads["detailed"].file_name.endswith(".csv")
    assert "raw_answers" in payloads["raw"].file_name
    assert payloads["raw"].file_name.endswith(".csv")
    assert "executive_report" in payloads["markdown"].file_name
    assert payloads["markdown"].file_name.endswith(".md")
    assert "ai_visibility_report" in payloads["docx"].file_name
    assert payloads["docx"].file_name.endswith(".docx")


def test_report_download_payloads_preserve_download_keys_and_mime_types():
    payloads = build_report_payload_fixture()

    assert payloads["summary"].key == "summary_download"
    assert payloads["summary"].mime == "text/csv"
    assert payloads["detailed"].key == "detailed_download"
    assert payloads["detailed"].mime == "text/csv"
    assert payloads["raw"].key == "raw_download"
    assert payloads["raw"].mime == "text/csv"
    assert payloads["markdown"].key == "executive_report_download"
    assert payloads["docx"].key == "client_report_docx_download"


def test_report_download_payload_csv_data_remains_utf8_sig_bytes():
    payloads = build_report_payload_fixture()

    assert isinstance(payloads["summary"].data, bytes)
    assert payloads["summary"].data.startswith(b"\xef\xbb\xbf")
    assert isinstance(payloads["detailed"].data, bytes)
    assert payloads["detailed"].data.startswith(b"\xef\xbb\xbf")
    assert isinstance(payloads["raw"].data, bytes)
    assert payloads["raw"].data.startswith(b"\xef\xbb\xbf")
