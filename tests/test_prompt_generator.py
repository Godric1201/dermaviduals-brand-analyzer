def test_extract_python_list_from_code_fence(prompt_generator_module):
    text = """
```python
[
    "What are the best cafes for remote workers in Berlin?",
    "Which cafes in Berlin have strong reviews and trust signals?"
]
```
"""

    result = prompt_generator_module.extract_python_list(text)

    assert result == [
        "What are the best cafes for remote workers in Berlin?",
        "Which cafes in Berlin have strong reviews and trust signals?",
    ]


def test_extract_python_list_from_surrounding_text(prompt_generator_module):
    text = 'Here are prompts: ["one", "two"] Thanks.'

    assert prompt_generator_module.extract_python_list(text) == ["one", "two"]


def test_extract_python_list_returns_empty_for_invalid_text(prompt_generator_module):
    assert prompt_generator_module.extract_python_list("not a list") == []
    assert prompt_generator_module.extract_python_list('["missing end"') == []


def test_is_valid_prompt_accepts_generic_recommendation_query(prompt_generator_module):
    query = "What are the best cafe options for remote workers in Berlin?"

    assert prompt_generator_module.is_valid_prompt(query) is True


def test_is_valid_prompt_accepts_trust_and_decision_queries(prompt_generator_module):
    trust_query = "Which cafes are known for strong reviews and trust signals?"
    decision_query = "What should remote workers consider when choosing between cafe options?"

    assert prompt_generator_module.is_valid_prompt(trust_query) is True
    assert prompt_generator_module.is_valid_prompt(decision_query) is True


def test_is_valid_prompt_rejects_general_advice_query(prompt_generator_module):
    query = "How should I brew better espresso at home?"

    assert prompt_generator_module.is_valid_prompt(query) is False


def test_is_valid_prompt_rejects_booking_or_transactional_query(prompt_generator_module):
    query = "Which cafe options can I book an appointment for near me?"

    assert prompt_generator_module.is_valid_prompt(query) is False


def test_generate_search_prompts_uses_generic_category_context(
    monkeypatch,
    capsys,
    prompt_generator_module,
):
    captured_prompts = []
    fake_queries = [
        "What are the best cafes for remote workers in Berlin?",
        "Which cafes brands or providers are recommended locally in Berlin?",
        "How do leading cafes compare for remote workers in Berlin?",
        "What are good alternatives to leading cafes in Berlin?",
        "Which cafes in Berlin are known for strong reviews and trust signals?",
        "What should remote workers in Berlin consider when choosing between cafes?",
        "Which premium cafes are worth considering in Berlin?",
        "Which budget-friendly cafes are worth considering in Berlin?",
        "Which cafes fit high-intent use cases for remote workers in Berlin?",
        "Which cafes brands are top recommendations for remote workers in Berlin?",
        "Which cafes in Berlin are most trusted by remote workers?",
        "Is Espresso House one of the best cafes in Berlin for remote workers?",
        "How does Coffee Fellows compare with other cafes in Berlin?",
        "What are the best cafes for remote workers in Berlin?",
    ]

    def fake_ask_ai(prompt, language="English"):
        captured_prompts.append(prompt)
        return repr(fake_queries)

    monkeypatch.setattr(prompt_generator_module, "ask_ai", fake_ask_ai)

    result = prompt_generator_module.generate_search_prompts(
        brand="Espresso House",
        competitors=["Coffee Fellows", "Einstein Kaffee"],
        category="cafes",
        market="Berlin",
        audience="remote workers",
        output_language="English",
    )

    prompt = captured_prompts[0]
    blocked_terms = [
        "professional skincare",
        "clinic-grade",
        "sensitive skin",
        "barrier repair",
        "post-treatment",
        "dermatologist",
        "skin therapist",
        "Hong Kong skincare",
    ]

    assert "cafes" in prompt
    assert "Berlin" in prompt
    assert "remote workers" in prompt
    assert "comparison" in prompt.lower()
    assert "local" in prompt.lower()
    assert "trust" in prompt.lower() or "reviews" in prompt.lower()
    assert "decision criteria" in prompt.lower()
    assert "cafes options" not in prompt.lower()
    assert "in berlin in berlin" not in prompt.lower()

    for term in blocked_terms:
        assert term.lower() not in prompt.lower()

    assert len(result) == 10
    assert all(set(item) == {"category", "prompt"} for item in result)
    assert all("Espresso House" not in item["prompt"] for item in result)
    assert all("Coffee Fellows" not in item["prompt"] for item in result)
    assert all("cafes brands or providers" not in item["prompt"].lower() for item in result)
    assert all("in berlin in berlin" not in item["prompt"].lower() for item in result)
    assert capsys.readouterr().out == ""


def test_generate_search_prompts_avoids_duplicate_audience_market_context(
    monkeypatch,
    prompt_generator_module,
):
    captured_prompts = []

    def fake_ask_ai(prompt, language="English"):
        captured_prompts.append(prompt)
        return "[]"

    monkeypatch.setattr(prompt_generator_module, "ask_ai", fake_ask_ai)

    prompt_generator_module.generate_search_prompts(
        brand="Dermaviduals",
        competitors=["Competitor A"],
        category="skincare products",
        market="Hong Kong",
        audience="skincare-conscious consumers in Hong Kong",
        output_language="English",
    )

    prompt = captured_prompts[0]

    assert "skincare-conscious consumers in Hong Kong in Hong Kong" not in prompt
    assert "skincare-conscious consumers in Hong Kong" in prompt


def test_generate_search_prompts_returns_empty_without_debug_print(
    monkeypatch,
    capsys,
    prompt_generator_module,
):
    monkeypatch.setattr(
        prompt_generator_module,
        "ask_ai",
        lambda prompt, language="English": "not a python list",
    )

    result = prompt_generator_module.generate_search_prompts(
        brand="Espresso House",
        competitors=["Coffee Fellows"],
        category="cafes",
        market="Berlin",
        audience="remote workers",
    )

    assert result == []
    assert capsys.readouterr().out == ""


def test_clean_generated_prompt_text_fixes_product_brand_grammar(
    prompt_generator_module,
):
    cleaned = prompt_generator_module.clean_generated_prompt_text(
        "Which skincare products brands or providers are most recommended locally in Hong Kong?",
        category="skincare products",
        market="Hong Kong",
    )

    assert cleaned == (
        "Which skincare product brands are most recommended locally in Hong Kong?"
    )


def test_clean_generated_prompt_text_fixes_cafes_options_and_market_duplication(
    prompt_generator_module,
):
    cleaned = prompt_generator_module.clean_generated_prompt_text(
        "What are the best cafes options in Berlin in Berlin?",
        category="cafes",
        market="Berlin",
    )

    assert cleaned == "What are the best cafes in Berlin?"


def test_clean_generated_prompt_text_keeps_valid_prompt_stable(
    prompt_generator_module,
):
    prompt = "How do leading cafes compare for remote workers in Berlin?"

    cleaned = prompt_generator_module.clean_generated_prompt_text(
        prompt,
        category="cafes",
        market="Berlin",
    )

    assert cleaned == prompt
