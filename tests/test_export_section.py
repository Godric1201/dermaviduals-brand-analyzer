import streamlit as st

from geo_audit.ui.export_section import (
    build_source_evidence_export_status_message,
    get_source_evidence_payload_for_markdown_export,
)
from geo_audit.ui.source_evidence_panel import SOURCE_EVIDENCE_SESSION_KEY


def test_get_source_evidence_payload_for_markdown_export_returns_stored_payload():
    payload = {
        "target_brand": "Example Infrastructure Co.",
        "retrieved_brands": ["Reference Brand A"],
        "evidence_items": [],
    }
    st.session_state[SOURCE_EVIDENCE_SESSION_KEY] = payload

    assert get_source_evidence_payload_for_markdown_export() == payload

    st.session_state.pop(SOURCE_EVIDENCE_SESSION_KEY, None)


def test_get_source_evidence_payload_for_markdown_export_returns_none_without_payload():
    st.session_state.pop(SOURCE_EVIDENCE_SESSION_KEY, None)

    assert get_source_evidence_payload_for_markdown_export() is None

def test_build_source_evidence_export_status_message_when_payload_loaded():
    message = build_source_evidence_export_status_message({"target_brand": "Example"})

    assert "Markdown export will include" in message
    assert "DOCX export does not include source evidence yet" in message


def test_build_source_evidence_export_status_message_without_payload():
    message = build_source_evidence_export_status_message(None)

    assert message == (
        "No source evidence loaded. Markdown and DOCX exports will use benchmark "
        "signals only."
    )