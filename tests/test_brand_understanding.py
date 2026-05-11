import json

from geo_audit import brand_understanding
from geo_audit.brand_understanding import (
    INTERPRETATION_MIXED_DIAGNOSIS,
    INTERPRETATION_RECOMMENDATION_RETRIEVAL_GAP,
    STATUS_CLEAR,
    STATUS_MISALIGNED,
    STATUS_NOT_ENOUGH_EVIDENCE,
    BrandUnderstandingProbeResult,
    build_brand_understanding_prompt,
    parse_brand_understanding_response,
    run_brand_understanding_probe,
)


def valid_probe_payload(**overrides):
    payload = {
        "brand_known_status": "Clear",
        "inferred_category": "Regional reinsurance provider",
        "category_alignment": "Clear",
        "inferred_market": "Taiwan and Asia-Pacific",
        "market_alignment": "Partial",
        "inferred_audience": "Enterprise insurance buyers",
        "audience_alignment": "Clear",
        "inferred_offerings": ["Treaty reinsurance", "risk transfer"],
        "inferred_strengths": ["Regional market knowledge"],
        "missing_or_uncertain_evidence": ["Independent proof points"],
        "possible_hallucinations": ["Specific customer names would need verification"],
        "diagnosis_summary": "The brand appears known but needs validation.",
        "recommended_interpretation": "Recommendation retrieval gap",
        "validation_note": "AI-inferred brand understanding probe. Validate before using as client-facing fact.",
    }
    payload.update(overrides)
    return payload


def test_brand_understanding_prompt_includes_target_context():
    prompt = build_brand_understanding_prompt(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
    )

    assert "Regional Re" in prompt
    assert "reinsurance" in prompt
    assert "Taiwan and Asia-Pacific" in prompt
    assert "enterprise insurance buyers" in prompt
    assert "Return ONLY valid JSON" in prompt


def test_valid_json_parses_into_probe_result():
    result = parse_brand_understanding_response(
        json.dumps(valid_probe_payload()),
        brand="Regional Re",
    )

    assert isinstance(result, BrandUnderstandingProbeResult)
    assert result.brand_known_status == STATUS_CLEAR
    assert result.inferred_category == "Regional reinsurance provider"
    assert result.inferred_offerings == ["Treaty reinsurance", "risk transfer"]
    assert result.recommended_interpretation == (
        INTERPRETATION_RECOMMENDATION_RETRIEVAL_GAP
    )


def test_fenced_json_parses_when_present():
    response = "```json\n" + json.dumps(valid_probe_payload()) + "\n```"

    result = parse_brand_understanding_response(response)

    assert result.brand_known_status == STATUS_CLEAR
    assert result.category_alignment == STATUS_CLEAR


def test_malformed_json_returns_fallback():
    result = parse_brand_understanding_response(
        "not json",
        brand="Regional Re",
    )

    assert result.brand_known_status == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.recommended_interpretation == INTERPRETATION_MIXED_DIAGNOSIS
    assert result.missing_or_uncertain_evidence


def test_missing_fields_normalize_safely():
    result = parse_brand_understanding_response(
        json.dumps({
            "brand_known_status": "Clear",
            "recommended_interpretation": "Recommendation retrieval gap",
        })
    )

    assert result.brand_known_status == STATUS_CLEAR
    assert result.category_alignment == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.inferred_offerings == []
    assert result.inferred_strengths == []
    assert result.missing_or_uncertain_evidence == []
    assert result.possible_hallucinations == []


def test_unknown_statuses_and_interpretations_use_safe_defaults():
    result = parse_brand_understanding_response(
        json.dumps(valid_probe_payload(
            brand_known_status="Famous",
            category_alignment="Looks good",
            market_alignment="wrong market",
            audience_alignment="unknown-ish",
            recommended_interpretation="SEO opportunity",
        ))
    )

    assert result.brand_known_status == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.category_alignment == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.market_alignment == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.audience_alignment == STATUS_NOT_ENOUGH_EVIDENCE
    assert result.recommended_interpretation == INTERPRETATION_MIXED_DIAGNOSIS


def test_supported_status_variants_normalize_case_and_separators():
    result = parse_brand_understanding_response(
        json.dumps(valid_probe_payload(
            brand_known_status="clear",
            category_alignment="mis-aligned",
            recommended_interpretation="recommendation_retrieval_gap",
        ))
    )

    assert result.brand_known_status == STATUS_CLEAR
    assert result.category_alignment == STATUS_MISALIGNED
    assert result.recommended_interpretation == (
        INTERPRETATION_RECOMMENDATION_RETRIEVAL_GAP
    )


def test_run_brand_understanding_probe_uses_structured_single_call(monkeypatch):
    captured_kwargs = {}

    class FakeMessage:
        content = json.dumps(valid_probe_payload())

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        model = "gpt-4o-mini"
        choices = [FakeChoice()]
        usage = None

    class FakeCompletions:
        def create(self, **kwargs):
            captured_kwargs.update(kwargs)
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(
        brand_understanding.analyzer,
        "get_openai_client",
        lambda: FakeClient(),
        raising=False,
    )

    result = run_brand_understanding_probe(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
    )

    assert result.brand_known_status == STATUS_CLEAR
    assert captured_kwargs["temperature"] == 0
    assert captured_kwargs["max_tokens"] <= 1000
    assert len(captured_kwargs["messages"]) == 2


def test_run_brand_understanding_probe_falls_back_without_real_api(monkeypatch):
    def raise_error():
        raise RuntimeError("no api")

    monkeypatch.setattr(
        brand_understanding.analyzer,
        "get_openai_client",
        raise_error,
        raising=False,
    )

    result = run_brand_understanding_probe(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
    )

    assert result.brand_known_status == STATUS_NOT_ENOUGH_EVIDENCE
