import re

from analyzer import ask_ai
from brand_intelligence_prompts import (
    build_target_diagnostic_prompts,
    parse_user_brand_strengths,
)


VALIDATION_NOTE = (
    "AI-inferred diagnostic output. Validate before using as client-facing fact."
)

SOURCE_LABEL_PATTERN = re.compile(
    r"\(Source:\s*(Tracked competitor|AI-discovered market signal)\)",
    re.IGNORECASE,
)


def _normalize_user_brand_strengths(user_brand_strengths):
    if user_brand_strengths is None:
        return []

    if isinstance(user_brand_strengths, str):
        return parse_user_brand_strengths(user_brand_strengths)

    return list(user_brand_strengths)


def normalize_brand_name(value):
    return " ".join(str(value or "").strip().lower().split())


def is_tracked_competitor(brand_name, tracked_competitors):
    normalized_brand = normalize_brand_name(brand_name)
    normalized_tracked = {
        normalize_brand_name(item)
        for item in (tracked_competitors or [])
        if normalize_brand_name(item)
    }
    return normalized_brand in normalized_tracked


def _extract_labeled_brand_name(line):
    if "(Source:" not in line:
        return None

    bold_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*\*\*(?P<brand>[^*]+)\*\*",
        line,
    )
    if bold_match:
        return bold_match.group("brand").strip()

    plain_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*(?P<brand>[^–—:\-()]+?)\s*(?:[–—:-])",
        line,
    )
    if plain_match:
        return plain_match.group("brand").strip()

    return None


def correct_competitor_source_labels(text, tracked_competitors):
    corrected_lines = []

    for line in str(text).splitlines():
        label_match = SOURCE_LABEL_PATTERN.search(line)
        brand_name = _extract_labeled_brand_name(line)

        if not label_match or not brand_name:
            corrected_lines.append(line)
            continue

        expected_label = (
            "Tracked competitor"
            if is_tracked_competitor(brand_name, tracked_competitors)
            else "AI-discovered market signal"
        )

        corrected_lines.append(
            SOURCE_LABEL_PATTERN.sub(
                f"(Source: {expected_label})",
                line,
                count=1,
            )
        )

    return "\n".join(corrected_lines)


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
- Top 5 recurring recommendation drivers
- Top 5 competitor advantage signals
- Evidence patterns from benchmark answers
- Unmet query intents
- Tracked Competitors Included in Scoring
- AI-Discovered Market Signals Not Included in Scoring
- If listing competitor advantage signals, label each item with Source: Tracked competitor or Source: AI-discovered market signal

Format:
- Prefer compact tables or bullet lists over long paragraphs.
- Clearly label each signal as Benchmark-derived, AI-inferred, or User-provided where relevant.

Rules:
- Do not treat this as a scoring calculation.
- Do not create visibility scores, share of voice, or rankings.
- Treat competitors listed above as tracked competitors used for benchmark scoring.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- If other brands appear in raw answers, describe them as AI-discovered market signals only.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Do not call non-tracked brands competitors included in benchmark.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
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
- Top competitor-owned associations
- Tracked Competitors Included in Scoring
- AI-Discovered Market Signals Not Included in Scoring
- Action implications

Format:
- Prefer compact tables or bullet lists over long paragraphs.
- Clearly label signals as Benchmark-derived, AI-inferred, or User-provided where relevant.

Rules:
- AI-inferred; validate before using as client-facing fact.
- Distinguish inferred observations from verified facts.
- Natural benchmark visibility comes from the unbranded benchmark.
- Prompted diagnostic fit is a target-branded diagnostic assessment requiring validation.
- Distinguish tracked competitors from AI-discovered market signals.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
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
- For each missing association include:
  - Association
  - Source: benchmark-derived / AI-inferred / user-provided
  - Why It Matters
  - Evidence Needed
  - Recommended Action
- Strongest opportunity territories
- Review / Trust Signal Gaps
- Content priorities
- PR / trust signal priorities
- Recommended next steps

Rules:
- Prefer compact tables or bullet lists over long paragraphs.
- Do not produce unsupported factual claims.
- Label AI-inferred findings clearly.
- Clearly label each signal as Benchmark-derived, AI-inferred, or User-provided.
- Distinguish tracked competitors from AI-discovered market signals.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Include separate sections titled Tracked Competitors Included in Scoring and AI-Discovered Market Signals Not Included in Scoring where relevant.
- If non-tracked brands are mentioned, label them as Source: AI-discovered market signal.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Do not call non-tracked brands competitors included in benchmark.
- Treat user-provided strengths as client-provided notes that still need evidence.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
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
    recommendation_drivers = correct_competitor_source_labels(
        recommendation_drivers,
        competitors,
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
    target_brand_understanding = correct_competitor_source_labels(
        target_brand_understanding,
        competitors,
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
    positioning_gap_analysis = correct_competitor_source_labels(
        positioning_gap_analysis,
        competitors,
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
