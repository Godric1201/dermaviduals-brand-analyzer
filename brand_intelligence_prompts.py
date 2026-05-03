DIAGNOSTIC_VALIDATION_NOTE = (
    "AI-inferred; validate before using as client-facing fact."
)


def parse_user_brand_strengths(text):
    return [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]


def build_target_diagnostic_prompts(
    brand,
    category,
    market,
    audience,
    competitors=None,
    user_brand_strengths=None,
):
    competitors = competitors or []
    user_brand_strengths = user_brand_strengths or []

    competitor_context = "None provided"
    if competitors:
        competitor_context = ", ".join(competitors)

    strengths_context = "None provided"
    if user_brand_strengths:
        strengths_context = "; ".join(user_brand_strengths)

    shared_context = f"""
This is a target-brand diagnostic prompt for Brand Intelligence and Positioning Gap Analysis.
It is not part of the unbranded benchmark metrics.

Target Brand: {brand}
Category: {category}
Market: {market}
Audience: {audience}
Competitor Context: {competitor_context}
User-Provided Brand Strengths: {strengths_context}
Tracked Competitors Included in Scoring: {competitor_context}
AI-Discovered Market Signals Not Included in Scoring: Identify only if they appear in diagnostic analysis or benchmark raw answers and label them clearly.

Important:
- Label uncertain or weakly supported claims clearly.
- Distinguish AI-inferred observations from user-provided positioning notes.
- Distinguish natural benchmark visibility from prompted diagnostic fit.
- Do not imply natural AI recommendation visibility from a target-branded diagnostic prompt.
- Natural benchmark visibility refers to unbranded benchmark results.
- Prompted diagnostic fit is a target-branded diagnostic assessment that requires validation.
- Tracked competitors are the benchmark competitors included in visibility scoring.
- AI-discovered market signals are diagnostic only and must not be described as included in scoring unless they are tracked competitors.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- If a brand is not in the tracked competitor list, label it as an AI-discovered market signal.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not list tracked competitors as AI-discovered market signals.
- Before suggesting a brand for the next benchmark run, verify it is not already in the tracked competitor list.
- If no non-tracked brands are available, say no additional non-tracked market signals were identified.
- Do not place tracked competitors and non-tracked brands in the same competitor advantage list unless each item is labeled with Source: Tracked competitor or Source: AI-discovered market signal.
- Prefer tracked competitors first when listing competitor signals.
- If non-tracked brands are strategically relevant, add: "Consider adding these brands as tracked competitors before the benchmark run."
- Do not call non-tracked brands competitors included in benchmark scoring.
- Clearly label signals as Benchmark-derived, AI-inferred, or User-provided where relevant.
- Prefer compact tables or bullet lists over long paragraphs.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
- If the benchmark shows the target brand has 0 mentions or 0 share of voice, describe diagnostic fit as potential, prompted, or subject to validation, not as natural recommendation visibility.
- Avoid unsupported factual claims.
- {DIAGNOSTIC_VALIDATION_NOTE}
"""

    return [
        {
            "category": "Brand Knowledge",
            "prompt": f"""
{shared_context}

Diagnostic task:
What does AI appear to know about {brand} in the context of {category} for {audience} in {market}?

Return:
- Known associations
- Weak or uncertain associations
- Missing context
- Evidence that would need validation
- Compact bullet points only
""".strip()
        },
        {
            "category": "Category Association",
            "prompt": f"""
{shared_context}

Diagnostic task:
How is {brand} associated with {category}, and which needs, use cases, or buyer questions for {audience} in {market} does it appear connected to?

Return:
- Strong category associations
- Weak category associations
- Missing use-case associations
- Uncertainty notes
- Benchmark-derived / AI-inferred labels where relevant
""".strip()
        },
        {
            "category": "Strengths And Weaknesses",
            "prompt": f"""
{shared_context}

Diagnostic task:
What strengths, weaknesses, and uncertainties would AI infer for {brand} as a {category} option for {audience} in {market}?

Return:
- AI-inferred strengths
- AI-inferred weaknesses
- User-provided strengths that appear unsupported or under-evidenced
- Validation needs
- Compact bullet points only
""".strip()
        },
        {
            "category": "Prompted Diagnostic Fit",
            "prompt": f"""
{shared_context}

Diagnostic task:
Assess the prompted diagnostic fit of {brand} as a {category} option for {audience} in {market}. Explain why, why not, and what evidence would change that assessment.

Return:
- Prompted Diagnostic Fit
- Reasons for inclusion
- Reasons for exclusion
- Evidence gaps
- Action implications

Rules:
- Describe this as prompted diagnostic fit, not natural benchmark visibility.
- If benchmark visibility is weak or absent, keep the assessment potential, prompted, and subject to validation.
""".strip()
        },
        {
            "category": "Competitive Comparison",
            "prompt": f"""
{shared_context}

Diagnostic task:
How does {brand} appear to compare with other {category} brands or providers in {market}, using the competitor context where relevant?

Return:
- Competitor advantages
- Target brand advantages
- Comparison gaps
- Positioning opportunities
- Distinguish tracked competitors from AI-discovered market signals
""".strip()
        },
        {
            "category": "Evidence And Trust Signals",
            "prompt": f"""
{shared_context}

Diagnostic task:
What evidence, reviews, third-party references, local proof points, or trust signals would make {brand} more credible as a {category} option for {audience} in {market}?

Return:
- Existing trust signals AI may infer
- Missing trust signals
- Evidence-building opportunities
- Validation notes
- Concrete evidence gaps and recommended action types
""".strip()
        },
    ]
