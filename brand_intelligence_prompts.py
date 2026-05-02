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

Important:
- Label uncertain or weakly supported claims clearly.
- Distinguish AI-inferred observations from user-provided positioning notes.
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
""".strip()
        },
        {
            "category": "Recommendation Likelihood",
            "prompt": f"""
{shared_context}

Diagnostic task:
Would AI be likely to recommend {brand} as a {category} option for {audience} in {market}? Explain why, why not, and what evidence would change that recommendation.

Return:
- Recommendation likelihood
- Reasons for inclusion
- Reasons for exclusion
- Evidence gaps
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
""".strip()
        },
    ]
