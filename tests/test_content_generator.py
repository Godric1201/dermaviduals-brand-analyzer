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
