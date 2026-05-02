def test_extract_section_between_markers(content_generator_module):
    text = """
Intro
## 1. SEO Blog Post
Blog content
## 2. Google Maps / Clinic Review Strategy
Review content
"""

    result = content_generator_module.extract_section(
        text,
        "## 1. SEO Blog Post",
        "## 2. Google Maps / Clinic Review Strategy",
    )

    assert result == "## 1. SEO Blog Post\nBlog content"


def test_extract_section_returns_original_text_when_start_missing(content_generator_module):
    text = "Plain content without the expected heading."

    assert content_generator_module.extract_section(text, "## Missing") == text


def test_extract_section_returns_from_start_when_end_missing(content_generator_module):
    text = """
Intro
## 4. FAQ Content
FAQ content
More FAQ content
"""

    result = content_generator_module.extract_section(
        text,
        "## 4. FAQ Content",
        "## 5. Comparison Page Outline",
    )

    assert result == "## 4. FAQ Content\nFAQ content\nMore FAQ content"


def test_generate_level_2_content_pack_uses_generic_category_prompt(
    monkeypatch,
    content_generator_module
):
    captured = {}

    fake_response = """
## 1. SEO Blog Post
Blog content
## 2. Local Review / Trust Signal Strategy
Review content
## 3. Social Posts
Social content
## 4. FAQ Content
FAQ content
## 5. Comparison Page Outline
Comparison content
## 6. AI Visibility Content Cluster
Cluster content
"""

    def fake_ask_ai(prompt, language="English"):
        captured["prompt"] = prompt
        return fake_response

    monkeypatch.setattr(content_generator_module, "ask_ai", fake_ask_ai)

    result = content_generator_module.generate_level_2_content_pack(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows", "einstein kaffee"],
        summary_table="summary",
        detailed_table="details",
    )

    prompt = captured["prompt"]

    assert "## 2. Local Review / Trust Signal Strategy" in prompt
    assert "Google Maps / Clinic Review Strategy" not in prompt
    assert "Clinic Review" not in prompt

    expected_terms = [
        "Espresso House",
        "cafes",
        "Berlin",
        "remote workers",
        "coffee fellows",
        "einstein kaffee",
    ]

    for term in expected_terms:
        assert term in prompt

    blocked_terms = [
        "professional skincare",
        "clinic-grade",
        "sensitive skin",
        "barrier repair",
        "post-treatment",
        "corneotherapy",
        "skin therapists",
        "Hong Kong skincare",
        "PCA Skin",
        "iS Clinical",
        "ZO Skin Health",
        "Biologique Recherche",
    ]

    prompt_lower = prompt.lower()
    for term in blocked_terms:
        assert term.lower() not in prompt_lower

    assert {
        "seo_blog",
        "review_strategy",
        "social_posts",
        "faq_content",
        "comparison_outline",
    }.issubset(result)


def test_generate_level_2_content_pack_supports_legacy_review_heading(
    monkeypatch,
    content_generator_module
):
    fake_response = """
## 1. SEO Blog Post
Blog content
## 2. Google Maps / Clinic Review Strategy
Legacy review content
## 3. Social Posts
Social content
## 4. FAQ Content
FAQ content
## 5. Comparison Page Outline
Comparison content
## 6. AI Visibility Content Cluster
Cluster content
"""

    def fake_ask_ai(prompt, language="English"):
        return fake_response

    monkeypatch.setattr(content_generator_module, "ask_ai", fake_ask_ai)

    result = content_generator_module.generate_level_2_content_pack(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        competitors=["coffee fellows", "einstein kaffee"],
        summary_table="summary",
        detailed_table="details",
    )

    assert result["seo_blog"] == "## 1. SEO Blog Post\nBlog content"
    assert result["review_strategy"] == (
        "## 2. Google Maps / Clinic Review Strategy\nLegacy review content"
    )
