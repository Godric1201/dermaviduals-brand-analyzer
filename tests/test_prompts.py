from prompts import build_fixed_prompts


def test_build_fixed_prompts_uses_generic_category_inputs():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert len(prompts) == 10

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    assert "cafes" in prompt_text
    assert "berlin" in prompt_text
    assert "remote workers" in prompt_text


def test_build_fixed_prompts_returns_expected_intent_categories():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    categories = [item["category"] for item in prompts]

    assert categories == [
        "Best Options",
        "Local Recommendations",
        "Audience-Specific Recommendations",
        "Use-Case Recommendations",
        "Premium Options",
        "Budget-Friendly Options",
        "Comparison Queries",
        "Alternatives To Leading Competitors",
        "Trust And Review Signals",
        "Decision Criteria",
    ]


def test_build_fixed_prompts_avoids_skincare_specific_words():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    blocked_terms = [
        "skincare",
        "clinic-grade",
        "barrier repair",
        "sensitive skin",
        "post-treatment care",
    ]

    for term in blocked_terms:
        assert term not in prompt_text


def test_build_fixed_prompts_returns_expected_prompt_shape():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    for item in prompts:
        assert set(item) == {"category", "prompt"}
        assert item["category"]
        assert item["prompt"]


def test_build_fixed_prompts_uses_diverse_intent_wording():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    assert "premium" in prompt_text
    assert "budget-friendly" in prompt_text or "accessible" in prompt_text
    assert "alternatives" in prompt_text
    assert "reviews" in prompt_text or "trust signals" in prompt_text
    assert "consider when choosing" in prompt_text


def test_build_fixed_prompts_does_not_mention_target_brand_wording():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    assert "target brand" not in prompt_text
    assert "espresso house" not in prompt_text
