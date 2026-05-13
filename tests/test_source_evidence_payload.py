import json
from pathlib import Path

from geo_audit.source_evidence_payload import (
    format_source_evidence_payload_errors,
    load_source_evidence_payload,
    load_source_evidence_payload_from_text,
    validate_source_evidence_payload,
)


def make_payload():
    return {
        "target_brand": "Example Infrastructure Co.",
        "retrieved_brands": ["Reference Brand A", " Reference Brand B "],
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


def test_validate_source_evidence_payload_returns_normalized_payload():
    result = validate_source_evidence_payload(make_payload())

    assert result.ok
    assert result.errors == []
    assert result.payload is not None
    assert result.payload.target_brand == "Example Infrastructure Co."
    assert result.payload.retrieved_brands == [
        "Reference Brand A",
        "Reference Brand B",
    ]
    assert result.payload.category == "Data center infrastructure consulting"
    assert result.payload.market == "Germany"
    assert result.payload.audience == "Enterprise buyers"
    assert result.payload.evidence_items[0].brand == "Example Infrastructure Co."


def test_source_evidence_payload_to_dict_returns_renderer_shape():
    result = validate_source_evidence_payload(make_payload())

    payload_dict = result.payload.to_dict()

    assert payload_dict["target_brand"] == "Example Infrastructure Co."
    assert payload_dict["retrieved_brands"] == [
        "Reference Brand A",
        "Reference Brand B",
    ]
    assert payload_dict["evidence_items"][0].evidence_type == "Entity Evidence"


def test_validate_source_evidence_payload_rejects_non_object():
    result = validate_source_evidence_payload(["not", "an", "object"])

    assert not result.ok
    assert result.payload is None
    assert result.errors == ["payload: expected JSON object"]


def test_validate_source_evidence_payload_reports_top_level_errors():
    result = validate_source_evidence_payload(
        {
            "target_brand": "",
            "retrieved_brands": [],
            "evidence_items": [],
        }
    )

    assert not result.ok
    assert result.payload is None
    assert "target_brand: required" in result.errors
    assert "retrieved_brands: must contain at least one brand" in result.errors


def test_validate_source_evidence_payload_reports_evidence_items_type_error():
    result = validate_source_evidence_payload(
        {
            "target_brand": "Example Infrastructure Co.",
            "retrieved_brands": ["Reference Brand A"],
            "evidence_items": "not-a-list",
        }
    )

    assert not result.ok
    assert "evidence_items: expected list" in result.errors


def test_validate_source_evidence_payload_reports_item_validation_errors():
    payload = make_payload()
    payload["evidence_items"][0]["source_url"] = "not-a-url"

    result = validate_source_evidence_payload(payload)

    assert not result.ok
    assert "evidence_items[0].source_url: source_url must be an http(s) URL" in result.errors


def test_load_source_evidence_payload_from_text_parses_valid_json():
    result = load_source_evidence_payload_from_text(json.dumps(make_payload()))

    assert result.ok
    assert result.payload.target_brand == "Example Infrastructure Co."


def test_load_source_evidence_payload_from_text_reports_json_error():
    result = load_source_evidence_payload_from_text("{bad json")

    assert not result.ok
    assert result.payload is None
    assert result.errors[0].startswith("json:")


def test_load_source_evidence_payload_reads_file(tmp_path: Path):
    input_path = tmp_path / "source-evidence.json"
    input_path.write_text(json.dumps(make_payload()), encoding="utf-8")

    result = load_source_evidence_payload(input_path)

    assert result.ok
    assert result.payload.target_brand == "Example Infrastructure Co."


def test_load_source_evidence_payload_reports_file_error(tmp_path: Path):
    missing_path = tmp_path / "missing.json"

    result = load_source_evidence_payload(missing_path)

    assert not result.ok
    assert result.payload is None
    assert result.errors[0].startswith("file:")


def test_format_source_evidence_payload_errors_returns_bulleted_message():
    message = format_source_evidence_payload_errors(
        [
            "target_brand: required",
            "evidence_items: expected list",
        ]
    )

    assert message == (
        "Source evidence payload has validation errors:\n"
        "- target_brand: required\n"
        "- evidence_items: expected list"
    )


def test_format_source_evidence_payload_errors_returns_empty_string_without_errors():
    assert format_source_evidence_payload_errors([]) == ""