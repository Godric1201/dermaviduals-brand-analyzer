from geo_audit.run_setup import build_run_setup, estimate_api_calls


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
