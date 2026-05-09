FIXED_PROMPTS = [
    {
        "category": "Professional Skincare",
        "prompt": "Which professional skincare brands are most commonly recommended in Hong Kong?"
    },
    {
        "category": "Clinic-Grade Skincare",
        "prompt": "What clinic-grade skincare brands are recommended for professional skincare users in Hong Kong?"
    },
    {
        "category": "Dermatologist Recommended",
        "prompt": "Which skincare brands are commonly recommended by dermatologists or skin professionals in Hong Kong?"
    },
    {
        "category": "Skin Therapist Recommendation",
        "prompt": "What professional skincare brands do skin therapists in Hong Kong recommend most often?"
    },
    {
        "category": "Sensitive Skin",
        "prompt": "Which professional skincare brands are recommended for sensitive or reactive skin in Hong Kong?"
    },
    {
        "category": "Barrier Repair",
        "prompt": "Which clinic-grade skincare brands are best known for skin barrier repair?"
    },
    {
        "category": "Corneotherapy",
        "prompt": "Which professional skincare brands focus on corneotherapy or skin barrier restoration?"
    },
    {
        "category": "Post-Treatment Care",
        "prompt": "What professional skincare brands are recommended for post-laser or post-aesthetic treatment recovery?"
    },
    {
        "category": "Acne-Prone Skin",
        "prompt": "Which clinic-grade skincare brands are recommended for acne-prone or congested skin?"
    },
    {
        "category": "Pigmentation",
        "prompt": "Which professional skincare brands are recommended for pigmentation, uneven skin tone, or dark spots?"
    },
    {
        "category": "Anti-Aging",
        "prompt": "Which professional skincare brands are recommended for anti-aging and skin rejuvenation?"
    },
    {
        "category": "Dry Skin",
        "prompt": "Which clinic-grade skincare brands are recommended for dry, dehydrated, or compromised skin?"
    },
    {
        "category": "Customized Skincare",
        "prompt": "What professional skincare brands offer customized or consultation-based skincare recommendations?"
    },
    {
        "category": "Ingredient Compatibility",
        "prompt": "Which professional skincare brands are known for skin compatibility and low-irritation formulations?"
    },
    {
        "category": "Premium Professional",
        "prompt": "Which premium professional skincare brands are worth considering in Hong Kong?"
    },
    {
        "category": "Comparison",
        "prompt": "How do professional skincare brands compare for sensitive skin, barrier repair, and post-treatment care?"
    },
    {
        "category": "Clinic-Grade Comparison",
        "prompt": "Compare clinic-grade skincare brands for professional use in Hong Kong."
    },
    {
        "category": "Professional Brand Ranking",
        "prompt": "What are the top professional skincare product brands for skin therapists and aesthetic clinics?"
    },
]


def _normalize_context(value):
    return " ".join(str(value).strip().split())


def audience_contains_market(audience, market):
    audience_text = _normalize_context(audience).lower()
    market_text = _normalize_context(market).lower()

    return bool(market_text and market_text in audience_text)


def format_audience_market_context(audience, market):
    audience_text = _normalize_context(audience)
    market_text = _normalize_context(market)

    if not audience_text:
        return f"in {market_text}" if market_text else ""

    if not market_text or audience_contains_market(audience_text, market_text):
        return audience_text

    return f"{audience_text} in {market_text}"


def build_fixed_prompts(category, market, audience):
    audience_market_context = format_audience_market_context(audience, market)

    return [
        {
            "category": "Best Options",
            "prompt": f"What are the best {category} for {audience_market_context}?"
        },
        {
            "category": "Local Recommendations",
            "prompt": f"Which {category} are most recommended locally in {market}?"
        },
        {
            "category": "Audience-Specific Recommendations",
            "prompt": f"Which {category} are best suited for {audience_market_context}?"
        },
        {
            "category": "Use-Case Recommendations",
            "prompt": f"Which {category} are recommended for common high-intent use cases among {audience_market_context}?"
        },
        {
            "category": "Premium Options",
            "prompt": f"Which premium or high-end {category} are worth considering in {market}?"
        },
        {
            "category": "Budget-Friendly Options",
            "prompt": f"Which accessible or budget-friendly {category} are worth considering in {market}?"
        },
        {
            "category": "Comparison Queries",
            "prompt": f"How do leading {category} compare for {audience_market_context}?"
        },
        {
            "category": "Alternatives To Leading Competitors",
            "prompt": f"What are good alternatives to leading {category} in {market}?"
        },
        {
            "category": "Trust And Review Signals",
            "prompt": f"Which {category} in {market} are known for strong reviews, trust signals, or customer confidence?"
        },
        {
            "category": "Decision Criteria",
            "prompt": f"What should {audience_market_context} consider when choosing between {category}?"
        },
    ]
