"""Streamlit panel for optional source evidence upload and preview."""

from __future__ import annotations

from typing import Any

import streamlit as st

from geo_audit.source_evidence_markdown import render_source_evidence_summary_section
from geo_audit.source_evidence_payload import (
    SourceEvidencePayloadResult,
    format_source_evidence_payload_errors,
    load_source_evidence_payload_from_text,
)


SOURCE_EVIDENCE_SESSION_KEY = "source_evidence_payload"
SOURCE_EVIDENCE_UPLOAD_KEY = "source_evidence_json_upload"


def decode_source_evidence_upload(uploaded_bytes: bytes) -> SourceEvidencePayloadResult:
    """Decode uploaded JSON bytes and validate the source evidence payload."""

    try:
        text = uploaded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return SourceEvidencePayloadResult(
            payload=None,
            errors=["json: uploaded file must be UTF-8 encoded"],
        )

    return load_source_evidence_payload_from_text(text)


def build_source_evidence_preview_metadata(payload: dict[str, Any]) -> dict[str, str]:
    """Build display metadata for a validated source evidence payload."""

    target_brand = str(payload.get("target_brand", "")).strip() or "Unknown target"
    retrieved_brands = [
        str(brand).strip()
        for brand in payload.get("retrieved_brands", [])
        if str(brand).strip()
    ]
    evidence_items = payload.get("evidence_items", [])

    return {
        "Target brand": target_brand,
        "Retrieved brands": ", ".join(retrieved_brands) if retrieved_brands else "None",
        "Evidence items": str(len(evidence_items)),
    }


def _store_source_evidence_payload(payload: dict[str, Any]) -> None:
    st.session_state[SOURCE_EVIDENCE_SESSION_KEY] = payload


def _clear_source_evidence_payload() -> None:
    st.session_state.pop(SOURCE_EVIDENCE_SESSION_KEY, None)


def _render_payload_metadata(payload: dict[str, Any]) -> None:
    metadata = build_source_evidence_preview_metadata(payload)
    for label, value in metadata.items():
        st.write(f"**{label}:** {value}")


def render_source_evidence_panel() -> None:
    """Render optional source evidence JSON upload and summary preview."""

    st.subheader("Source Evidence Preview")
    st.caption(
        "Optional validation context for source-grounded evidence gaps. "
        "This does not affect the benchmark run and does not prove retrieval causality."
    )

    uploaded_file = st.file_uploader(
        "Upload source evidence JSON",
        type=["json"],
        key=SOURCE_EVIDENCE_UPLOAD_KEY,
        help=(
            "Upload a JSON payload that follows the source evidence schema. "
            "The file is validated locally and is not sent to OpenAI."
        ),
    )

    if uploaded_file is not None:
        result = decode_source_evidence_upload(uploaded_file.getvalue())

        if not result.ok:
            _clear_source_evidence_payload()
            st.error(format_source_evidence_payload_errors(result.errors))
            return

        payload = result.payload.to_dict()
        _store_source_evidence_payload(payload)
        st.success("Source evidence payload loaded.")
        _render_payload_metadata(payload)

        with st.expander("Source-Grounded Evidence Summary Preview", expanded=True):
            st.markdown(render_source_evidence_summary_section(payload))

        return

    stored_payload = st.session_state.get(SOURCE_EVIDENCE_SESSION_KEY)
    if stored_payload:
        st.info("Using previously loaded source evidence payload.")
        _render_payload_metadata(stored_payload)

        with st.expander("Source-Grounded Evidence Summary Preview", expanded=False):
            st.markdown(render_source_evidence_summary_section(stored_payload))

        if st.button("Clear source evidence payload"):
            _clear_source_evidence_payload()
            st.rerun()

        return

    st.info(
        "No source evidence JSON uploaded. You can export the benchmark report without source evidence, "
        "or upload a source evidence payload to preview source-supported gaps."
    )