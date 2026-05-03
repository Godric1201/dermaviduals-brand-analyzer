from brand_intelligence_prompts import (
    build_target_diagnostic_prompts,
    parse_user_brand_strengths,
)


def test_build_target_diagnostic_prompts_returns_expected_shape():
    prompts = build_target_diagnostic_prompts(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert len(prompts) == 6

    expected_categories = [
        "Brand Knowledge",
        "Category Association",
        "Strengths And Weaknesses",
        "Prompted Diagnostic Fit",
        "Competitive Comparison",
        "Evidence And Trust Signals",
    ]

    assert [item["category"] for item in prompts] == expected_categories

    for item in prompts:
        assert set(item) == {"category", "prompt"}
        assert item["category"]
        assert item["prompt"]


def test_build_target_diagnostic_prompts_include_context_and_validation_wording():
    prompts = build_target_diagnostic_prompts(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    for item in prompts:
        prompt = item["prompt"]

        assert "diagnostic" in prompt.lower()
        assert "AI-inferred; validate before using as client-facing fact." in prompt
        assert "Espresso House" in prompt
        assert "cafes" in prompt
        assert "Berlin" in prompt
        assert "remote workers" in prompt
        assert "Prefer compact tables or bullet lists" in prompt
        assert "Avoid generic advice" in prompt


def test_build_target_diagnostic_prompts_distinguish_benchmark_visibility_and_diagnostic_fit():
    prompts = build_target_diagnostic_prompts(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    prompt_text = " ".join(item["prompt"] for item in prompts).lower()

    assert "prompted diagnostic fit" in prompt_text
    assert "natural benchmark visibility" in prompt_text
    assert "unbranded benchmark results" in prompt_text
    assert "0 mentions or 0 share of voice" in prompt_text
    assert "benchmark-derived" in prompt_text
    assert "ai-inferred" in prompt_text
    assert "user-provided" in prompt_text
    assert "tracked competitors included in scoring" in prompt_text
    assert "ai-discovered market signals not included in scoring" in prompt_text
    assert "tracked competitor list is the only source of truth" in prompt_text
    assert "tracked competitors" in prompt_text
    assert "ai-discovered market signals" in prompt_text
    assert "source: tracked competitor" in prompt_text
    assert "source: ai-discovered market signal" in prompt_text
    assert "never label a non-tracked brand as source: tracked competitor" in prompt_text
    assert "do not list tracked competitors as ai-discovered market signals" in prompt_text
    assert "verify it is not already in the tracked competitor list" in prompt_text
    assert "no additional non-tracked market signals were identified" in prompt_text
    assert "selected as tracked competitors before the benchmark run" in prompt_text or "consider adding these brands as tracked competitors before the benchmark run." in prompt_text
    assert "do not call non-tracked brands competitors included in benchmark" in prompt_text
    assert "recommendation likelihood" not in prompt_text


def test_build_target_diagnostic_prompts_can_include_competitors_and_user_strengths():
    prompts = build_target_diagnostic_prompts(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows", "einstein kaffee"],
        user_brand_strengths=["quiet work tables", "central locations"],
    )

    prompt_text = " ".join(item["prompt"] for item in prompts)

    assert "coffee fellows" in prompt_text
    assert "einstein kaffee" in prompt_text
    assert "quiet work tables" in prompt_text
    assert "central locations" in prompt_text


def test_parse_user_brand_strengths_keeps_one_item_per_line_without_rewriting():
    strengths = parse_user_brand_strengths(
        """
          quiet work tables

        Starbuks typo stays
        iS Clinical casing
        """
    )

    assert strengths == [
        "quiet work tables",
        "Starbuks typo stays",
        "iS Clinical casing",
    ]
