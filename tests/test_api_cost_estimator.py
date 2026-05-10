import pytest

from geo_audit.api_cost_estimator import (
    HIGH_TOKEN_ASSUMPTION,
    LOW_TOKEN_ASSUMPTION,
    calculate_cost_usd,
    estimate_api_cost_range,
    estimate_actual_usage_cost,
    format_cost_range,
    get_pricing_assumption,
)


def test_gpt_4o_mini_pricing_defaults():
    pricing = get_pricing_assumption("gpt-4o-mini")

    assert pricing["label"] == "gpt-4o-mini text token pricing"
    assert pricing["input_usd_per_1m_tokens"] == 0.15
    assert pricing["output_usd_per_1m_tokens"] == 0.60


def test_low_and_high_estimate_calculation():
    pricing = get_pricing_assumption("gpt-4o-mini")

    low = calculate_cost_usd(100, LOW_TOKEN_ASSUMPTION, pricing)
    high = calculate_cost_usd(100, HIGH_TOKEN_ASSUMPTION, pricing)

    assert low == pytest.approx(0.0525)
    assert high == pytest.approx(0.15)


def test_unknown_model_fallback():
    estimate = estimate_api_cost_range(25, "custom-model")

    assert estimate["estimated_calls"] == 25
    assert estimate["pricing_available"] is False
    assert estimate["pricing_label"] is None
    assert estimate["low_usd"] is None
    assert estimate["high_usd"] is None
    assert estimate["formatted_cost_range"] is None


def test_formatted_cost_range():
    assert format_cost_range(0.0525, 0.15) == "approx. USD 0.05 - USD 0.15"


def test_high_estimate_is_greater_than_or_equal_to_low_estimate():
    estimate = estimate_api_cost_range(40, "gpt-4o-mini")

    assert estimate["pricing_available"] is True
    assert estimate["high_usd"] >= estimate["low_usd"]

def test_format_cost_range_handles_sub_cent_values():
    assert format_cost_range(0.004, 0.02) == "approx. < USD 0.01 - USD 0.02"


def test_estimate_actual_usage_cost_for_known_model():
    estimate = estimate_actual_usage_cost(1_000_000, 500_000, "gpt-4o-mini")

    assert estimate["pricing_available"] is True
    assert estimate["pricing_label"] == "gpt-4o-mini text token pricing"
    assert estimate["estimated_actual_cost_usd"] == pytest.approx(0.45)


def test_estimate_actual_usage_cost_unknown_model_fallback():
    estimate = estimate_actual_usage_cost(1000, 500, "custom-model")

    assert estimate["pricing_available"] is False
    assert estimate["pricing_label"] is None
    assert estimate["estimated_actual_cost_usd"] is None
