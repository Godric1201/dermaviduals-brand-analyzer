import json

import pandas as pd

from geo_audit import market_relevance
from geo_audit.market_relevance import (
    INTERPRETATION_GLOBAL_DEFAULT_RETRIEVAL_RISK,
    INTERPRETATION_INSUFFICIENT_EVIDENCE,
    LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE,
    MARKET_LOCK_GLOBAL_DEFAULT_RISK,
    MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    MarketRelevanceProbeResult,
    build_market_relevance_prompt,
    build_query_winners_context,
    build_top_visible_brands_context,
    parse_market_relevance_response,
    run_market_relevance_probe,
)


def valid_market_payload(**overrides):
    payload = {
        "market_lock_status": "Global-default risk",
        "local_brand_presence_signal": "Weak",
        "visible_market_fit": [
            {
                "brand": "Munich Re",
                "market_fit": "Global-default",
                "rationale": "Highly visible global category anchor.",
            }
        ],
        "global_default_risk_reason": "Visible brands are globally famous category leaders.",
        "market_evidence_gap_summary": "Local or regional market evidence is not visible in the benchmark context.",
        "recommended_interpretation": "Global-default retrieval risk",
        "validation_note": "AI-inferred market relevance probe. Validate before using as client-facing fact.",
    }
    payload.update(overrides)
    return payload


def sample_summary_df():
    return pd.DataFrame([
        {
            "brand": "Regional Re",
            "total_mentions": 0,
            "average_visibility_score": 0,
            "prompts_visible": 0,
            "share_of_voice_percent": 0,
        },
        {
            "brand": "Munich Re",
            "total_mentions": 18,
            "average_visibility_score": 75,
            "prompts_visible": 6,
            "share_of_voice_percent": 45,
        },
        {
            "brand": "Swiss Re",
            "total_mentions": 14,
            "average_visibility_score": 68,
            "prompts_visible": 5,
            "share_of_voice_percent": 35,
        },
    ])


def sample_detailed_df():
    return pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "Munich Re",
            "visibility_score": 75,
        },
        {
            "prompt_category": "Local Recommendations",
            "brand": "Swiss Re",
            "visibility_score": 60,
        },
        {
            "prompt_category": "Best Options",
            "brand": "Regional Re",
            "visibility_score": 0,
        },
    ])


def test_compact_context_helpers_extract_visible_brands_and_query_winners():
    visible_brands = build_top_visible_brands_context(
        sample_summary_df(),
        "Regional Re",
    )
    query_winners = build_query_winners_context(sample_detailed_df())

    assert visible_brands[0]["brand"] == "Munich Re"
    assert visible_brands[1]["brand"] == "Swiss Re"
    assert {row["brand"] for row in query_winners} == {"Munich Re", "Swiss Re"}


def test_market_relevance_prompt_includes_target_context_and_compact_benchmark_context():
    visible_brands = build_top_visible_brands_context(
        sample_summary_df(),
        "Regional Re",
    )
    query_winners = build_query_winners_context(sample_detailed_df())

    prompt = build_market_relevance_prompt(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
        visible_brands=visible_brands,
        query_winners=query_winners,
        prompt_categories=["Best Options", "Local Recommendations"],
        brand_understanding={
            "brand_known_status": "Clear",
            "diagnosis_summary": "The brand appears understood.",
        },
    )

    assert "Regional Re" in prompt
    assert "reinsurance" in prompt
    assert "Taiwan and Asia-Pacific" in prompt
    assert "enterprise insurance buyers" in prompt
    assert "Munich Re" in prompt
    assert "Swiss Re" in prompt
    assert "Best Options" in prompt
    assert "Local Recommendations" in prompt
    assert "The brand appears understood." in prompt
    assert "Return ONLY valid JSON" in prompt


def test_valid_json_parses_into_market_relevance_result():
    result = parse_market_relevance_response(json.dumps(valid_market_payload()))

    assert isinstance(result, MarketRelevanceProbeResult)
    assert result.market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK
    assert result.visible_market_fit[0]["market_fit"] == "Global-default"
    assert result.recommended_interpretation == (
        INTERPRETATION_GLOBAL_DEFAULT_RETRIEVAL_RISK
    )


def test_fenced_json_parses_when_present():
    response = "```json\n" + json.dumps(valid_market_payload()) + "\n```"

    result = parse_market_relevance_response(response)

    assert result.market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK


def test_malformed_json_returns_fallback():
    result = parse_market_relevance_response(
        "not json",
        market="Taiwan and Asia-Pacific",
    )

    assert result.market_lock_status == MARKET_LOCK_INSUFFICIENT_EVIDENCE
    assert result.local_brand_presence_signal == LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE
    assert result.recommended_interpretation == INTERPRETATION_INSUFFICIENT_EVIDENCE


def test_missing_fields_normalize_safely():
    result = parse_market_relevance_response(
        json.dumps({
            "market_lock_status": "Global-default risk",
            "recommended_interpretation": "Global-default retrieval risk",
        })
    )

    assert result.market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK
    assert result.local_brand_presence_signal == LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE
    assert result.visible_market_fit == []
    assert result.global_default_risk_reason
    assert result.market_evidence_gap_summary


def test_unknown_labels_normalize_to_safe_defaults():
    result = parse_market_relevance_response(
        json.dumps(valid_market_payload(
            market_lock_status="Definitely local",
            local_brand_presence_signal="Lots",
            visible_market_fit=[
                {
                    "brand": "Munich Re",
                    "market_fit": "Dominant",
                    "rationale": "Known brand.",
                }
            ],
            recommended_interpretation="Sales issue",
        ))
    )

    assert result.market_lock_status == MARKET_LOCK_INSUFFICIENT_EVIDENCE
    assert result.local_brand_presence_signal == LOCAL_SIGNAL_NOT_ENOUGH_EVIDENCE
    assert result.visible_market_fit[0]["market_fit"] == "Unclear"
    assert result.recommended_interpretation == INTERPRETATION_INSUFFICIENT_EVIDENCE


def test_run_market_relevance_probe_uses_structured_single_call(monkeypatch):
    captured_kwargs = {}

    class FakeMessage:
        content = json.dumps(valid_market_payload())

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
        market_relevance.analyzer,
        "get_openai_client",
        lambda: FakeClient(),
        raising=False,
    )

    result = run_market_relevance_probe(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
        summary_df=sample_summary_df(),
        detailed_df=sample_detailed_df(),
        prompt_categories=["Best Options", "Local Recommendations"],
    )

    assert result.market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK
    assert captured_kwargs["temperature"] == 0
    assert captured_kwargs["max_tokens"] <= 1000
    assert len(captured_kwargs["messages"]) == 2
    assert "Munich Re" in captured_kwargs["messages"][1]["content"]


def test_run_market_relevance_probe_falls_back_without_real_api(monkeypatch):
    def raise_error():
        raise RuntimeError("no api")

    monkeypatch.setattr(
        market_relevance.analyzer,
        "get_openai_client",
        raise_error,
        raising=False,
    )

    result = run_market_relevance_probe(
        brand="Regional Re",
        category="reinsurance",
        market="Taiwan and Asia-Pacific",
        audience="enterprise insurance buyers",
        summary_df=sample_summary_df(),
        detailed_df=sample_detailed_df(),
    )

    assert result.market_lock_status == MARKET_LOCK_INSUFFICIENT_EVIDENCE
