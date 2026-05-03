import ast

from analyzer import ask_ai
from prompts import format_audience_market_context


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
        "provider",
        "providers",
        "option",
        "options",
        "service",
        "services",
        "product",
        "products",
        "tool",
        "tools",
        "platform",
        "platforms",
        "solution",
        "solutions",
        "vendor",
        "vendors",
        "company",
        "companies",
        "best",
        "top",
        "recommended",
        "recommendation",
        "recommendations",
        "compare",
        "comparison",
        "alternative",
        "alternatives",
        "local",
        "reviews",
        "review",
        "trust",
        "premium",
        "budget",
        "decision criteria",
        "consider",
        "choosing",
    ]

    blocked_terms = [
        "book",
        "appointment",
        "price of treatment",
        "where to buy",
        "coupon",
        "discount code",
        "how should i",
        "how do i",
        "tutorial",
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

    if "alternative" in q_lower or "alternatives" in q_lower:
        return "AI Generated - Alternatives"

    if "local" in q_lower or "nearby" in q_lower or " in " in q_lower:
        return "AI Generated - Local Recommendations"

    if "review" in q_lower or "reviews" in q_lower or "trust" in q_lower:
        return "AI Generated - Trust Signals"

    if "premium" in q_lower or "high-end" in q_lower:
        return "AI Generated - Premium Options"

    if "budget" in q_lower or "affordable" in q_lower or "accessible" in q_lower:
        return "AI Generated - Budget-Friendly Options"

    if "decision criteria" in q_lower or "consider" in q_lower or "choosing" in q_lower:
        return "AI Generated - Decision Criteria"

    if "best" in q_lower or "top" in q_lower or "recommended" in q_lower:
        return "AI Generated - Brand Recommendation"

    if "use case" in q_lower or "use cases" in q_lower:
        return "AI Generated - Use-Case Recommendations"

    return "AI Generated - Category Discovery"


def contains_blocked_brand(query, brand, competitors):
    q_lower = query.lower()
    blocked_names = [brand] + list(competitors or [])

    return any(
        name and str(name).lower() in q_lower
        for name in blocked_names
    )


def generate_search_prompts(
    brand,
    competitors,
    category,
    market,
    audience,
    output_language="English"
):
    audience_market_context = format_audience_market_context(audience, market)

    prompt = f"""
You are an AI search behavior expert specializing in generative search visibility and category recommendation behavior.

Generate 12 realistic AI search queries that users in {market} might ask when looking for {category} recommendations.

Context:
- Target category: {category}
- Market: {market}
- Audience: {audience}

Important:
- Do NOT mention any specific brand names
- Do NOT mention {brand}
- Do NOT mention these competitors directly: {", ".join(competitors)}
- Every query must be unbiased
- Every query must be likely to make an AI answer with specific brands, providers, products, services, tools, platforms, or solutions in the category
- Use {category}, {market}, and {audience} naturally

Generate a balanced Prompt Matrix:

1. Best Options / Top Recommendations
- Ask for the best, top, or recommended {category}

2. Local Recommendations
- Ask which {category} are recommended locally in {market}

3. Audience-Specific Recommendations
- Ask which {category} are best suited for {audience_market_context}

4. High-Intent Use Cases
- Ask which {category} fit common high-intent use cases for {audience_market_context}

5. Premium / Budget Options
- Include premium, high-end, accessible, or budget-friendly recommendation contexts

6. Comparison Queries
- Ask how leading {category} compare without naming any brand

7. Alternatives To Leading Competitors
- Ask for alternatives to leading {category} without naming any brand

8. Trust Signals And Reviews
- Ask which {category} are known for strong reviews, trust signals, credibility, or customer confidence

9. Decision Criteria
- Ask what {audience_market_context} should consider when choosing between {category}

Strict Rules:
- Return ONLY a Python list of strings
- No markdown
- No explanation
- No numbering outside the list
- Each query must be one sentence
- Avoid broad general advice questions that do not ask for category options, brands, providers, products, services, tools, platforms, or solutions
- Avoid booking, appointment, coupon, discount, or transactional shopping questions
- Avoid regulated-category advice unless the category itself explicitly requires it
- Keep every query category-neutral, market-aware, and suitable for benchmark visibility scoring

Good examples:
[
"What are the best {category} for {audience_market_context}?",
"Which {category} brands or providers are most recommended locally in {market}?",
"How do leading {category} compare for {audience_market_context}?",
"What are good alternatives to leading {category} in {market}?",
"What should {audience_market_context} consider when choosing between {category}?"
]
"""

    result = ask_ai(prompt, output_language)

    queries = extract_python_list(result)

    filtered = []

    for q in queries:
        if not isinstance(q, str):
            continue

        query = q.strip()
        if (
            query
            and is_valid_prompt(query)
            and not contains_blocked_brand(query, brand, competitors)
        ):
            filtered.append(query)

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
