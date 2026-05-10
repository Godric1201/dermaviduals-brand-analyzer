from dataclasses import dataclass
from datetime import date

import streamlit as st

from geo_audit.benchmark_snapshot import (
    build_benchmark_snapshot,
    serialize_benchmark_snapshot,
)
from geo_audit.ui_formatters import build_export_filename


@dataclass(frozen=True)
class BenchmarkSnapshotExport:
    snapshot: dict
    json_bytes: bytes
    file_name: str


@dataclass(frozen=True)
class ReportDownloadPayload:
    data: bytes
    file_name: str
    mime: str
    key: str


def build_report_download_payloads(
    *,
    summary_df,
    detailed_df,
    raw_answer_df,
    executive_report,
    executive_docx,
    display_brand,
    display_market,
    run_mode,
):
    from geo_audit.utils import convert_df_to_csv

    return {
        "summary": ReportDownloadPayload(
            data=convert_df_to_csv(summary_df),
            file_name=build_export_filename(
                display_brand,
                display_market,
                "summary",
                "csv",
                run_mode,
            ),
            mime="text/csv",
            key="summary_download",
        ),
        "detailed": ReportDownloadPayload(
            data=convert_df_to_csv(detailed_df),
            file_name=build_export_filename(
                display_brand,
                display_market,
                "detailed_results",
                "csv",
                run_mode,
            ),
            mime="text/csv",
            key="detailed_download",
        ),
        "raw": ReportDownloadPayload(
            data=convert_df_to_csv(raw_answer_df),
            file_name=build_export_filename(
                display_brand,
                display_market,
                "raw_answers",
                "csv",
                run_mode,
            ),
            mime="text/csv",
            key="raw_download",
        ),
        "markdown": ReportDownloadPayload(
            data=executive_report.encode("utf-8-sig"),
            file_name=build_export_filename(
                display_brand,
                display_market,
                "executive_report",
                "md",
                run_mode,
            ),
            mime="text/markdown",
            key="executive_report_download",
        ),
        "docx": ReportDownloadPayload(
            data=executive_docx,
            file_name=build_export_filename(
                display_brand,
                display_market,
                "ai_visibility_report",
                "docx",
                run_mode,
            ),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="client_report_docx_download",
        ),
    }


def render_report_download_exports(
    *,
    t,
    summary_df,
    detailed_df,
    raw_answer_df,
    executive_report,
    executive_docx,
    display_brand,
    display_market,
    run_mode,
):
    payloads = build_report_download_payloads(
        summary_df=summary_df,
        detailed_df=detailed_df,
        raw_answer_df=raw_answer_df,
        executive_report=executive_report,
        executive_docx=executive_docx,
        display_brand=display_brand,
        display_market=display_market,
        run_mode=run_mode,
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        payload = payloads["summary"]
        st.download_button(
            label=t["summary_csv"],
            data=payload.data,
            file_name=payload.file_name,
            mime=payload.mime,
            key=payload.key,
            on_click="ignore",
        )

    with col2:
        payload = payloads["detailed"]
        st.download_button(
            label=t["detailed_csv"],
            data=payload.data,
            file_name=payload.file_name,
            mime=payload.mime,
            key=payload.key,
            on_click="ignore",
        )

    with col3:
        payload = payloads["raw"]
        st.download_button(
            label=t["raw_csv"],
            data=payload.data,
            file_name=payload.file_name,
            mime=payload.mime,
            key=payload.key,
            on_click="ignore",
        )

    with col4:
        payload = payloads["markdown"]
        st.download_button(
            label="Download Executive Report MD",
            data=payload.data,
            file_name=payload.file_name,
            mime=payload.mime,
            key=payload.key,
            on_click="ignore",
        )

    with col5:
        payload = payloads["docx"]
        st.download_button(
            label="Download Client Report DOCX",
            data=payload.data,
            file_name=payload.file_name,
            mime=payload.mime,
            key=payload.key,
            on_click="ignore",
        )

        st.divider()


def build_benchmark_snapshot_export(
    *,
    display_brand,
    display_market,
    display_category,
    display_audience,
    run_mode,
    prompt_limit,
    prompt_count,
    competitors,
    prompt_categories,
    summary_df,
    detailed_df,
    snapshot_brand_intelligence,
    include_raw_answers,
    raw_answer_df,
    api_usage_summary,
    report_date=None,
):
    snapshot = build_benchmark_snapshot(
        brand=display_brand,
        market=display_market,
        category=display_category,
        audience=display_audience,
        report_date=report_date or date.today().isoformat(),
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        prompt_count=prompt_count,
        competitors=competitors,
        query_intent_categories=prompt_categories,
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence=snapshot_brand_intelligence,
        include_raw_answers=include_raw_answers,
        raw_answer_df=raw_answer_df,
        api_usage_summary=api_usage_summary,
    )
    benchmark_snapshot_json = serialize_benchmark_snapshot(snapshot)

    return BenchmarkSnapshotExport(
        snapshot=snapshot,
        json_bytes=benchmark_snapshot_json.encode("utf-8"),
        file_name=build_export_filename(
            display_brand,
            display_market,
            "benchmark_snapshot",
            "json",
            run_mode,
        ),
    )


def render_benchmark_snapshot_export(
    *,
    display_brand,
    display_market,
    display_category,
    display_audience,
    run_mode,
    prompt_limit,
    prompt_count,
    competitors,
    prompt_categories,
    summary_df,
    detailed_df,
    snapshot_brand_intelligence,
    raw_answer_df,
    api_usage_summary,
    raw_answer_evidence_help,
):
    st.subheader("Benchmark Snapshot")
    st.caption(
        "Export a benchmark snapshot JSON for progress tracking, audit review, "
        "or comparison with future benchmark runs."
    )

    include_raw_answers_in_snapshot = st.checkbox(
        "Include raw AI answers in Benchmark Snapshot JSON",
        value=False,
        help=raw_answer_evidence_help,
        key="include_raw_answers_in_benchmark_snapshot",
    )
    st.caption(raw_answer_evidence_help)

    export = build_benchmark_snapshot_export(
        display_brand=display_brand,
        display_market=display_market,
        display_category=display_category,
        display_audience=display_audience,
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        prompt_count=prompt_count,
        competitors=competitors,
        prompt_categories=prompt_categories,
        summary_df=summary_df,
        detailed_df=detailed_df,
        snapshot_brand_intelligence=snapshot_brand_intelligence,
        include_raw_answers=include_raw_answers_in_snapshot,
        raw_answer_df=raw_answer_df,
        api_usage_summary=api_usage_summary,
    )

    st.download_button(
        label="Download Benchmark Snapshot JSON",
        data=export.json_bytes,
        file_name=export.file_name,
        mime="application/json",
        key="benchmark_snapshot_download",
        on_click="ignore",
    )
