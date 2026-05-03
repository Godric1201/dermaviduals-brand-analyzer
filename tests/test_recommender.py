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

    assert "Recommendations should be non-overlapping" in prompt
    assert "priority level" in prompt
    assert "query territory" in prompt
    assert "competitor challenged" in prompt
    assert "content asset or evidence asset" in prompt
    assert "intended benchmark metric impact" in prompt
    assert "validated in Full Report Mode" in prompt
    assert "Do not use unsupported percentages" in prompt
    assert "Do not mention conversion rate" in prompt
    assert "session duration" in prompt
    assert "total_mentions" in prompt
    assert "average_visibility_score" in prompt
    assert "prompts_visible" in prompt
    assert "share_of_voice_percent" in prompt
    assert "query intent visibility" in prompt
