TOKENS_PER_MILLION = 1_000_000

LOW_TOKEN_ASSUMPTION = {
    "input_tokens": 1500,
    "output_tokens": 500,
}
HIGH_TOKEN_ASSUMPTION = {
    "input_tokens": 4000,
    "output_tokens": 1500,
}

MODEL_PRICING_ASSUMPTIONS = {
    "gpt-4o-mini": {
        "label": "gpt-4o-mini text token pricing",
        "input_usd_per_1m_tokens": 0.15,
        "output_usd_per_1m_tokens": 0.60,
    },
}


def normalize_model_name(model_name):
    return str(model_name or "").strip().lower()


def get_pricing_assumption(model_name):
    return MODEL_PRICING_ASSUMPTIONS.get(normalize_model_name(model_name))


def calculate_cost_usd(call_count, token_assumption, pricing_assumption):
    calls = max(0, int(call_count or 0))
    input_cost = (
        calls
        * token_assumption["input_tokens"]
        / TOKENS_PER_MILLION
        * pricing_assumption["input_usd_per_1m_tokens"]
    )
    output_cost = (
        calls
        * token_assumption["output_tokens"]
        / TOKENS_PER_MILLION
        * pricing_assumption["output_usd_per_1m_tokens"]
    )

    return input_cost + output_cost


def format_usd(value):
    if value <= 0:
        return "USD 0.00"

    if value < 0.01:
        return "< USD 0.01"

    return f"USD {value:.2f}"


def format_cost_range(low_usd, high_usd):
    return f"approx. {format_usd(low_usd)} - {format_usd(high_usd)}"


def estimate_api_cost_range(call_count, model_name):
    calls = max(0, int(call_count or 0))
    pricing_assumption = get_pricing_assumption(model_name)

    if pricing_assumption is None:
        return {
            "estimated_calls": calls,
            "model_name": model_name,
            "pricing_available": False,
            "pricing_label": None,
            "low_usd": None,
            "high_usd": None,
            "formatted_cost_range": None,
        }

    low_usd = calculate_cost_usd(
        calls,
        LOW_TOKEN_ASSUMPTION,
        pricing_assumption,
    )
    high_usd = calculate_cost_usd(
        calls,
        HIGH_TOKEN_ASSUMPTION,
        pricing_assumption,
    )

    if high_usd < low_usd:
        low_usd, high_usd = high_usd, low_usd

    return {
        "estimated_calls": calls,
        "model_name": model_name,
        "pricing_available": True,
        "pricing_label": pricing_assumption["label"],
        "low_usd": low_usd,
        "high_usd": high_usd,
        "formatted_cost_range": format_cost_range(low_usd, high_usd),
    }
