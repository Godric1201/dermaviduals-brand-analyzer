import pandas as pd
import streamlit as st

from geo_audit.benchmark_comparison import (
    compare_query_intent_visibility,
    compare_target_brand_metrics,
    load_snapshot_json,
)


def render_benchmark_progress(current_snapshot):
    st.subheader("Benchmark Progress")
    st.caption(
        "Upload a previous Benchmark Snapshot JSON to compare target-brand visibility progress."
    )

    previous_snapshot_file = st.file_uploader(
        "Upload Previous Benchmark Snapshot JSON",
        type=["json"],
        key="previous_benchmark_snapshot_upload",
    )

    if previous_snapshot_file is not None:
        try:
            previous_snapshot = load_snapshot_json(previous_snapshot_file)
            comparison = compare_target_brand_metrics(
                previous_snapshot,
                current_snapshot,
            )

            previous_metadata = previous_snapshot.get("metadata", {}) or {}
            current_metadata = current_snapshot.get("metadata", {}) or {}
            context_rows = [
                {
                    "Context": "Report Date",
                    "Previous": previous_metadata.get("report_date", "Unknown"),
                    "Current": current_metadata.get("report_date", "Unknown"),
                },
                {
                    "Context": "Run Mode",
                    "Previous": previous_metadata.get("run_mode", "Unknown"),
                    "Current": current_metadata.get("run_mode", "Unknown"),
                },
                {
                    "Context": "Prompt Count",
                    "Previous": previous_metadata.get("prompt_count", 0),
                    "Current": current_metadata.get("prompt_count", 0),
                },
            ]

            for warning in comparison["warnings"]:
                st.warning(warning)

            st.write("**Snapshot Context**")
            st.dataframe(pd.DataFrame(context_rows), use_container_width=True)

            st.write("**Target Brand Progress**")
            st.dataframe(
                pd.DataFrame(comparison["metrics"]),
                use_container_width=True,
            )

            query_intent_progress = compare_query_intent_visibility(
                previous_snapshot,
                current_snapshot,
            )
            st.write("**Query Intent Progress**")
            if query_intent_progress:
                st.dataframe(
                    pd.DataFrame(query_intent_progress),
                    use_container_width=True,
                )
            else:
                st.info(
                    "No query intent-level comparison data available in the uploaded snapshot."
                )
        except ValueError as exc:
            st.error(str(exc))
