from analyzer import ask_ai
from brand_intelligence_prompts import (
    build_target_diagnostic_prompts,
    parse_user_brand_strengths,
)


VALIDATION_NOTE = (
    "AI-inferred diagnostic output. Validate before using as client-facing fact."
)


def _normalize_user_brand_strengths(user_brand_strengths):
    if user_brand_strengths is None:
        return []

    if isinstance(user_brand_strengths, str):
        return parse_user_brand_strengths(user_brand_strengths)

    return list(user_brand_strengths)


def _dataframe_preview(df, max_rows=40):
    if df is None:
        return "No data provided."

    if hasattr(df, "empty") and df.empty:
        return "No data provided."

    if hasattr(df, "head") and hasattr(df, "to_string"):
        return df.head(max_rows).to_string(index=False)

    return str(df)


def _raw_answers_preview(raw_answers, max_items=10):
    if not raw_answers:
        return "No benchmark answers provided."

    return str(raw_answers[:max_items])


def _get_target_benchmark_visibility_context(summary_df, brand):
    if summary_df is None or getattr(summary_df, "empty", False):
        return "No benchmark visibility summary was provided."

    if "brand" not in summary_df.columns:
        return "No benchmark visibility summary was provided."

    brand_rows = summary_df[
        summary_df["brand"].astype(str).str.lower() == str(brand).lower()
    ]

    if brand_rows.empty:
        return f"No benchmark summary row was found for {brand}."

    row = brand_rows.iloc[0]

    mentions = row.get("total_mentions", 0)
    average_visibility = row.get("average_visibility_score", 0)
    prompts_visible = row.get("prompts_visible", 0)
    share_of_voice = row.get("share_of_voice_percent", 0)

    return (
        f"Unbranded benchmark visibility for {brand}: "
        f"{mentions} total mentions, "
        f"{average_visibility} average visibility score, "
        f"{prompts_visible} prompts visible, "
        f"{share_of_voice}% share of voice."
    )


def build_recommendation_driver_prompt(
    brand,
    category,
    market,
    audience,
    competitors,
    raw_answers,
    summary_df,
    detailed_df,
):
    return f"""
You are analyzing benchmark AI answers for Brand Intelligence and Positioning Gap Analysis.

This analysis is derived from benchmark answers; not a visibility score.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Competitors:
{", ".join(competitors)}

Summary Data:
{_dataframe_preview(summary_df)}

Detailed Data:
{_dataframe_preview(detailed_df)}

Benchmark Raw Answers:
{_raw_answers_preview(raw_answers)}

Task:
Extract the recurring recommendation drivers that appear in the benchmark answers.

Return:
- Recurring recommendation drivers
- Competitor advantage signals
- Evidence patterns from benchmark answers
- Unmet query intents

Rules:
- Do not treat this as a scoring calculation.
- Do not create visibility scores, share of voice, or rankings.
- Avoid unsupported factual claims.
- Label uncertain observations clearly.
""".strip()


def build_target_understanding_prompt(
    brand,
    category,
    market,
    audience,
    diagnostic_answers,
    benchmark_visibility_context,
):
    return f"""
You are synthesizing target-brand diagnostic answers for Brand Intelligence and Positioning Gap Analysis.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Benchmark Visibility Context:
{benchmark_visibility_context}

Diagnostic Answers:
{diagnostic_answers}

Task:
Summarize how AI appears to understand the target brand.

Return:
- AI-inferred strengths
- Weak associations
- Missing evidence
- Uncertainties
- Prompted Diagnostic Fit

Rules:
- AI-inferred; validate before using as client-facing fact.
- Distinguish inferred observations from verified facts.
- Natural benchmark visibility comes from the unbranded benchmark.
- Prompted diagnostic fit is a target-branded diagnostic assessment requiring validation.
- If the benchmark shows 0 mentions or 0 share of voice, describe fit as potential, prompted, or subject to validation, not as natural recommendation visibility.
- Avoid unsupported factual claims.
""".strip()


def build_positioning_gap_prompt(
    brand,
    category,
    market,
    audience,
    recommendation_drivers,
    target_brand_understanding,
    user_brand_strengths,
):
    return f"""
You are creating a positioning gap analysis for Brand Intelligence.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Recommendation Drivers:
{recommendation_drivers}

Target Brand Understanding:
{target_brand_understanding}

User-Provided Brand Strengths:
{user_brand_strengths}

Task:
Compare category recommendation drivers, competitor advantage signals, AI-inferred target brand understanding, and user-provided brand strengths.

Return:
- Missing associations
- Strongest opportunity territories
- Content priorities
- PR / trust signal priorities
- Competitor attack angles
- Evidence gaps
- Recommended next steps

Rules:
- Do not produce unsupported factual claims.
- Label AI-inferred findings clearly.
- Treat user-provided strengths as client-provided notes that still need evidence.
- Do not create or modify visibility scores, share of voice, or rankings.
""".strip()


def run_brand_intelligence_analysis(
    brand,
    category,
    market,
    audience,
    competitors,
    raw_answers,
    summary_df,
    detailed_df,
    user_brand_strengths=None,
    answer_language="English",
    report_language="English",
    on_progress=None,
):
    user_brand_strengths = _normalize_user_brand_strengths(user_brand_strengths)

    diagnostic_prompts = build_target_diagnostic_prompts(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        user_brand_strengths=user_brand_strengths,
    )

    if on_progress is not None:
        on_progress("diagnostic_prompts")

    diagnostic_answers = []

    for item in diagnostic_prompts:
        answer = ask_ai(item["prompt"], answer_language)
        diagnostic_answers.append({
            "category": item["category"],
            "prompt": item["prompt"],
            "answer": answer,
        })

    if on_progress is not None:
        on_progress("recommendation_drivers")

    recommendation_drivers = ask_ai(
        build_recommendation_driver_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            competitors=competitors,
            raw_answers=raw_answers,
            summary_df=summary_df,
            detailed_df=detailed_df,
        ),
        report_language,
    )

    if on_progress is not None:
        on_progress("target_understanding")

    target_brand_understanding = ask_ai(
        build_target_understanding_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            diagnostic_answers=diagnostic_answers,
            benchmark_visibility_context=_get_target_benchmark_visibility_context(
                summary_df,
                brand,
            ),
        ),
        report_language,
    )

    if on_progress is not None:
        on_progress("positioning_gap")

    positioning_gap_analysis = ask_ai(
        build_positioning_gap_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            recommendation_drivers=recommendation_drivers,
            target_brand_understanding=target_brand_understanding,
            user_brand_strengths=user_brand_strengths,
        ),
        report_language,
    )

    return {
        "diagnostic_prompts": diagnostic_prompts,
        "diagnostic_answers": diagnostic_answers,
        "recommendation_drivers": recommendation_drivers,
        "target_brand_understanding": target_brand_understanding,
        "positioning_gap_analysis": positioning_gap_analysis,
        "user_brand_strengths": user_brand_strengths,
        "validation_note": VALIDATION_NOTE,
    }
