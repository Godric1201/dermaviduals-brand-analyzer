from dataclasses import dataclass

import pandas as pd


VISIBILITY_NOT_DETECTED = "Not Detected"
VISIBILITY_WEAKLY_DETECTED = "Weakly Detected"
VISIBILITY_PARTIALLY_VISIBLE = "Partially Visible"
VISIBILITY_COMPETITIVELY_VISIBLE = "Competitively Visible"
VISIBILITY_CATEGORY_ANCHOR = "Category Anchor"

FIRST_DETECTION_STRATEGY = "First Detection Strategy"
ASSOCIATION_GROWTH_STRATEGY = "Association Growth Strategy"
CATEGORY_OWNERSHIP_STRATEGY = "Category Ownership Strategy"

RELIABILITY_STRONG = "Strong"
RELIABILITY_DIRECTIONAL = "Directional"
RELIABILITY_EXPLORATORY = "Exploratory"
RELIABILITY_INSUFFICIENT = "Insufficient evidence"

COMPETITOR_TIER_PEER = "Peer competitor"
COMPETITOR_TIER_ASPIRATIONAL = "Aspirational competitor"
COMPETITOR_TIER_CATEGORY_ANCHOR = "Category anchor"
COMPETITOR_TIER_UNCLEAR = "Unclear / needs validation"

RETRIEVAL_ROLE_PLANNING = "Planning / consulting authority"
RETRIEVAL_ROLE_TECHNICAL = "Technical infrastructure provider"
RETRIEVAL_ROLE_LOCAL = "Local market provider"
RETRIEVAL_ROLE_TRUST = "Trust / premium reference"
RETRIEVAL_ROLE_BUDGET = "Budget / practical option"
RETRIEVAL_ROLE_NICHE = "Niche specialist"
RETRIEVAL_ROLE_COMPARISON = "Comparison anchor"
RETRIEVAL_ROLE_UNCLEAR = "Unclear retrieved reference"

EVIDENCE_TAXONOMY = (
    "Entity Evidence",
    "Market Evidence",
    "Offering Evidence",
    "Trust Evidence",
    "Third-Party Evidence",
    "Comparison Evidence",
    "Structured Evidence",
    "Community Evidence",
)


@dataclass(frozen=True)
class VisibilityMetrics:
    total_mentions: int
    average_visibility_score: float
    prompts_visible: int
    share_of_voice_percent: float


def _coerce_number(value, default=0):
    try:
        numeric_value = pd.to_numeric(value, errors="coerce")
    except Exception:
        return default

    if pd.isna(numeric_value):
        return default

    return numeric_value.item() if hasattr(numeric_value, "item") else numeric_value


def _get_field(value, field, default=""):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)


def _normalize_text(value):
    return " ".join(str(value or "").strip().split())


def _normalize_label_text(value):
    return _normalize_text(value).lower()


def _contains_any(text, terms):
    normalized_text = _normalize_label_text(text)
    return any(term in normalized_text for term in terms)


def _visible_market_fit_for_brand(market_relevance, brand):
    visible_market_fit = _get_field(market_relevance, "visible_market_fit", [])
    if not isinstance(visible_market_fit, list):
        return {}

    target = _normalize_label_text(brand)
    for row in visible_market_fit:
        if not isinstance(row, dict):
            continue
        if _normalize_label_text(row.get("brand")) == target:
            return row

    return {}


def _prompt_categories_for_brand(top_brands_df, brand):
    if top_brands_df is None or getattr(top_brands_df, "empty", True):
        return []
    if "brand" not in top_brands_df.columns or "prompt_category" not in top_brands_df.columns:
        return []

    target = _normalize_label_text(brand)
    matching_rows = top_brands_df[
        top_brands_df["brand"].astype(str).str.lower() == target
    ]

    return [
        str(item).strip()
        for item in matching_rows["prompt_category"].dropna().tolist()
        if str(item).strip()
    ]


def _metrics_from_reference_brand(reference_brand):
    return VisibilityMetrics(
        total_mentions=int(_coerce_number(reference_brand.get("Mentions", 0))),
        average_visibility_score=float(
            _coerce_number(reference_brand.get("Average Visibility Score", 0))
        ),
        prompts_visible=int(_coerce_number(reference_brand.get("Prompts Visible", 0))),
        share_of_voice_percent=float(
            _coerce_number(reference_brand.get("Share of Voice %", 0))
        ),
    )


def get_target_visibility_metrics(summary_df, brand):
    if summary_df is None or summary_df.empty or "brand" not in summary_df.columns:
        return VisibilityMetrics(0, 0, 0, 0)

    target_row = summary_df[
        summary_df["brand"].astype(str).str.lower() == str(brand).lower()
    ]

    if target_row.empty:
        return VisibilityMetrics(0, 0, 0, 0)

    row = target_row.iloc[0]

    return VisibilityMetrics(
        total_mentions=int(_coerce_number(row.get("total_mentions", 0))),
        average_visibility_score=float(_coerce_number(row.get("average_visibility_score", 0))),
        prompts_visible=int(_coerce_number(row.get("prompts_visible", 0))),
        share_of_voice_percent=float(_coerce_number(row.get("share_of_voice_percent", 0))),
    )


def is_zero_visibility(metrics):
    return (
        metrics.total_mentions == 0
        and metrics.average_visibility_score == 0
        and metrics.prompts_visible == 0
        and metrics.share_of_voice_percent == 0
    )


def classify_visibility_state(metrics):
    if is_zero_visibility(metrics):
        return VISIBILITY_NOT_DETECTED

    if (
        metrics.total_mentions >= 20
        or metrics.prompts_visible >= 8
        or metrics.share_of_voice_percent >= 25
        or metrics.average_visibility_score >= 65
    ):
        return VISIBILITY_CATEGORY_ANCHOR

    if (
        metrics.total_mentions >= 8
        or metrics.prompts_visible >= 4
        or metrics.share_of_voice_percent >= 10
        or metrics.average_visibility_score >= 45
    ):
        return VISIBILITY_COMPETITIVELY_VISIBLE

    if (
        metrics.total_mentions >= 3
        or metrics.prompts_visible >= 2
        or metrics.share_of_voice_percent >= 3
        or metrics.average_visibility_score >= 20
    ):
        return VISIBILITY_PARTIALLY_VISIBLE

    return VISIBILITY_WEAKLY_DETECTED


def select_strategy_mode(metrics):
    visibility_state = classify_visibility_state(metrics)

    if visibility_state == VISIBILITY_NOT_DETECTED:
        return FIRST_DETECTION_STRATEGY

    if visibility_state in {
        VISIBILITY_COMPETITIVELY_VISIBLE,
        VISIBILITY_CATEGORY_ANCHOR,
    }:
        return CATEGORY_OWNERSHIP_STRATEGY

    return ASSOCIATION_GROWTH_STRATEGY


def build_visible_reference_brands(summary_df, brand, limit=5):
    if summary_df is None or summary_df.empty or "brand" not in summary_df.columns:
        return []

    competitors = summary_df[
        summary_df["brand"].astype(str).str.lower() != str(brand).lower()
    ].copy()

    if competitors.empty:
        return []

    for column in [
        "total_mentions",
        "average_visibility_score",
        "prompts_visible",
        "share_of_voice_percent",
    ]:
        if column not in competitors.columns:
            competitors[column] = 0
        competitors[column] = pd.to_numeric(competitors[column], errors="coerce").fillna(0)

    visible = competitors[
        (competitors["total_mentions"] > 0)
        | (competitors["average_visibility_score"] > 0)
        | (competitors["prompts_visible"] > 0)
        | (competitors["share_of_voice_percent"] > 0)
    ].copy()

    if visible.empty:
        return []

    visible = visible.sort_values(
        by=["average_visibility_score", "total_mentions", "share_of_voice_percent"],
        ascending=False,
    ).head(limit)

    reference_brands = []
    for _, row in visible.iterrows():
        metrics = VisibilityMetrics(
            total_mentions=int(row.get("total_mentions", 0)),
            average_visibility_score=float(row.get("average_visibility_score", 0)),
            prompts_visible=int(row.get("prompts_visible", 0)),
            share_of_voice_percent=float(row.get("share_of_voice_percent", 0)),
        )
        state = classify_visibility_state(metrics)
        role = (
            "Visible category anchor"
            if state in {VISIBILITY_CATEGORY_ANCHOR, VISIBILITY_COMPETITIVELY_VISIBLE}
            else "AI-visible reference brand"
        )
        reference_brands.append({
            "Brand": row.get("brand", ""),
            "Reference Role": role,
            "Mentions": metrics.total_mentions,
            "Average Visibility Score": metrics.average_visibility_score,
            "Prompts Visible": metrics.prompts_visible,
            "Share of Voice %": metrics.share_of_voice_percent,
            "Interpretation": (
                "Retrieved alternative with measurable benchmark signal; use as evidence context, not as a brand to attack."
            ),
        })

    return reference_brands


def format_reference_brand_names(reference_brands, limit=3):
    names = [
        str(item.get("Brand", "")).strip()
        for item in (reference_brands or [])[:limit]
        if str(item.get("Brand", "")).strip()
    ]

    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"

    return f"{', '.join(names[:-1])}, and {names[-1]}"


def build_market_relevance_interpretation(brand, market, category, reference_brands):
    if reference_brands:
        names = format_reference_brand_names(reference_brands)
        return (
            f"The benchmark retrieved AI-visible reference brands such as {names}, while {brand} was not detected. "
            f"These visible category anchors may indicate that the model defaults to established {category} leaders "
            f"when market-specific evidence for {market} is not strong enough to place a regional or challenger brand "
            "in the recommendation candidate set. This is an interpretation risk, not a confirmed fact without "
            "dedicated market-relevance probes."
        )

    return (
        f"No tracked alternative generated measurable visibility, so this run cannot diagnose whether {category} "
        f"answers are defaulting away from {market}. The next useful check is still whether {brand} can earn first "
        "measurable inclusion in relevant category, market, and use-case prompts."
    )


def classify_benchmark_reliability(
    *,
    run_mode,
    prompt_categories=None,
    reference_brands=None,
    source_grounded_evidence_available=False,
):
    reference_brands = reference_brands or []
    prompt_count = len([
        item for item in prompt_categories or []
        if str(item).strip()
    ])
    is_quick_test = str(run_mode or "").strip().lower() == "quick test mode"

    if not reference_brands:
        return {
            "label": RELIABILITY_INSUFFICIENT,
            "rationale": (
                "The benchmark did not provide a meaningful retrieved-brand reference set, "
                "so recommendation-readiness interpretation is limited."
            ),
        }

    if (
        source_grounded_evidence_available
        and len(reference_brands) >= 2
        and prompt_count >= 3
        and not is_quick_test
    ):
        return {
            "label": RELIABILITY_STRONG,
            "rationale": (
                "The benchmark has multiple visible retrieved brands and source-grounded evidence support."
            ),
        }

    if is_quick_test or prompt_count == 1 or len(reference_brands) == 1:
        return {
            "label": RELIABILITY_EXPLORATORY,
            "rationale": (
                "The benchmark has useful early signal, but prompt coverage or retrieved-brand context is limited."
            ),
        }

    return {
        "label": RELIABILITY_DIRECTIONAL,
        "rationale": (
            "The benchmark has visible retrieved brands and enough context for directional diagnosis, "
            "but no source-grounded research is available in this report."
        ),
    }


def classify_retrieved_brand_tier(
    metrics,
    *,
    market_fit=None,
    source_grounded_peer=False,
):
    if source_grounded_peer:
        return COMPETITOR_TIER_PEER

    visibility_state = classify_visibility_state(metrics)

    if visibility_state == VISIBILITY_CATEGORY_ANCHOR:
        return COMPETITOR_TIER_CATEGORY_ANCHOR

    if (
        str(market_fit or "").strip() == "Market-relevant"
        and metrics.prompts_visible >= 2
        and metrics.average_visibility_score >= 20
    ):
        return COMPETITOR_TIER_PEER

    if visibility_state == VISIBILITY_COMPETITIVELY_VISIBLE:
        return COMPETITOR_TIER_ASPIRATIONAL

    return COMPETITOR_TIER_UNCLEAR


def classify_retrieval_role(
    *,
    prompt_categories=None,
    visible_market_fit=None,
    metrics=None,
):
    prompt_text = " ".join(
        str(item)
        for item in prompt_categories or []
        if str(item).strip()
    )
    market_fit = str(visible_market_fit or "").strip()

    if market_fit == "Market-relevant":
        return RETRIEVAL_ROLE_LOCAL

    if _contains_any(prompt_text, [
        "compare",
        "comparison",
        "alternative",
        "alternatives",
        "shortlist",
        "versus",
        " vs ",
    ]):
        return RETRIEVAL_ROLE_COMPARISON

    if _contains_any(prompt_text, [
        "local",
        "regional",
        "market",
        "near",
        "geography",
        "location",
    ]):
        return RETRIEVAL_ROLE_LOCAL

    if _contains_any(prompt_text, [
        "technical",
        "infrastructure",
        "platform",
        "system",
        "systems",
        "facility",
        "facilities",
        "architecture",
        "operational",
        "data center",
        "datacenter",
        "cloud",
    ]):
        return RETRIEVAL_ROLE_TECHNICAL

    if _contains_any(prompt_text, [
        "planning",
        "consulting",
        "consultant",
        "advisory",
        "strategy",
        "strategic",
        "evaluate",
        "evaluation",
        "expert",
    ]):
        return RETRIEVAL_ROLE_PLANNING

    if _contains_any(prompt_text, [
        "budget",
        "affordable",
        "pricing",
        "cost",
        "practical",
        "easy",
        "small business",
    ]):
        return RETRIEVAL_ROLE_BUDGET

    if _contains_any(prompt_text, [
        "niche",
        "specialist",
        "specialized",
        "use case",
        "use-case",
        "audience",
        "segment",
        "industry-specific",
    ]):
        return RETRIEVAL_ROLE_NICHE

    if _contains_any(prompt_text, [
        "best",
        "top",
        "premium",
        "trusted",
        "trust",
        "enterprise",
        "reliable",
        "credible",
        "quality",
    ]):
        return RETRIEVAL_ROLE_TRUST

    if metrics and classify_visibility_state(metrics) == VISIBILITY_CATEGORY_ANCHOR:
        return RETRIEVAL_ROLE_TRUST

    if market_fit == "Global-default":
        return RETRIEVAL_ROLE_TRUST

    return RETRIEVAL_ROLE_UNCLEAR


def _inferred_reason_for_role(role):
    if role == RETRIEVAL_ROLE_COMPARISON:
        return (
            "Based on this benchmark, the brand appears to provide a familiar alternative "
            "or comparison reference in tested recommendation contexts."
        )
    if role == RETRIEVAL_ROLE_LOCAL:
        return (
            "Based on this benchmark, the brand appears to have market-qualified relevance "
            "in the tested answer set; this requires validation and is not verified market fact."
        )
    if role == RETRIEVAL_ROLE_TECHNICAL:
        return (
            "Based on this benchmark, the brand appears to be retrieved for technical capability "
            "or infrastructure-oriented contexts."
        )
    if role == RETRIEVAL_ROLE_PLANNING:
        return (
            "Based on this benchmark, the brand appears to be retrieved for planning, advisory, "
            "or evaluation-oriented contexts."
        )
    if role == RETRIEVAL_ROLE_TRUST:
        return (
            "Based on this benchmark, the brand appears to act as a trust or premium reference "
            "within the tested answer set."
        )
    if role == RETRIEVAL_ROLE_BUDGET:
        return (
            "Based on this benchmark, the brand appears to be retrieved for practical, pricing, "
            "or accessibility-oriented contexts."
        )
    if role == RETRIEVAL_ROLE_NICHE:
        return (
            "Based on this benchmark, the brand appears to be retrieved for a narrower use case, "
            "audience, or specialist context."
        )

    return (
        "Based on this benchmark, the reason this brand was retrieved is unclear and requires validation."
    )


def _evidence_implication_for_role(role):
    if role == RETRIEVAL_ROLE_COMPARISON:
        return "Build comparison and alternatives evidence that explains when the target is a relevant option."
    if role == RETRIEVAL_ROLE_LOCAL:
        return "Build market evidence that connects the target to the requested geography and buyer context."
    if role == RETRIEVAL_ROLE_TECHNICAL:
        return "Build offering and capability evidence that clarifies the target's technical or operational fit."
    if role == RETRIEVAL_ROLE_PLANNING:
        return "Build advisory, methodology, or decision-support evidence that makes the target eligible for planning prompts."
    if role == RETRIEVAL_ROLE_TRUST:
        return "Build trust evidence with substantiated proof points that can support shortlist and decision-stage prompts."
    if role == RETRIEVAL_ROLE_BUDGET:
        return "Build practical buyer guidance that clarifies fit, tradeoffs, and selection criteria."
    if role == RETRIEVAL_ROLE_NICHE:
        return "Build use-case and audience evidence that makes the target eligible for specialist prompts."

    return "Build entity, offering, and market evidence before drawing a stronger retrieval-role conclusion."


def _target_gap_for_role(role):
    if role == RETRIEVAL_ROLE_COMPARISON:
        return "The target may lack retrievable comparison evidence for alternative and shortlist prompts."
    if role == RETRIEVAL_ROLE_LOCAL:
        return "The target may lack retrievable market evidence for the requested geography."
    if role == RETRIEVAL_ROLE_TECHNICAL:
        return "The target may lack retrievable capability evidence for technical or operational prompts."
    if role == RETRIEVAL_ROLE_PLANNING:
        return "The target may lack retrievable decision-support evidence for planning or evaluation prompts."
    if role == RETRIEVAL_ROLE_TRUST:
        return "The target may lack retrievable trust evidence for shortlist and decision-stage prompts."
    if role == RETRIEVAL_ROLE_BUDGET:
        return "The target may lack retrievable practical-selection evidence for value or fit prompts."
    if role == RETRIEVAL_ROLE_NICHE:
        return "The target may lack retrievable use-case evidence for audience-specific prompts."

    return "The target needs clearer entity, offering, market, and comparison evidence before the gap can be diagnosed more specifically."


def build_retrieved_brand_profiles(
    summary_df,
    brand,
    *,
    top_brands_df=None,
    market_relevance=None,
    limit=5,
):
    reference_brands = build_visible_reference_brands(summary_df, brand, limit=limit)
    profiles = []

    for reference_brand in reference_brands:
        brand_name = str(reference_brand.get("Brand", "")).strip()
        if not brand_name:
            continue

        metrics = _metrics_from_reference_brand(reference_brand)
        brand_prompt_categories = _prompt_categories_for_brand(top_brands_df, brand_name)
        fit_row = _visible_market_fit_for_brand(market_relevance, brand_name)
        market_fit = fit_row.get("market_fit")
        retrieval_role = classify_retrieval_role(
            prompt_categories=brand_prompt_categories,
            visible_market_fit=market_fit,
            metrics=metrics,
        )
        competitor_tier = classify_retrieved_brand_tier(
            metrics,
            market_fit=market_fit,
        )
        observed_signal = (
            f"{brand_name} generated {metrics.total_mentions} mentions, appeared in "
            f"{metrics.prompts_visible} prompts, and recorded {metrics.share_of_voice_percent}% "
            "share of voice in this benchmark."
        )

        profiles.append({
            "brand": brand_name,
            "observed_signal": observed_signal,
            "competitor_tier": competitor_tier,
            "retrieval_role": retrieval_role,
            "inferred_reason": _inferred_reason_for_role(retrieval_role),
            "inferred_target_gap": _target_gap_for_role(retrieval_role),
            "evidence_implication": _evidence_implication_for_role(retrieval_role),
            "required_validation": (
                "This requires validation with source-grounded research and a comparable future benchmark before treating it as competitive fact."
            ),
            "prompt_categories": brand_prompt_categories,
            "market_fit": market_fit or "",
            "market_fit_rationale": fit_row.get("rationale", ""),
        })

    return profiles


def build_evidence_gap_map(brand, category, market, audience):
    return [
        {
            "Evidence Type": "Entity Evidence",
            "Current Diagnosis": f"{brand} was not retrieved as a recognizable {category} entity in this benchmark.",
            "Gap Addressed": "Basic entity-category association",
            "Why It Matters": "AI systems need clear, repeated signals about who the brand is and what category it belongs to before it can be considered for recommendation prompts.",
            "Validation Method": "Re-run category and use-case prompts and check for first target-brand mention with the correct category context.",
        },
        {
            "Evidence Type": "Market Evidence",
            "Current Diagnosis": f"The report cannot confirm that {brand} is strongly associated with {market} recommendation contexts.",
            "Gap Addressed": "Market relevance and local retrieval",
            "Why It Matters": "Regional brands often need market-specific proof to compete with globally visible reference brands in AI answers.",
            "Validation Method": f"Re-run prompts explicitly qualified for {market} and check whether the brand appears in market-qualified answers.",
        },
        {
            "Evidence Type": "Offering Evidence",
            "Current Diagnosis": f"The tested answers did not connect {brand} to concrete offerings, use cases, or buyer needs for {audience}.",
            "Gap Addressed": "Offering and use-case clarity",
            "Why It Matters": "Recommendation prompts retrieve brands that appear eligible for a specific need, product, service, or decision context.",
            "Validation Method": "Re-run use-case and audience-specific prompts and look for accurate offering descriptions.",
        },
        {
            "Evidence Type": "Trust Evidence",
            "Current Diagnosis": "No trust signal for the target brand was measurable in generated answers.",
            "Gap Addressed": "Recommendation confidence",
            "Why It Matters": "Trust evidence helps a brand become eligible for shortlist, comparison, and decision-stage answers.",
            "Validation Method": "Re-run trust and decision-stage prompts and check whether cited proof points appear with the brand.",
        },
        {
            "Evidence Type": "Third-Party Evidence",
            "Current Diagnosis": "No external source footprint was visible in the benchmark output.",
            "Gap Addressed": "Independent corroboration",
            "Why It Matters": "Third-party references can help models corroborate that the brand is real, relevant, and category-associated.",
            "Validation Method": "Re-run prompts after third-party evidence is published and check for first inclusion or stronger association language.",
        },
        {
            "Evidence Type": "Comparison Evidence",
            "Current Diagnosis": f"{brand} was not retrieved as a comparison-eligible alternative.",
            "Gap Addressed": "Fair comparison eligibility",
            "Why It Matters": "AI recommendation answers often rely on explicit comparison evidence when selecting alternatives.",
            "Validation Method": "Re-run comparison and alternative prompts and check whether the brand appears beside relevant retrieved alternatives.",
        },
        {
            "Evidence Type": "Structured Evidence",
            "Current Diagnosis": "The benchmark cannot verify whether brand, organization, and offering data are consistently structured.",
            "Gap Addressed": "Machine-readable entity clarity",
            "Why It Matters": "Clear structure, schema, sameAs links, and consistent naming reduce ambiguity around the brand entity.",
            "Validation Method": "Audit structured data first, then re-run entity and category prompts for first measurable inclusion.",
        },
        {
            "Evidence Type": "Community Evidence",
            "Current Diagnosis": "No community or user-generated proof was visible in benchmark answers.",
            "Gap Addressed": "Real-world usage signal",
            "Why It Matters": "Community references can support relevance for local, niche, or audience-specific prompts.",
            "Validation Method": "Re-run audience and local-intent prompts and check whether community proof contributes to retrieval.",
        },
    ]


def build_first_detection_task_roadmap(brand, category, market, audience, reference_brands=None):
    reference_name = (
        str(reference_brands[0]["Brand"])
        if reference_brands
        else "retrieved alternatives"
    )

    return [
        {
            "Action": f"Create or update a canonical {brand} entity page for {category}.",
            "Gap Addressed": "The brand is not yet retrieved as a category entity.",
            "Evidence Type": "Entity Evidence",
            "Why It Matters": "First detection requires the model to connect the brand name with a clear category and role.",
            "Where Evidence Should Live": "About page, product/service overview, organization profile, and structured data.",
            "Benchmark Validation Method": "Re-run category prompts and check for first target-brand mention with correct category wording.",
            "Expected Influence": "First measurable inclusion and clearer entity-category association.",
        },
        {
            "Action": f"Publish a {market} relevance page explaining where and for whom {brand} operates.",
            "Gap Addressed": "Market-specific relevance is not visible enough for recommendation retrieval.",
            "Evidence Type": "Market Evidence",
            "Why It Matters": "A regional or challenger brand needs market proof when AI answers default to broader category anchors.",
            "Where Evidence Should Live": "Market landing page, local service pages, location pages, partner pages, or regional proof page.",
            "Benchmark Validation Method": f"Re-run prompts explicitly qualified for {market} and check whether the brand enters market-specific answers.",
            "Expected Influence": "Market association and first detection in local or regional prompts.",
        },
        {
            "Action": f"Document the concrete {category} offerings and use cases {brand} should be eligible for.",
            "Gap Addressed": "The benchmark did not connect the brand to concrete offerings or buyer needs.",
            "Evidence Type": "Offering Evidence",
            "Why It Matters": "AI recommendation answers need a reason to include the brand for a specific need, audience, or use case.",
            "Where Evidence Should Live": "Product/service pages, use-case pages, audience pages, FAQs, and solution pages.",
            "Benchmark Validation Method": f"Re-run use-case and audience-specific prompts for {audience} and check for accurate offering retrieval.",
            "Expected Influence": "Use-case association and comparison eligibility.",
        },
        {
            "Action": "Add substantiated trust proof tied to the claims the brand wants AI systems to retrieve.",
            "Gap Addressed": "No measurable trust signal appeared for the target brand.",
            "Evidence Type": "Trust Evidence",
            "Why It Matters": "Recommendation answers favor brands with verifiable proof for quality, fit, credibility, or reliability.",
            "Where Evidence Should Live": "Testimonials, case studies, certifications, awards, ratings, expert validation, or proof pages.",
            "Benchmark Validation Method": "Re-run trust and decision-stage prompts and check whether proof points appear with the brand.",
            "Expected Influence": "Trust signal retrieval and shortlist eligibility.",
        },
        {
            "Action": f"Build fair comparison evidence against {reference_name} and other retrieved alternatives.",
            "Gap Addressed": "The brand is not yet comparison-eligible in AI answers.",
            "Evidence Type": "Comparison Evidence",
            "Why It Matters": "Comparison evidence helps AI answers understand when the brand is a relevant alternative rather than an unrelated entity.",
            "Where Evidence Should Live": "Comparison pages, alternatives pages, buyer guides, and category selection criteria pages.",
            "Benchmark Validation Method": "Re-run comparison and alternative prompts and check whether the brand appears beside retrieved alternatives.",
            "Expected Influence": "Comparison eligibility and first inclusion in alternative prompts.",
        },
        {
            "Action": "Strengthen third-party and structured evidence so the brand can be corroborated outside its own site.",
            "Gap Addressed": "The benchmark did not surface independent or machine-readable corroboration.",
            "Evidence Type": "Third-Party Evidence / Structured Evidence",
            "Why It Matters": "External references and consistent structured data reduce ambiguity and support retrieval confidence.",
            "Where Evidence Should Live": "Directories, partner pages, media references, industry profiles, schema markup, sameAs links, and organization data.",
            "Benchmark Validation Method": "Re-run entity, category, and market prompts after evidence is live and check for first measurable inclusion.",
            "Expected Influence": "Corroboration, entity clarity, and market association.",
        },
    ]


def _task_by_evidence_type(tasks):
    mapped_tasks = {}
    for task in tasks:
        evidence_type = str(task.get("Evidence Type", "")).strip()
        if evidence_type and evidence_type not in mapped_tasks:
            mapped_tasks[evidence_type] = task
    return mapped_tasks


def _asset_name_for_evidence_type(evidence_type, brand, category, market):
    names = {
        "Entity Evidence": f"Canonical {brand} entity and {category} category page",
        "Market Evidence": f"{market} market relevance proof page",
        "Offering Evidence": "Offering and use-case evidence pages",
        "Trust Evidence": "Substantiated trust proof page",
        "Comparison Evidence": "Comparison and alternatives evidence",
        "Third-Party Evidence / Structured Evidence": "Third-party and structured corroboration",
    }
    return names.get(evidence_type, evidence_type or "Recommendation readiness evidence")


def _target_prompt_groups_for_evidence_type(evidence_type, prompt_categories, market, audience):
    prompt_scope = ", ".join([
        str(item).strip()
        for item in prompt_categories or []
        if str(item).strip()
    ])
    prompt_suffix = f" Covered prompt groups: {prompt_scope}." if prompt_scope else ""
    targets = {
        "Entity Evidence": "Category, entity, and use-case prompts.",
        "Market Evidence": f"Prompts explicitly qualified for {market}.",
        "Offering Evidence": f"Use-case and audience-specific prompts for {audience}.",
        "Trust Evidence": "Trust, shortlist, and decision-stage prompts.",
        "Comparison Evidence": "Comparison, alternatives, and shortlist prompts.",
        "Third-Party Evidence / Structured Evidence": "Entity, category, market, and corroboration prompts.",
    }
    return f"{targets.get(evidence_type, 'Relevant category and market prompts.')}{prompt_suffix}"


def _evidence_type_for_retrieval_role(role):
    if role == RETRIEVAL_ROLE_LOCAL:
        return "Market Evidence"
    if role in {RETRIEVAL_ROLE_TECHNICAL, RETRIEVAL_ROLE_NICHE, RETRIEVAL_ROLE_PLANNING}:
        return "Offering Evidence"
    if role == RETRIEVAL_ROLE_TRUST:
        return "Trust Evidence"
    if role == RETRIEVAL_ROLE_COMPARISON:
        return "Comparison Evidence"
    if role == RETRIEVAL_ROLE_BUDGET:
        return "Comparison Evidence"
    return ""


def _brand_understanding_needs_entity_evidence(brand_understanding):
    if not brand_understanding:
        return True

    status_values = [
        _get_field(brand_understanding, "brand_known_status"),
        _get_field(brand_understanding, "category_alignment"),
        _get_field(brand_understanding, "market_alignment"),
        _get_field(brand_understanding, "audience_alignment"),
    ]

    return any(
        value in {"Unclear", "Misaligned", "Not Enough Evidence", ""}
        for value in status_values
    )


def _market_relevance_needs_market_evidence(market_relevance):
    if not market_relevance:
        return True

    market_lock_status = _get_field(market_relevance, "market_lock_status")
    local_signal = _get_field(market_relevance, "local_brand_presence_signal")

    return (
        market_lock_status in {"Global-default risk", "Insufficient evidence", ""}
        or local_signal in {"Weak", "Not Enough Evidence", ""}
    )


def _build_evidence_asset(task, priority, brand, category, market, audience, prompt_categories):
    evidence_type = str(task.get("Evidence Type", "")).strip()
    return {
        "priority": priority,
        "asset_name": _asset_name_for_evidence_type(
            evidence_type,
            brand,
            category,
            market,
        ),
        "what_to_build": task.get("Action", ""),
        "why_it_matters": task.get("Why It Matters", ""),
        "target_retrieval_driver": task.get("Gap Addressed", ""),
        "targets_or_prompt_groups": _target_prompt_groups_for_evidence_type(
            evidence_type,
            prompt_categories,
            market,
            audience,
        ),
        "validation": task.get("Benchmark Validation Method", ""),
    }


def build_first_three_evidence_assets(
    *,
    brand,
    category,
    market,
    audience,
    reference_brands=None,
    retrieved_brand_profiles=None,
    brand_understanding=None,
    market_relevance=None,
    prompt_categories=None,
):
    tasks = build_first_detection_task_roadmap(
        brand,
        category,
        market,
        audience,
        reference_brands=reference_brands,
    )
    tasks_by_type = _task_by_evidence_type(tasks)
    selected_evidence_types = []

    def select(evidence_type):
        if evidence_type in tasks_by_type and evidence_type not in selected_evidence_types:
            selected_evidence_types.append(evidence_type)

    if _brand_understanding_needs_entity_evidence(brand_understanding):
        select("Entity Evidence")

    if _market_relevance_needs_market_evidence(market_relevance):
        select("Market Evidence")

    for profile in retrieved_brand_profiles or []:
        select(_evidence_type_for_retrieval_role(profile.get("retrieval_role")))
        if len(selected_evidence_types) >= 3:
            break

    if reference_brands:
        select("Comparison Evidence")
        select("Trust Evidence")

    for evidence_type in [
        "Entity Evidence",
        "Market Evidence",
        "Offering Evidence",
        "Comparison Evidence",
        "Trust Evidence",
        "Third-Party Evidence / Structured Evidence",
    ]:
        select(evidence_type)
        if len(selected_evidence_types) >= 3:
            break

    assets = []
    for priority, evidence_type in enumerate(selected_evidence_types[:3], start=1):
        assets.append(
            _build_evidence_asset(
                tasks_by_type[evidence_type],
                priority,
                brand,
                category,
                market,
                audience,
                prompt_categories,
            )
        )

    return assets


def build_validation_plan(prompt_categories):
    prompt_categories = [
        str(item).strip()
        for item in prompt_categories or []
        if str(item).strip()
    ]
    prompt_scope = (
        ", ".join(prompt_categories)
        if prompt_categories
        else "the same category, market, use-case, comparison, and decision-stage prompt set"
    )

    return [
        {
            "Validation Area": "What to re-run",
            "Plan": f"Re-run a comparable Full Report Mode benchmark covering {prompt_scope}. Keep target brand, market, audience, and competitor set consistent where possible.",
        },
        {
            "Validation Area": "First milestone",
            "Plan": "First measurable inclusion: the target brand appears at least once in a relevant category, market, use-case, or comparison answer with the correct category context.",
        },
        {
            "Validation Area": "What counts as progress",
            "Plan": "Progress includes first target-brand mention, appearance in one relevant prompt category, accurate market association, or retrieval beside appropriate alternatives.",
        },
        {
            "Validation Area": "What does not count as proof",
            "Plan": "A one-off irrelevant mention, generic brand description, or broader business outcome claim does not prove durable AI visibility.",
        },
        {
            "Validation Area": "Timing expectation",
            "Plan": "No fixed timeline should be promised. The benchmark should be used to validate whether new evidence has become retrievable, not to promise AI mentions.",
        },
    ]
