from dataclasses import dataclass

from geo_audit.api_cost_estimator import estimate_api_cost_range
from geo_audit.brand_intelligence_prompts import build_target_diagnostic_prompts
from geo_audit.prompts import build_fixed_prompts


@dataclass(frozen=True)
class RunSetup:
    current_competitors: list[str]
    current_analysis_context: object
    validation_errors: list[str]
    validation_warnings: list[str]
    fixed_prompt_count: int
    api_call_estimate: dict
    brand_intelligence_estimated_calls: int
    estimated_total_ai_calls: int
    api_cost_estimate: dict


def normalize_context_text(value):
    return " ".join(str(value).strip().split())


def normalize_competitors(competitors):
    return [
        normalized
        for normalized in [
            normalize_context_text(competitor)
            for competitor in competitors
        ]
        if normalized
    ]


def build_analysis_context(
    brand,
    category,
    market,
    audience,
    competitors,
    run_mode,
    prompt_limit,
    user_brand_strengths=None,
):
    return {
        "brand": normalize_context_text(brand),
        "category": normalize_context_text(category),
        "market": normalize_context_text(market),
        "audience": normalize_context_text(audience),
        "competitors": normalize_competitors(competitors),
        "run_mode": run_mode,
        "prompt_limit": prompt_limit,
        "user_brand_strengths": normalize_competitors(user_brand_strengths or []),
    }


def validate_run_inputs(brand, category, market, audience, competitors):
    errors = []

    if not normalize_context_text(brand):
        errors.append("Target Brand is required.")
    if not normalize_context_text(category):
        errors.append("Category is required.")
    if not normalize_context_text(market):
        errors.append("Market is required.")
    if not normalize_context_text(audience):
        errors.append("Audience is required.")
    if not normalize_competitors(competitors):
        errors.append("At least one competitor is required.")

    return errors


def get_run_warnings(competitors, run_mode):
    warnings = []

    if (
        run_mode == "Full Report Mode"
        and len(normalize_competitors(competitors)) < 3
    ):
        warnings.append("Full Report Mode works best with at least 3 competitors.")

    return warnings


def estimate_api_calls(
    fixed_prompt_count,
    ai_generated_prompt_estimate,
    prompt_limit,
    run_mode,
    geo_content_roadmap_calls=1,
):
    estimated_total_prompts = (
        fixed_prompt_count + ai_generated_prompt_estimate
    )

    if run_mode == "Quick Test Mode" and prompt_limit is not None:
        effective_prompt_count = min(
            estimated_total_prompts,
            int(prompt_limit)
        )
    else:
        effective_prompt_count = estimated_total_prompts

    prompt_generation_calls = 1
    ai_answer_generation_calls = effective_prompt_count
    recommendation_calls = 1
    strategy_report_calls = 1

    return {
        "fixed_prompt_count": fixed_prompt_count,
        "ai_generated_prompt_estimate": ai_generated_prompt_estimate,
        "estimated_total_prompts": estimated_total_prompts,
        "effective_prompt_count": effective_prompt_count,
        "prompt_generation_calls": prompt_generation_calls,
        "ai_answer_generation_calls": ai_answer_generation_calls,
        "recommendation_calls": recommendation_calls,
        "strategy_report_calls": strategy_report_calls,
        "geo_content_roadmap_calls": geo_content_roadmap_calls,
        "estimated_pipeline_calls": (
            prompt_generation_calls
            + ai_answer_generation_calls
            + recommendation_calls
            + strategy_report_calls
            + geo_content_roadmap_calls
        ),
        "auto_result_narrative_calls_estimate": 3,
    }


def estimate_total_ai_calls(api_call_estimate, brand_intelligence_calls):
    return (
        api_call_estimate["estimated_pipeline_calls"]
        + brand_intelligence_calls
        + api_call_estimate["auto_result_narrative_calls_estimate"]
    )


def build_run_setup(
    *,
    target_brand,
    target_category,
    target_market,
    target_audience,
    configured_competitors,
    run_mode,
    prompt_limit,
    parsed_user_brand_strengths,
    model_name,
):
    current_competitors = configured_competitors
    current_analysis_context = build_analysis_context(
        brand=target_brand,
        category=target_category,
        market=target_market,
        audience=target_audience,
        competitors=current_competitors,
        run_mode=run_mode,
        prompt_limit=prompt_limit,
        user_brand_strengths=parsed_user_brand_strengths,
    )

    validation_errors = validate_run_inputs(
        brand=target_brand,
        category=target_category,
        market=target_market,
        audience=target_audience,
        competitors=current_competitors
    )
    validation_warnings = get_run_warnings(
        competitors=current_competitors,
        run_mode=run_mode
    )
    fixed_prompt_count = len(build_fixed_prompts(
        category=target_category,
        market=target_market,
        audience=target_audience
    ))
    api_call_estimate = estimate_api_calls(
        fixed_prompt_count=fixed_prompt_count,
        ai_generated_prompt_estimate=10,
        prompt_limit=prompt_limit,
        run_mode=run_mode
    )
    brand_intelligence_estimated_calls = len(build_target_diagnostic_prompts(
        brand=target_brand,
        category=target_category,
        market=target_market,
        audience=target_audience,
        competitors=current_competitors,
        user_brand_strengths=parsed_user_brand_strengths,
    )) + 3
    estimated_total_ai_calls = estimate_total_ai_calls(
        api_call_estimate,
        brand_intelligence_estimated_calls,
    )
    api_cost_estimate = estimate_api_cost_range(
        estimated_total_ai_calls,
        model_name,
    )

    return RunSetup(
        current_competitors=current_competitors,
        current_analysis_context=current_analysis_context,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings,
        fixed_prompt_count=fixed_prompt_count,
        api_call_estimate=api_call_estimate,
        brand_intelligence_estimated_calls=brand_intelligence_estimated_calls,
        estimated_total_ai_calls=estimated_total_ai_calls,
        api_cost_estimate=api_cost_estimate,
    )
