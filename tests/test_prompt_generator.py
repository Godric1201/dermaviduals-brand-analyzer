def test_extract_python_list_from_code_fence(prompt_generator_module):
    text = """
```python
[
    "What professional skincare brands are recommended in Hong Kong?",
    "Which clinic-grade skincare brands are best for sensitive skin?"
]
```
"""

    result = prompt_generator_module.extract_python_list(text)

    assert result == [
        "What professional skincare brands are recommended in Hong Kong?",
        "Which clinic-grade skincare brands are best for sensitive skin?",
    ]


def test_extract_python_list_from_surrounding_text(prompt_generator_module):
    text = 'Here are prompts: ["one", "two"] Thanks.'

    assert prompt_generator_module.extract_python_list(text) == ["one", "two"]


def test_extract_python_list_returns_empty_for_invalid_text(prompt_generator_module):
    assert prompt_generator_module.extract_python_list("not a list") == []
    assert prompt_generator_module.extract_python_list('["missing end"') == []


def test_is_valid_prompt_accepts_brand_recommendation_query(prompt_generator_module):
    query = "What professional skincare brands are recommended for sensitive skin?"

    assert prompt_generator_module.is_valid_prompt(query) is True


def test_is_valid_prompt_rejects_general_advice_query(prompt_generator_module):
    query = "How should I care for sensitive skin?"

    assert prompt_generator_module.is_valid_prompt(query) is False


def test_is_valid_prompt_rejects_booking_or_location_query(prompt_generator_module):
    query = "Which skincare brands can I book an appointment for near me?"

    assert prompt_generator_module.is_valid_prompt(query) is False
