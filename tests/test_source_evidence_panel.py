import json

from geo_audit.ui.source_evidence_panel import (
    build_source_evidence_preview_metadata,
    decode_source_evidence_upload,
)


def make_payload():
    return {
        "target_brand": "Example Infrastructure Co.",
        "retrieved_brands": ["Reference Brand A", "Reference Brand B"],
        "category": "Data center infrastructure consulting",
        "market": "Germany",
        "audience": "Enterprise buyers",
        "evidence_items": [
            {
                "brand": "Example Infrastructure Co.",
                "evidence_type": "Entity Evidence",
                "source_url": "https://example-infrastructure.test/about",
                "source_title": "About Example Infrastructure Co.",
                "source_domain": "example-infrastructure.test",
                "source_type": "Owned Source",
                "excerpt_or_summary": "Identifies the target brand.",
                "observed_claim": "The target has basic entity evidence.",
                "supported_retrieval_driver": "Candidate-set inclusion",
                "confidence": "Medium",
                "validation_status": "Observed",
            }
        ],
    }


def test_decode_source_evidence_upload_returns_valid_payload():
    uploaded_bytes = json.dumps(make_payload()).encode("utf-8")

    result = decode_source_evidence_upload(uploaded_bytes)

    assert result.ok
    assert result.payload.target_brand == "Example Infrastructure Co."
    assert result.payload.retrieved_brands == [
        "Reference Brand A",
        "Reference Brand B",
    ]


def test_decode_source_evidence_upload_reports_invalid_utf8():
    result = decode_source_evidence_upload(b"\xff\xfe\x00")

    assert not result.ok
    assert result.payload is None
    assert result.errors == ["json: uploaded file must be UTF-8 encoded"]


def test_decode_source_evidence_upload_reports_json_error():
    result = decode_source_evidence_upload(b"{bad json")

    assert not result.ok
    assert result.payload is None
    assert result.errors[0].startswith("json:")


def test_decode_source_evidence_upload_reports_payload_validation_error():
    payload = make_payload()
    payload["target_brand"] = ""

    result = decode_source_evidence_upload(json.dumps(payload).encode("utf-8"))

    assert not result.ok
    assert "target_brand: required" in result.errors


def test_build_source_evidence_preview_metadata_formats_payload_summary():
    metadata = build_source_evidence_preview_metadata(make_payload())

    assert metadata == {
        "Target brand": "Example Infrastructure Co.",
        "Retrieved brands": "Reference Brand A, Reference Brand B",
        "Evidence items": "1",
    }


def test_build_source_evidence_preview_metadata_handles_missing_values():
    metadata = build_source_evidence_preview_metadata({})

    assert metadata == {
        "Target brand": "Unknown target",
        "Retrieved brands": "None",
        "Evidence items": "0",
    }