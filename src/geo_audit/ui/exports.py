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
