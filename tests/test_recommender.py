import recommender


def test_generate_recommendations_uses_generic_category_context(monkeypatch):
    captured = {}

    def fake_ask_ai(prompt, language="English"):
        captured["prompt"] = prompt
        return "Test recommendations"

    monkeypatch.setattr(recommender, "ask_ai", fake_ask_ai)

    result = recommender.generate_recommendations(
        brand="Cafe Brand",
        category="cafes",
        market="Berlin",
        audience="remote workers",
        summary_table="brand total_mentions\nCafe Brand 1",
        detailed_table="prompt_category brand visibility_score\nBest Options Cafe Brand 5",
    )

    prompt = captured["prompt"]

    assert result == "Test recommendations"
    assert "cafes" in prompt
    assert "Berlin" in prompt
    assert "remote workers" in prompt

    blocked_terms = [
        "professional skincare",
        "sensitive skin",
        "barrier repair",
        "clinic-grade",
        "post-treatment",
        "dermatologist",
        "skin therapist",
    ]

    prompt_lower = prompt.lower()
    for term in blocked_terms:
        assert term not in prompt_lower
