import pandas as pd

import optimizer


def test_generate_action_plan_uses_generic_category_context(monkeypatch):
    captured = {}

    def fake_ask_ai(prompt, language="English"):
        captured["prompt"] = prompt
        return "Test strategy report"

    monkeypatch.setattr(optimizer, "ask_ai", fake_ask_ai)

    detailed_df = pd.DataFrame([
        {
            "brand": "Cafe Brand",
            "prompt_category": "Best Options",
            "prompt": "Best cafes in Berlin",
            "mentions": 1,
            "estimated_rank": 1,
            "visibility_score": 5,
            "visibility_level": "medium",
            "is_target_brand": True,
        }
    ])
    summary_df = pd.DataFrame([
        {
            "brand": "Cafe Brand",
            "total_mentions": 1,
            "average_visibility_score": 5,
            "prompts_visible": 1,
            "share_of_voice_percent": 100,
        }
    ])

    result = optimizer.generate_action_plan(
        brand="Cafe Brand",
        detailed_df=detailed_df,
        summary_df=summary_df,
        raw_answers=[
            {
                "prompt_category": "Best Options",
                "prompt": "Best cafes in Berlin",
                "answer": "Cafe Brand is mentioned.",
            }
        ],
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    prompt = captured["prompt"]

    assert result == "Test strategy report"
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

    assert "Do not make aggressive numeric performance promises" in prompt
    assert "0 mentions" in prompt
    assert "1-3 relevant prompt categories" in prompt
    assert "directional next-benchmark goals" in prompt
    assert "Use only numeric metrics explicitly provided" in prompt
    assert "Do not invent mention counts" in prompt
    assert "Do not treat first_position" in prompt
    assert "If a metric is not provided, describe it qualitatively" in prompt
