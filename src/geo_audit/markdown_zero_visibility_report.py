import pandas as pd

from .ui_formatters import df_to_markdown_table
from .brand_understanding import (
    STATUS_CLEAR,
    STATUS_MISALIGNED,
    STATUS_PARTIAL,
    STATUS_UNCLEAR,
    STATUS_NOT_ENOUGH_EVIDENCE,
)
from .market_relevance import (
    MARKET_LOCK_GLOBAL_DEFAULT_RISK,
    MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    MARKET_LOCK_MARKET_SPECIFIC,
    MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC,
)
from .source_evidence_markdown import render_source_evidence_summary_section
from .report_diagnosis import (
    build_first_three_evidence_assets,
    build_evidence_gap_map,
    build_market_relevance_interpretation,
    build_retrieved_brand_profiles,
    build_validation_plan,
    build_visible_reference_brands,
    classify_benchmark_reliability,
)


def _build_methodology_notes_md(category, prompt_categories):
    notes = [
        f"- This AI visibility benchmark is based on fixed and AI-generated prompts designed to simulate {category} recommendation queries.",
        "- Visibility is calculated from brand mentions, estimated ranking, and prompt-level appearance within the tested prompt set.",
        "- Share of voice reflects the distribution of brand mentions among tracked competitors in this benchmark run.",
        "- Scores reflect AI answer visibility, not market share, product performance, customer satisfaction, or broader business performance outcomes.",
        "- The output should be interpreted as an AI visibility benchmark, not as a consumer survey, sales performance report, or clinical evaluation.",
        "- Results should be re-run periodically to track whether content and visibility interventions produce stronger benchmark signals over time.",
    ]

    if prompt_categories:
        notes.append("")
        notes.append("Query intent coverage included:")
        notes.extend(f"- {item}" for item in prompt_categories)

    return "\n".join(notes)


def _get_probe_field(brand_understanding, field, default=""):
    if brand_understanding is None:
        return default

    if isinstance(brand_understanding, dict):
        return brand_understanding.get(field, default)

    return getattr(brand_understanding, field, default)


def _format_key_value_bullets(items):
    return "\n".join(
        f"- {label}: {value}"
        for label, value in items
        if str(value or "").strip()
    )


def _build_evidence_gap_cards_md(gaps):
    cards = []

    for row in gaps:
        evidence_type = row.get("Evidence Type", "Evidence Gap")
        cards.append(
            f"**{evidence_type}**\n"
            f"- Current diagnosis: {row.get('Current Diagnosis', '')}\n"
            f"- Gap addressed: {row.get('Gap Addressed', '')}\n"
            f"- Why it matters: {row.get('Why It Matters', '')}\n"
            f"- Validation: {row.get('Validation Method', '')}"
        )

    return "\n\n".join(cards)


def _build_visible_market_fit_bullets(rows):
    bullets = []

    for row in rows or []:
        if not isinstance(row, dict):
            continue

        brand = str(row.get("brand", "")).strip()
        market_fit = str(row.get("market_fit", "")).strip()
        rationale = str(row.get("rationale", "")).strip()

        if not brand:
            continue

        if market_fit and rationale:
            bullets.append(f"- {brand} — {market_fit}: {rationale}")
        elif market_fit:
            bullets.append(f"- {brand} — {market_fit}")
        elif rationale:
            bullets.append(f"- {brand}: {rationale}")
        else:
            bullets.append(f"- {brand}")

    return "\n".join(bullets)


def _build_recommendation_readiness_verdict_md(
    *,
    display_brand,
    display_category,
    display_market,
    display_audience,
    run_mode,
    deliverable_status,
    is_quick_test_mode,
    report_audience_context,
    target_mentions,
    target_avg_score,
    target_prompts_visible,
    target_sov,
    visibility_state,
    strategy_mode,
    reliability,
    query_intent_md,
):
    return (
        f"**Target Brand:** {display_brand}  \n"
        f"**Market:** {display_market}  \n"
        f"**Category:** {display_category}  \n"
        f"**Audience:** {display_audience}  \n"
        "**Report Type:** AI Recommendation Readiness Diagnosis  \n"
        f"**Run Mode:** {run_mode}  \n"
        f"**Deliverable Status:** {deliverable_status}  \n"
        f'{"**TEST VERSION ONLY - Quick Test Mode. Not Client Deliverable.**" if is_quick_test_mode else ""}\n\n'
        f"**Visibility State:** {visibility_state}  \n"
        f"**Strategy Mode:** {strategy_mode}  \n"
        "**Candidate-set status:** Not included in the tested recommendation candidate set  \n"
        "**First objective:** Candidate-set inclusion  \n"
        f"**Reliability Level:** {reliability['label']}  \n"
        f"**Reliability rationale:** {reliability['rationale']}  \n\n"
        f"In this benchmark, {display_brand} was not retrieved in the tested recommendation prompts, "
        f"based on the tested prompt set for {display_category} recommendations for {report_audience_context}. "
        f"The benchmark recorded {target_mentions} total mentions, {target_prompts_visible} prompts visible, "
        f"{target_avg_score} average visibility, and {target_sov}% share of voice.\n\n"
        "This result does not prove the model has no knowledge of the brand. It means the brand was not retrieved for the tested category, market, use-case, comparison, or decision-stage prompts.\n\n"
        "For a zero-visibility brand, the first measurable objective is candidate-set inclusion: getting the brand into relevant AI recommendation answers with accurate category and market context. Share-of-voice growth should come after the brand is first detected.\n\n"
        "### Query Intent Coverage\n\n"
        "This benchmark covers the following AI recommendation contexts:\n\n"
        f"{query_intent_md}"
    )


def _format_misaligned_context(misaligned_fields):
    if len(misaligned_fields) == 1:
        return f"{misaligned_fields[0]} context"
    if len(misaligned_fields) == 2:
        return f"{misaligned_fields[0]} and {misaligned_fields[1]} contexts"
    if misaligned_fields:
        return f"{', '.join(misaligned_fields[:-1])}, and {misaligned_fields[-1]} contexts"
    return ""


def _build_brand_understanding_summary_md(
    brand_understanding,
    display_brand,
    *,
    brand_understanding_done=False,
):
    if not brand_understanding_done or not brand_understanding:
        return (
            "The Brand Understanding Probe was not available for this report. "
            "The report cannot confidently separate entity understanding from recommendation retrieval failure, "
            "so the diagnosis should be treated as benchmark-based and requires validation."
        )

    brand_known_status = _get_probe_field(
        brand_understanding,
        "brand_known_status",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    category_alignment = _get_probe_field(
        brand_understanding,
        "category_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    market_alignment = _get_probe_field(
        brand_understanding,
        "market_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    audience_alignment = _get_probe_field(
        brand_understanding,
        "audience_alignment",
        STATUS_NOT_ENOUGH_EVIDENCE,
    )
    recommended_interpretation = _get_probe_field(
        brand_understanding,
        "recommended_interpretation",
        "Mixed diagnosis",
    )
    diagnosis_summary = _get_probe_field(
        brand_understanding,
        "diagnosis_summary",
        "",
    )
    validation_note = _get_probe_field(
        brand_understanding,
        "validation_note",
        "AI-inferred brand understanding probe. Validate before using as client-facing fact.",
    )
    misaligned_fields = [
        label
        for label, value in [
            ("category", category_alignment),
            ("market", market_alignment),
            ("audience", audience_alignment),
        ]
        if value == STATUS_MISALIGNED
    ]

    if misaligned_fields:
        interpretation = (
            "AI-inferred alignment signals suggest the non-visibility may reflect "
            f"an alignment problem in {_format_misaligned_context(misaligned_fields)}, "
            "not only a lack of evidence. This requires validation before being treated as fact."
        )
    elif brand_known_status in {STATUS_CLEAR, STATUS_PARTIAL}:
        interpretation = (
            f"The AI-inferred Brand Understanding Probe suggests {display_brand} appears to be recognized at least partially. "
            "Because the benchmark still recorded zero recommendation visibility, the issue appears more likely "
            "to involve recommendation retrieval, evidence depth, or market relevance than basic brand recognition. "
            "This requires validation."
        )
    elif brand_known_status in {STATUS_UNCLEAR, STATUS_NOT_ENOUGH_EVIDENCE}:
        interpretation = (
            "The AI-inferred Brand Understanding Probe did not provide enough confidence that the model understands the brand as a clear entity. "
            "Treat the zero-visibility result as a possible entity understanding gap until validated."
        )
    else:
        interpretation = (
            "The AI-inferred Brand Understanding Probe is inconclusive. Treat the visibility diagnosis as provisional and validate before acting on it."
        )

    probe_bullets = _format_key_value_bullets([
        ("Brand understanding", brand_known_status),
        ("Category alignment", category_alignment),
        ("Market alignment", market_alignment),
        ("Audience alignment", audience_alignment),
        ("Recommended interpretation", recommended_interpretation),
    ])
    body = f"{interpretation}\n\n{probe_bullets}"

    if diagnosis_summary:
        body += f"\n\n**Probe summary:** {diagnosis_summary}"

    body += f"\n\n_{validation_note}_"

    return body


def _build_market_relevance_summary_md(
    market_relevance,
    *,
    market_relevance_done=False,
):
    if not market_relevance_done or not market_relevance:
        return (
            "The Market Relevance Probe was not available, so retrieval-role explanations are benchmark-based only."
        )

    market_lock_status = _get_probe_field(
        market_relevance,
        "market_lock_status",
        MARKET_LOCK_INSUFFICIENT_EVIDENCE,
    )
    local_brand_presence_signal = _get_probe_field(
        market_relevance,
        "local_brand_presence_signal",
        "Not Enough Evidence",
    )
    recommended_interpretation = _get_probe_field(
        market_relevance,
        "recommended_interpretation",
        "Insufficient evidence",
    )
    global_default_risk_reason = _get_probe_field(
        market_relevance,
        "global_default_risk_reason",
        "",
    )
    market_evidence_gap_summary = _get_probe_field(
        market_relevance,
        "market_evidence_gap_summary",
        "",
    )
    validation_note = _get_probe_field(
        market_relevance,
        "validation_note",
        "AI-inferred market relevance probe. Validate before using as client-facing fact.",
    )
    visible_market_fit = _get_probe_field(market_relevance, "visible_market_fit", [])

    if market_lock_status == MARKET_LOCK_GLOBAL_DEFAULT_RISK:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests the answer set appears to lean toward globally visible category anchors. "
            "This may indicate a market evidence gap, but it requires validation and is not a verified market fact."
        )
    elif market_lock_status == MARKET_LOCK_MARKET_SPECIFIC:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests visible brands appear to have market relevance. "
            "In this case, non-visibility is less likely to be only a global-default artifact, but this requires validation."
        )
    elif market_lock_status == MARKET_LOCK_PARTIALLY_MARKET_SPECIFIC:
        interpretation = (
            "The AI-inferred Market Relevance Probe suggests the answer set shows mixed market adherence. "
            "Some retrieved brands may fit the target market while others may reflect broader category visibility."
        )
    else:
        interpretation = (
            "The AI-inferred Market Relevance Probe cannot determine market lock confidently from the benchmark context. "
            "Treat this as insufficient evidence, not verified market fact."
        )

    probe_bullets = _format_key_value_bullets([
        ("Market lock status", market_lock_status),
        ("Local brand presence", local_brand_presence_signal),
        ("Recommended interpretation", recommended_interpretation),
    ])
    body = f"{interpretation}\n\n{probe_bullets}"

    fit_bullets = _build_visible_market_fit_bullets(visible_market_fit)
    if fit_bullets:
        body += f"\n\nVisible brand market-fit signals:\n\n{fit_bullets}"

    if global_default_risk_reason:
        body += f"\n\n**Global-default risk reason:** {global_default_risk_reason}"
    if market_evidence_gap_summary:
        body += f"\n\n**Market evidence gap summary:** {market_evidence_gap_summary}"

    body += f"\n\n_{validation_note}_"

    return body


def _build_who_ai_retrieved_instead_md(retrieved_brand_profiles):
    if not retrieved_brand_profiles:
        return (
            "The benchmark did not provide a meaningful retrieved-brand reference set. "
            "This limits the ability to compare the target against visible alternatives."
        )

    cards = [
        (
            f"**{profile['brand']}**\n"
            f"- Observed benchmark signal: {profile['observed_signal']}\n"
            f"- Competitor tier: {profile['competitor_tier']}\n"
            f"- Retrieval role preview: {profile['retrieval_role']}"
        )
        for profile in retrieved_brand_profiles
    ]

    cards_md = "\n\n".join(cards)
    return (
        "The benchmark retrieved the following visible reference brands instead of the target in the tested recommendation contexts. "
        "These should be read as retrieved brands, visible reference brands, or category anchors rather than direct competitors to attack.\n\n"
        f"{cards_md}"
    )


def _build_retrieval_roles_md(
    retrieved_brand_profiles,
    *,
    market_relevance_summary_md,
):
    if not retrieved_brand_profiles:
        return (
            f"{market_relevance_summary_md}\n\n"
            "No retrieved-brand role cards are available because the benchmark did not produce a meaningful visible reference set."
        )

    cards = []
    for profile in retrieved_brand_profiles:
        card_lines = [
            f"**{profile['brand']}**",
            f"- Benchmark-based retrieval role: {profile['retrieval_role']}",
        ]
        if profile.get("secondary_retrieval_signals"):
            card_lines.append(
                "- Secondary signals: "
                + ", ".join(profile["secondary_retrieval_signals"])
            )
        if (
            profile.get("market_fit_modifier")
            and profile.get("retrieval_role") != "Local market provider"
        ):
            card_lines.append(
                f"- Market note: {profile['market_fit_modifier']}"
            )
        if profile.get("role_basis"):
            card_lines.append(
                f"- Role basis: {profile['role_basis']}"
            )
        card_lines.extend([
            f"- Why it may have been retrieved: {profile['inferred_reason']}",
            f"- What this implies for the target: {profile['evidence_implication']}",
        ])
        cards.append("\n".join(card_lines))

    cards_md = "\n\n".join(cards)
    return (
        f"{market_relevance_summary_md}\n\n"
        "The role labels below are benchmark-based retrieval hypotheses. They require validation and are not source-grounded facts.\n\n"
        f"{cards_md}"
    )


def _build_target_vs_retrieved_gap_md(retrieved_brand_profiles):
    caveat = (
        "This is benchmark-based inference, not verified competitive intelligence unless source-grounded research exists."
    )

    if not retrieved_brand_profiles:
        return (
            f"{caveat}\n\n"
            "No target-vs-retrieved brand gap can be diagnosed because the benchmark did not produce a meaningful retrieved-brand reference set."
        )

    cards = [
        (
            f"**{profile['brand']}**\n"
            f"- Observed benchmark signal: {profile['observed_signal']}\n"
            f"- Inferred retrieval role: {profile['retrieval_role']}\n"
            f"- Inferred target gap: {profile['inferred_target_gap']}\n"
            f"- Evidence asset implication: {profile['evidence_implication']}\n"
            f"- Required validation: {profile['required_validation']}"
        )
        for profile in retrieved_brand_profiles
    ]

    cards_md = "\n\n".join(cards)
    return f"{caveat}\n\n{cards_md}"


def _build_first_three_evidence_assets_md(evidence_assets):
    if not evidence_assets:
        return (
            "No prioritized evidence assets could be generated from the available benchmark context. "
            "Rerun the benchmark with a clean competitor set and broader prompt coverage."
        )

    cards = [
        (
            f"**Priority {asset['priority']} - {asset['asset_name']}**\n"
            f"- What to build: {asset['what_to_build']}\n"
            f"- Why it matters: {asset['why_it_matters']}\n"
            f"- Target retrieval driver: {asset['target_retrieval_driver']}\n"
            f"- Targets / prompt groups: {asset['targets_or_prompt_groups']}\n"
            f"- Validation: {asset['validation']}"
        )
        for asset in evidence_assets
    ]

    cards_md = "\n\n".join(cards)
    return (
        "The main report should focus on the first three evidence assets most likely to clarify recommendation readiness. "
        "These assets are intended to test whether clearer retrievable evidence improves candidate-set inclusion; they are not a promise of AI mentions or a fixed timeline.\n\n"
        f"{cards_md}"
    )


def _build_methodology_and_reliability_notes_md(
    *,
    display_category,
    prompt_categories,
    reliability,
    source_grounded_evidence_available=False,
):
    source_evidence_note = (
        "included as optional validation context in this Markdown report; source evidence can support gap validation, "
        "but it does not prove retrieval causality."
        if source_grounded_evidence_available
        else "not included in this Markdown report; current retrieval-role and gap explanations are not verified market fact."
    )

    return (
        f"**Reliability Level:** {reliability['label']}  \n"
        f"**Reliability rationale:** {reliability['rationale']}\n\n"
        "Evidence hierarchy used in this report:\n\n"
        "- Observed benchmark signal: measured mentions, prompt visibility, share of voice, and retrieved brands in this run.\n"
        "- Inferred retrieval driver: cautious explanation of why a visible brand may have been retrieved, based on benchmark patterns.\n"
        f"- Source-grounded evidence: {source_evidence_note}\n"
        "- Recommended action: evidence assets intended to test whether the target can enter the recommendation candidate set in future benchmarks.\n\n"
        f"{_build_methodology_notes_md(display_category, prompt_categories)}"
    )


def _build_zero_visibility_markdown_report(
    *,
    display_brand,
    display_category,
    display_market,
    display_audience,
    run_mode,
    deliverable_status,
    is_quick_test_mode,
    prompt_categories,
    report_audience_context,
    target_mentions,
    target_avg_score,
    target_prompts_visible,
    target_sov,
    visibility_state,
    strategy_mode,
    summary_report_md,
    trigger_report_md,
    top_brands_report_md,
    summary_df,
    top_brands_df,
    detailed_pivot_df,
    brand,
    brand_understanding=None,
    brand_understanding_done=False,
    market_relevance=None,
    market_relevance_done=False,
    source_evidence_payload=None,
):
    query_intent_md = "\n".join(
        f"- {item}" for item in prompt_categories
    ) or "_No query intent categories available._"
    reference_brands = build_visible_reference_brands(summary_df, brand)
    retrieved_brand_profiles = build_retrieved_brand_profiles(
        summary_df,
        brand,
        top_brands_df=top_brands_df,
        detailed_pivot_df=detailed_pivot_df,
        market_relevance=market_relevance if market_relevance_done else None,
    )
    reliability = classify_benchmark_reliability(
        run_mode=run_mode,
        prompt_categories=prompt_categories,
        reference_brands=reference_brands,
        source_grounded_evidence_available=bool(source_evidence_payload),
    )
    market_relevance_interpretation = build_market_relevance_interpretation(
        display_brand,
        display_market,
        display_category,
        reference_brands,
    )
    evidence_gap_md = _build_evidence_gap_cards_md(
        build_evidence_gap_map(
            display_brand,
            display_category,
            display_market,
            display_audience,
        )
    )
    evidence_assets = build_first_three_evidence_assets(
        brand=display_brand,
        category=display_category,
        market=display_market,
        audience=display_audience,
        reference_brands=reference_brands,
        retrieved_brand_profiles=retrieved_brand_profiles,
        brand_understanding=(
            brand_understanding if brand_understanding_done else None
        ),
        market_relevance=(market_relevance if market_relevance_done else None),
        prompt_categories=prompt_categories,
    )
    validation_plan_md = df_to_markdown_table(
        pd.DataFrame(build_validation_plan(prompt_categories)),
        max_rows=10,
    )
    market_relevance_summary_md = (
        f"{market_relevance_interpretation}\n\n"
        f"{_build_market_relevance_summary_md(market_relevance, market_relevance_done=market_relevance_done)}"
    )
    verdict_md = _build_recommendation_readiness_verdict_md(
        display_brand=display_brand,
        display_category=display_category,
        display_market=display_market,
        display_audience=display_audience,
        run_mode=run_mode,
        deliverable_status=deliverable_status,
        is_quick_test_mode=is_quick_test_mode,
        report_audience_context=report_audience_context,
        target_mentions=target_mentions,
        target_avg_score=target_avg_score,
        target_prompts_visible=target_prompts_visible,
        target_sov=target_sov,
        visibility_state=visibility_state,
        strategy_mode=strategy_mode,
        reliability=reliability,
        query_intent_md=query_intent_md,
    )
    brand_understanding_summary_md = _build_brand_understanding_summary_md(
        brand_understanding,
        display_brand,
        brand_understanding_done=brand_understanding_done,
    )
    who_retrieved_md = _build_who_ai_retrieved_instead_md(
        retrieved_brand_profiles
    )
    retrieval_roles_md = _build_retrieval_roles_md(
        retrieved_brand_profiles,
        market_relevance_summary_md=market_relevance_summary_md,
    )
    target_gap_md = _build_target_vs_retrieved_gap_md(retrieved_brand_profiles)
    first_three_assets_md = _build_first_three_evidence_assets_md(evidence_assets)
    methodology_reliability_md = _build_methodology_and_reliability_notes_md(
        display_category=display_category,
        prompt_categories=prompt_categories,
        reliability=reliability,
        source_grounded_evidence_available=bool(source_evidence_payload),
    )
    source_evidence_summary_md = (
        render_source_evidence_summary_section(source_evidence_payload)
        if source_evidence_payload
        else ""
    )

    parts = [
        f"# {display_brand} {display_market} AI Recommendation Readiness Diagnosis",
        (
            "## 1. Recommendation Readiness Verdict\n\n"
            f"{verdict_md}"
        ),
        (
            "## 2. Brand Understanding Summary\n\n"
            f"{brand_understanding_summary_md}"
        ),
        (
            "## 3. Who AI Retrieved Instead\n\n"
            f"{who_retrieved_md}"
        ),
        (
            "## 4. Why Those Brands Were Retrieved\n\n"
            f"{retrieval_roles_md}"
        ),
        (
            "## 5. Target vs Retrieved Brand Gap\n\n"
            f"{target_gap_md}"
        ),
        (
            "## 6. First 3 Evidence Assets to Build\n\n"
            f"{first_three_assets_md}"
        ),
        (
            "## 7. Validation Plan\n\n"
            "The next benchmark should validate whether evidence is becoming retrievable. The first milestone is first measurable inclusion, not immediate share-of-voice growth.\n\n"
            f"{validation_plan_md}"
        ),
        (
            "## 8. Supporting Benchmark Data\n\n"
            "These details support the recommendation-readiness diagnosis. They should be used as audit evidence rather than the main executive narrative.\n\n"
            "### Evidence Gap Map\n\n"
            f"{evidence_gap_md}\n\n"
            "### Competitive Benchmark\n\n"
            "Measured brand-level AI visibility across all tested prompts:\n\n"
            f"{summary_report_md}\n\n"
            "### Trigger-Level Visibility Findings\n\n"
            "Measured visibility by tracked brand across AI query categories:\n\n"
            f"{trigger_report_md}\n\n"
            "### Top Brand Winners by Query Type\n\n"
            "Strongest measured brand signal in each query category:\n\n"
            f"{top_brands_report_md}"
        ),
        (
            "## 9. Methodology / Reliability Notes\n\n"
            f"{methodology_reliability_md}"
        ),
    ]
    if source_evidence_summary_md:
        parts.append(source_evidence_summary_md)

    return parts
