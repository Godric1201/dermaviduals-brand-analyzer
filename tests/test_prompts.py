from prompts import build_fixed_prompts


def test_build_fixed_prompts_uses_generic_category_inputs():
    prompts = build_fixed_prompts(
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert 5 <= len(prompts) <= 8

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    assert "cafes" in prompt_text
    assert "berlin" in prompt_text
    assert "remote workers" in prompt_text


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
