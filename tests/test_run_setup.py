from geo_audit.run_setup import (
    build_run_setup,
    estimate_api_calls,
    parse_competitor_input,
)


def test_parse_competitor_input_splits_comma_separated_competitors():
    competitors = parse_competitor_input(
        "NTT Global Data Centers, Equinix, Digital Realty, NorthC, maincubes, Drees & Sommer, Arup"
    )

    assert competitors == [
        "NTT Global Data Centers",
        "Equinix",
        "Digital Realty",
        "NorthC",
        "maincubes",
        "Drees & Sommer",
        "Arup",
    ]


def test_parse_competitor_input_preserves_newline_separated_competitors():
    competitors = parse_competitor_input(
        "Equinix\nDigital Realty\nArup"
    )

    assert competitors == ["Equinix", "Digital Realty", "Arup"]


def test_parse_competitor_input_splits_semicolon_separated_competitors():
    competitors = parse_competitor_input(
        "Equinix; Digital Realty; Arup"
    )

    assert competitors == ["Equinix", "Digital Realty", "Arup"]


def test_parse_competitor_input_handles_mixed_separators():
    competitors = parse_competitor_input(
        "Equinix, Digital Realty\nNorthC; maincubes\nDrees & Sommer"
    )

    assert competitors == [
        "Equinix",
        "Digital Realty",
        "NorthC",
        "maincubes",
        "Drees & Sommer",
    ]


def test_parse_competitor_input_strips_trailing_commas_and_whitespace():
    competitors = parse_competitor_input(
        " Digital Realty, \n Equinix ,\n ; Arup ; "
    )

    assert competitors == ["Digital Realty", "Equinix", "Arup"]


def test_parse_competitor_input_deduplicates_case_insensitively():
    competitors = parse_competitor_input(
        "Equinix, equinix, EQUINIX, Digital Realty"
    )

    assert competitors == ["Equinix", "Digital Realty"]


def test_parse_competitor_input_preserves_ampersand_names():
    competitors = parse_competitor_input("Drees & Sommer, Arup")

    assert competitors == ["Drees & Sommer", "Arup"]


def test_parse_competitor_input_splits_grouped_strings_inside_lists():
    competitors = parse_competitor_input([
        "NTT Global Data Centers, Equinix",
        "Digital Realty\nNorthC; maincubes",
        "Drees & Sommer",
    ])

    assert competitors == [
        "NTT Global Data Centers",
        "Equinix",
        "Digital Realty",
        "NorthC",
        "maincubes",
        "Drees & Sommer",
    ]


def test_parse_competitor_input_handles_none_and_empty_input():
    assert parse_competitor_input(None) == []
    assert parse_competitor_input("") == []
    assert parse_competitor_input(["", " , ; "]) == []


def test_build_run_setup_full_report_mode_returns_estimates_for_valid_inputs():
    configured_competitors = ["Competitor One", "Competitor Two", "Competitor Three"]

    run_setup = build_run_setup(
        target_brand="Acme Analytics",
        target_category="AI analytics platforms",
        target_market="United States",
        target_audience="B2B marketing teams",
        configured_competitors=configured_competitors,
        run_mode="Full Report Mode",
        prompt_limit=None,
        parsed_user_brand_strengths=["Fast onboarding", "Strong reporting"],
        model_name="gpt-4o-mini",
    )

    assert run_setup.current_competitors == configured_competitors
    assert run_setup.validation_errors == []
    assert run_setup.fixed_prompt_count > 0
    assert "effective_prompt_count" in run_setup.api_call_estimate
    assert run_setup.api_call_estimate["brand_understanding_probe_calls"] == 1
    assert run_setup.api_call_estimate["market_relevance_probe_calls"] == 1
    assert run_setup.brand_intelligence_estimated_calls >= 3
    assert (
        run_setup.estimated_total_ai_calls
        >= run_setup.api_call_estimate["estimated_pipeline_calls"]
    )
    assert "estimated_calls" in run_setup.api_cost_estimate


def test_build_run_setup_quick_test_mode_uses_prompt_limit():
    run_setup = build_run_setup(
        target_brand="Acme Analytics",
        target_category="AI analytics platforms",
        target_market="United States",
        target_audience="B2B marketing teams",
        configured_competitors=["Competitor One", "Competitor Two"],
        run_mode="Quick Test Mode",
        prompt_limit=3,
        parsed_user_brand_strengths=[],
        model_name="gpt-4o-mini",
    )

    expected_api_call_estimate = estimate_api_calls(
        fixed_prompt_count=run_setup.fixed_prompt_count,
        ai_generated_prompt_estimate=10,
        prompt_limit=3,
        run_mode="Quick Test Mode",
    )

    assert run_setup.api_call_estimate["effective_prompt_count"] == (
        expected_api_call_estimate["effective_prompt_count"]
    )
    assert run_setup.api_call_estimate["brand_understanding_probe_calls"] == 0
    assert run_setup.api_call_estimate["market_relevance_probe_calls"] == 0
    assert run_setup.validation_errors == []
    assert run_setup.current_analysis_context is not None


def test_build_run_setup_returns_validation_errors_for_invalid_inputs():
    run_setup = build_run_setup(
        target_brand="",
        target_category="AI analytics platforms",
        target_market="United States",
        target_audience="B2B marketing teams",
        configured_competitors=[],
        run_mode="Full Report Mode",
        prompt_limit=None,
        parsed_user_brand_strengths=[],
        model_name="gpt-4o-mini",
    )

    assert run_setup.validation_errors


def test_build_run_setup_returns_normalized_current_competitors_for_grouped_input():
    run_setup = build_run_setup(
        target_brand="Regional DC",
        target_category="data centers",
        target_market="Germany",
        target_audience="enterprise infrastructure buyers",
        configured_competitors=[
            "NTT Global Data Centers, Equinix",
            "Digital Realty\nNorthC; maincubes",
            "Drees & Sommer, Arup",
        ],
        run_mode="Full Report Mode",
        prompt_limit=None,
        parsed_user_brand_strengths=[],
        model_name="gpt-4o-mini",
    )

    assert run_setup.current_competitors == [
        "NTT Global Data Centers",
        "Equinix",
        "Digital Realty",
        "NorthC",
        "maincubes",
        "Drees & Sommer",
        "Arup",
    ]
