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
            "Prompts Visible": metrics.prompts_visible,
            "Share of Voice %": metrics.share_of_voice_percent,
            "Interpretation": (
                "Retrieved alternative with measurable benchmark signal; use as evidence context, not as a brand to attack."
            ),
        })

    return reference_brands


def build_market_relevance_interpretation(brand, market, category, reference_brands):
    if reference_brands:
        names = ", ".join(str(item["Brand"]) for item in reference_brands[:3])
        return (
            f"The benchmark retrieved AI-visible reference brands such as {names} while {brand} was not detected. "
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
