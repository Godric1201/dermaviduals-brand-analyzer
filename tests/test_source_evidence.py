from geo_audit.source_evidence import (
    CONFIDENCE_HIGH,
    CONFIDENCE_INSUFFICIENT,
    EVIDENCE_COMPARISON,
    EVIDENCE_ENTITY,
    EVIDENCE_MARKET,
    EvidenceItem,
    SOURCE_DIRECTORY,
    SOURCE_OWNED,
    STATUS_CONFLICTING,
    STATUS_NEEDS_REVIEW,
    STATUS_OBSERVED,
    STATUS_REJECTED,
    EVIDENCE_OFFERING_USE_CASE,
    EVIDENCE_PROOF_TRUST,
    group_evidence_by_brand,
    normalize_evidence_item,
    summarize_evidence_coverage,
    validate_evidence_item,
    validate_evidence_items,
    compare_target_vs_retrieved_evidence,
    summarize_evidence_gap_rows,
)


def make_valid_evidence(**overrides):
    item = {
        "brand": "Example Infrastructure Co.",
        "evidence_type": "Market Evidence",
        "source_url": "https://example.com/germany-projects",
        "source_title": "Germany data center projects",
        "source_domain": "example.com",
        "source_type": "Owned Source",
        "excerpt_or_summary": "Shows Germany project activity.",
        "observed_claim": "The brand publishes Germany project examples.",
        "supported_retrieval_driver": "Local market provider",
        "confidence": "High",
        "freshness_date": "2025-01-15",
        "validation_status": "Observed",
        "notes": "Fixture evidence item.",
    }
    item.update(overrides)
    return item


def test_normalize_evidence_item_canonicalizes_labels_and_text():
    item = normalize_evidence_item(
        make_valid_evidence(
            brand="  Example Infrastructure Co.  ",
            evidence_type=" market ",
            source_domain="https://Example.com/path/page",
            source_type="official website",
            confidence="high",
            validation_status="needs_review",
        )
    )

    assert item.brand == "Example Infrastructure Co."
    assert item.evidence_type == EVIDENCE_MARKET
    assert item.source_domain == "example.com"
    assert item.source_type == SOURCE_OWNED
    assert item.confidence == CONFIDENCE_HIGH
    assert item.validation_status == STATUS_NEEDS_REVIEW


def test_normalize_evidence_item_accepts_dataclass_input():
    raw = EvidenceItem(
        brand="Reference Brand A",
        evidence_type="comparison",
        source_url="https://reference.example.com/alternatives",
        source_title="Alternatives guide",
        source_domain="reference.example.com",
        source_type="directory",
        excerpt_or_summary="Lists category alternatives.",
        observed_claim="The brand is listed as an alternative.",
        supported_retrieval_driver="Comparison anchor",
        confidence="medium",
        validation_status="observed",
    )

    item = normalize_evidence_item(raw)

    assert item.brand == "Reference Brand A"
    assert item.evidence_type == EVIDENCE_COMPARISON
    assert item.source_type == SOURCE_DIRECTORY
    assert item.validation_status == STATUS_OBSERVED


def test_validate_evidence_item_accepts_valid_item():
    errors = validate_evidence_item(make_valid_evidence())

    assert errors == []


def test_validate_evidence_item_reports_required_fields():
    errors = validate_evidence_item(
        make_valid_evidence(
            brand="",
            source_url="",
            observed_claim="",
            supported_retrieval_driver="",
        )
    )

    fields = {error.field for error in errors}

    assert "brand" in fields
    assert "source_url" in fields
    assert "observed_claim" in fields
    assert "supported_retrieval_driver" in fields


def test_validate_evidence_item_rejects_invalid_labels_and_url():
    errors = validate_evidence_item(
        make_valid_evidence(
            evidence_type="Magic Evidence",
            source_type="Unknown Source",
            confidence="Certain",
            validation_status="Approved Forever",
            source_url="not-a-url",
        )
    )

    messages = [error.message for error in errors]

    assert any("Unsupported evidence type" in message for message in messages)
    assert any("Unsupported source type" in message for message in messages)
    assert any("Unsupported confidence level" in message for message in messages)
    assert any("Unsupported validation status" in message for message in messages)
    assert any("http(s) URL" in message for message in messages)


def test_validate_evidence_items_preserves_item_index():
    errors = validate_evidence_items([
        make_valid_evidence(),
        make_valid_evidence(brand="", source_url="ftp://example.com/file"),
    ])

    assert {error.index for error in errors} == {1}


def test_missing_confidence_and_status_default_to_safe_labels():
    item = normalize_evidence_item(
        make_valid_evidence(
            confidence="",
            validation_status="",
        )
    )

    assert item.confidence == CONFIDENCE_INSUFFICIENT
    assert item.validation_status == STATUS_NEEDS_REVIEW


def test_group_evidence_by_brand_normalizes_records():
    grouped = group_evidence_by_brand([
        make_valid_evidence(brand="Target Brand", evidence_type="entity"),
        make_valid_evidence(brand="Reference Brand", evidence_type="comparison"),
        make_valid_evidence(brand="Target Brand", evidence_type="market"),
    ])

    assert set(grouped) == {"Reference Brand", "Target Brand"}
    assert len(grouped["Target Brand"]) == 2
    assert grouped["Target Brand"][0].evidence_type == EVIDENCE_ENTITY
    assert grouped["Target Brand"][1].evidence_type == EVIDENCE_MARKET


def test_summarize_evidence_coverage_counts_accepted_and_high_confidence_items():
    summary = summarize_evidence_coverage([
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="entity",
            confidence="High",
            validation_status="Observed",
        ),
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="market",
            confidence="Medium",
            validation_status="Needs Review",
        ),
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="comparison",
            confidence="Low",
            validation_status="Rejected",
        ),
        make_valid_evidence(
            brand="Reference Brand",
            evidence_type="comparison",
            confidence="High",
            validation_status="Observed",
        ),
    ])

    target_summary = next(row for row in summary if row["brand"] == "Target Brand")
    reference_summary = next(row for row in summary if row["brand"] == "Reference Brand")

    assert target_summary["total_items"] == 3
    assert target_summary["accepted_items"] == 2
    assert target_summary["high_confidence_items"] == 1
    assert target_summary["evidence_types"] == [
        EVIDENCE_ENTITY,
        EVIDENCE_MARKET,
    ]
    assert target_summary["evidence_type_count"] == 2

    assert reference_summary["total_items"] == 1
    assert reference_summary["accepted_items"] == 1
    assert reference_summary["high_confidence_items"] == 1
    assert reference_summary["evidence_types"] == [EVIDENCE_COMPARISON]


def test_conflicting_items_are_not_accepted_for_coverage():
    summary = summarize_evidence_coverage([
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="market",
            validation_status=STATUS_CONFLICTING,
        ),
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="comparison",
            validation_status=STATUS_REJECTED,
        ),
    ])

    row = summary[0]

    assert row["total_items"] == 2
    assert row["accepted_items"] == 0
    assert row["evidence_types"] == []
    assert row["evidence_type_count"] == 0

def test_compare_target_vs_retrieved_evidence_finds_missing_evidence_types():
    items = [
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="entity",
            supported_retrieval_driver="Candidate-set inclusion",
        ),
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="market",
            supported_retrieval_driver="Local market provider",
        ),
        make_valid_evidence(
            brand="Reference Brand A",
            evidence_type="comparison",
            supported_retrieval_driver="Comparison anchor",
            confidence="High",
        ),
        make_valid_evidence(
            brand="Reference Brand A",
            evidence_type="proof",
            supported_retrieval_driver="Trust / premium reference",
            confidence="Medium",
        ),
        make_valid_evidence(
            brand="Reference Brand B",
            evidence_type="offering",
            supported_retrieval_driver="Technical infrastructure provider",
            confidence="High",
        ),
    ]

    gaps = compare_target_vs_retrieved_evidence(
        items,
        target_brand="Target Brand",
        retrieved_brands=["Reference Brand A", "Reference Brand B"],
    )

    gap_types = {gap["missing_evidence_type"] for gap in gaps}

    assert gap_types == {
        EVIDENCE_COMPARISON,
        EVIDENCE_PROOF_TRUST,
        EVIDENCE_OFFERING_USE_CASE,
    }

    comparison_gap = next(
        gap for gap in gaps
        if gap["missing_evidence_type"] == EVIDENCE_COMPARISON
    )

    assert comparison_gap["target_brand"] == "Target Brand"
    assert comparison_gap["retrieved_brand"] == "Reference Brand A"
    assert comparison_gap["retrieved_brand_source_count"] == 1
    assert comparison_gap["retrieved_brand_highest_confidence"] == CONFIDENCE_HIGH
    assert comparison_gap["supported_retrieval_drivers"] == ["Comparison anchor"]
    assert "not proof of retrieval causality" in comparison_gap["interpretation"]


def test_compare_target_vs_retrieved_evidence_ignores_rejected_and_conflicting_items():
    items = [
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="entity",
        ),
        make_valid_evidence(
            brand="Reference Brand A",
            evidence_type="comparison",
            validation_status=STATUS_REJECTED,
        ),
        make_valid_evidence(
            brand="Reference Brand A",
            evidence_type="proof",
            validation_status=STATUS_CONFLICTING,
        ),
    ]

    gaps = compare_target_vs_retrieved_evidence(
        items,
        target_brand="Target Brand",
        retrieved_brands=["Reference Brand A"],
    )

    assert gaps == []


def test_compare_target_vs_retrieved_evidence_does_not_flag_existing_target_coverage():
    items = [
        make_valid_evidence(
            brand="Target Brand",
            evidence_type="comparison",
            supported_retrieval_driver="Comparison anchor",
        ),
        make_valid_evidence(
            brand="Reference Brand A",
            evidence_type="comparison",
            supported_retrieval_driver="Comparison anchor",
        ),
    ]

    gaps = compare_target_vs_retrieved_evidence(
        items,
        target_brand="Target Brand",
        retrieved_brands=["Reference Brand A"],
    )

    assert gaps == []


def test_summarize_evidence_gap_rows_aggregates_by_missing_evidence_type():
    gaps = compare_target_vs_retrieved_evidence(
        [
            make_valid_evidence(
                brand="Target Brand",
                evidence_type="entity",
            ),
            make_valid_evidence(
                brand="Reference Brand A",
                evidence_type="comparison",
                supported_retrieval_driver="Comparison anchor",
                confidence="Medium",
            ),
            make_valid_evidence(
                brand="Reference Brand B",
                evidence_type="comparison",
                supported_retrieval_driver="Alternative prompt eligibility",
                confidence="High",
            ),
            make_valid_evidence(
                brand="Reference Brand B",
                evidence_type="proof",
                supported_retrieval_driver="Trust / premium reference",
                confidence="Medium",
            ),
        ],
        target_brand="Target Brand",
        retrieved_brands=["Reference Brand A", "Reference Brand B"],
    )

    summary = summarize_evidence_gap_rows(gaps)

    comparison_summary = next(
        row for row in summary
        if row["missing_evidence_type"] == EVIDENCE_COMPARISON
    )

    assert comparison_summary["retrieved_brands_with_evidence"] == [
        "Reference Brand A",
        "Reference Brand B",
    ]
    assert comparison_summary["retrieved_brand_source_count"] == 2
    assert comparison_summary["highest_confidence"] == CONFIDENCE_HIGH
    assert comparison_summary["supported_retrieval_drivers"] == [
        "Alternative prompt eligibility",
        "Comparison anchor",
    ]
    assert "source-supported evidence gap" in comparison_summary["interpretation"]

    assert summary[0]["missing_evidence_type"] == EVIDENCE_COMPARISON


def test_summarize_evidence_gap_rows_returns_empty_list_for_no_gaps():
    assert summarize_evidence_gap_rows([]) == []