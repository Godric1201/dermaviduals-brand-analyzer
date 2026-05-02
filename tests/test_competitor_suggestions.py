import pytest

from conftest import import_without_real_analyzer


@pytest.fixture()
def competitor_suggestions_module():
    return import_without_real_analyzer("competitor_suggestions")


def test_build_competitor_suggestion_prompt_includes_context(
    competitor_suggestions_module
):
    prompt = competitor_suggestions_module.build_competitor_suggestion_prompt(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        existing_competitors=["Coffee Fellows", "Einstein Kaffee"],
    )

    expected_terms = [
        "Espresso House",
        "cafes",
        "Berlin",
        "remote workers",
        "Coffee Fellows",
        "Einstein Kaffee",
        "one competitor per line",
        "not automatically included in scoring",
    ]

    for term in expected_terms:
        assert term in prompt


def test_suggest_competitors_with_ai_returns_parsed_suggestions(
    monkeypatch,
    competitor_suggestions_module
):
    captured = {}

    def fake_ask_ai(prompt, language="English"):
        captured["prompt"] = prompt
        captured["language"] = language
        return """
        The Barn
        Five Elephant
        Coffee Circle
        """

    monkeypatch.setattr(competitor_suggestions_module, "ask_ai", fake_ask_ai)

    suggestions = competitor_suggestions_module.suggest_competitors_with_ai(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        existing_competitors=["Coffee Fellows"],
        answer_language="English",
    )

    assert suggestions == ["The Barn", "Five Elephant", "Coffee Circle"]
    assert "Espresso House" in captured["prompt"]
    assert captured["language"] == "English"


def test_parse_competitor_suggestions_removes_bullets_and_numbers(
    competitor_suggestions_module
):
    suggestions = competitor_suggestions_module.parse_competitor_suggestions(
        """
        - The Barn
        * Five Elephant
        1. Coffee Circle
        2) Bonanza Coffee
        • Distrikt Coffee
        """
    )

    assert suggestions == [
        "The Barn",
        "Five Elephant",
        "Coffee Circle",
        "Bonanza Coffee",
        "Distrikt Coffee",
    ]


def test_parse_competitor_suggestions_removes_duplicates_case_insensitively(
    competitor_suggestions_module
):
    suggestions = competitor_suggestions_module.parse_competitor_suggestions(
        """
        The Barn
        the barn
        THE BARN
        Five Elephant
        """
    )

    assert suggestions == ["The Barn", "Five Elephant"]


def test_parse_competitor_suggestions_removes_existing_competitors(
    competitor_suggestions_module
):
    suggestions = competitor_suggestions_module.parse_competitor_suggestions(
        """
        Coffee Fellows
        Einstein Kaffee
        The Barn
        """,
        existing_competitors=["coffee fellows", "EINSTEIN KAFFEE"],
    )

    assert suggestions == ["The Barn"]


def test_parse_competitor_suggestions_respects_max_suggestions(
    competitor_suggestions_module
):
    suggestions = competitor_suggestions_module.parse_competitor_suggestions(
        """
        One
        Two
        Three
        Four
        """,
        max_suggestions=2,
    )

    assert suggestions == ["One", "Two"]


def test_parse_competitor_suggestions_does_not_autocorrect_spelling(
    competitor_suggestions_module
):
    suggestions = competitor_suggestions_module.parse_competitor_suggestions(
        "starbuks"
    )

    assert suggestions == ["starbuks"]


def test_suggest_competitors_with_ai_removes_target_brand(
    monkeypatch,
    competitor_suggestions_module
):
    def fake_ask_ai(prompt, language="English"):
        return """
        Espresso House
        The Barn
        """

    monkeypatch.setattr(competitor_suggestions_module, "ask_ai", fake_ask_ai)

    suggestions = competitor_suggestions_module.suggest_competitors_with_ai(
        brand="Espresso House",
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert suggestions == ["The Barn"]
