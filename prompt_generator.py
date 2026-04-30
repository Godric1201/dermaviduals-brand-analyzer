from analyzer import ask_ai
import ast


def extract_python_list(text):
    text = str(text).strip()

    text = (
        text.replace("```python", "")
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        return []

    list_text = text[start:end + 1]

    try:
        data = ast.literal_eval(list_text)
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


def is_valid_prompt(q):
    q_lower = q.lower()

    required_terms = [
        "brand",
        "brands",
        "product brands",
        "skincare brands",
        "clinic-grade skincare",
        "professional skincare",
    ]

    blocked_terms = [
        "where to find",
        "which clinic",
        "clinic near me",
        "book",
        "appointment",
        "price of treatment",
        "facial treatment center",
        "beauty salon near",
        "doctor near",
    ]

    if not any(term in q_lower for term in required_terms):
        return False

    if any(term in q_lower for term in blocked_terms):
        return False

    return True


def categorize_prompt(q):
    q_lower = q.lower()

    if "compare" in q_lower or "versus" in q_lower or "vs" in q_lower:
        return "AI Generated - Comparison"

    if "best" in q_lower or "top" in q_lower or "recommended" in q_lower:
        return "AI Generated - Brand Recommendation"

    if (
        "sensitive" in q_lower
        or "barrier" in q_lower
        or "acne" in q_lower
        or "pigmentation" in q_lower
        or "dry skin" in q_lower
        or "post-treatment" in q_lower
        or "anti-aging" in q_lower
    ):
        return "AI Generated - Problem Solution"

    return "AI Generated - Professional Skincare"


def generate_search_prompts(
    brand,
    competitors,
    category,
    market,
    audience,
    output_language="English"
):
    prompt = f"""
You are an AI search behavior expert specializing in professional skincare, clinic-grade skincare, and generative search visibility.

Generate 12 realistic AI search queries that users in {market} might ask when looking for professional skincare product BRAND recommendations.

Context:
- Target category: professional skincare product brands
- Market: {market}
- Audience: {audience}
- Channel focus: dermatology clinics, aesthetic clinics, professional skin therapists, beauty professionals
- Brand type: professional / clinic-grade / consultation-based skincare, not mass-market drugstore skincare

Important:
- Do NOT mention any specific brand names
- Do NOT mention {brand}
- Do NOT mention these competitors directly: {", ".join(competitors)}
- Every query must be unbiased
- Every query must be likely to make an AI answer with specific skincare brand names

Generate a balanced Prompt Matrix:

1. Brand Recommendation Queries
- Ask for the best or recommended professional skincare brands
- Must include words like "brands", "skincare brands", or "product brands"

2. Problem-Solution Queries
- Ask for professional skincare brands for specific skin needs:
  sensitive skin, barrier repair, acne-prone skin, pigmentation, dry skin, post-treatment care, anti-aging

3. Comparison Queries
- Ask to compare professional skincare brands or clinic-grade skincare brands
- Do not name any brand

Strict Rules:
- Return ONLY a Python list of strings
- No markdown
- No explanation
- No numbering outside the list
- Each query must be one sentence
- Avoid general advice questions such as "how to care for skin"
- Avoid service/location/booking questions such as "where to find clinics", "which clinic", "book treatment"
- Avoid asking about treatments, procedures, doctors, or salon services
- Focus only on skincare product brands

Good examples:
[
"What professional skincare brands are recommended for sensitive skin in Hong Kong?",
"Which clinic-grade skincare product brands are best for skin barrier repair?",
"Compare professional skincare brands for post-treatment care after aesthetic procedures.",
"What skincare brands do skin therapists recommend for acne-prone skin?",
"Which professional skincare brands are suitable for pigmentation and uneven skin tone?"
]
"""

    result = ask_ai(prompt, output_language)

    queries = extract_python_list(result)

    if not queries:
        print("⚠️ AI prompt generation failed")
        print("RAW:", result)

    filtered = []

    for q in queries:
        if isinstance(q, str) and q.strip() and is_valid_prompt(q):
            filtered.append(q.strip())

    seen = set()
    unique_filtered = []

    for q in filtered:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique_filtered.append(q)

    return [
        {
            "category": categorize_prompt(q),
            "prompt": q
        }
        for q in unique_filtered[:10]
    ]