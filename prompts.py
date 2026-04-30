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


def build_fixed_prompts(category, market, audience):
    return [
        {
            "category": "Best Options",
            "prompt": f"What are the best {category} for {audience} in {market}?"
        },
        {
            "category": "Recommended Brands",
            "prompt": f"Which {category} brands or providers are most commonly recommended for {audience} in {market}?"
        },
        {
            "category": "Local Recommendations",
            "prompt": f"What {category} options are most recommended in {market}?"
        },
        {
            "category": "Comparison",
            "prompt": f"How do leading {category} brands or providers compare for {audience} in {market}?"
        },
        {
            "category": "Quality Signals",
            "prompt": f"Which {category} options are known for quality, trust, and strong customer fit in {market}?"
        },
        {
            "category": "Decision Criteria",
            "prompt": f"What should {audience} consider when choosing {category} in {market}?"
        },
        {
            "category": "Top Ranking",
            "prompt": f"What are the top ranked {category} brands or providers for {audience}?"
        },
    ]
