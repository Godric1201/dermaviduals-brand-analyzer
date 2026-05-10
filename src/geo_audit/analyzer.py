import json
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class AIServiceError(RuntimeError):
    """Raised when the AI service cannot return a usable response."""


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create the OpenAI client lazily so imports do not fail before runtime."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise AIServiceError(
            "OPENAI_API_KEY is not configured. Create a local .env file based on .env.example."
        )

    return OpenAI(api_key=api_key)


def ask_ai(prompt: str, language: str = "English", model: str | None = None) -> str:
    """
    Main AI answer generator.

    Used for generating recommendation answers and strategic report sections.
    Raises AIServiceError when the API call fails instead of returning raw error text
    as if it were a valid AI answer.
    """
    selected_model = model or DEFAULT_MODEL

    try:
        response = get_openai_client().chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": f"""
Answer in {language}.

Be analytical and strategic when generating reports.

When analyzing:
- Identify patterns
- Explain cause-and-effect relationships
- Avoid generic advice
- Focus on decision logic

When the question asks for skincare brands, professional skincare, clinic-grade skincare, or skincare product recommendations:

- ALWAYS provide a clear list of brand names when relevant
- Format skincare brand recommendations as a numbered list
- Put brand names at the beginning of each line

Example:
1. Brand A – explanation
2. Brand B – explanation
3. Brand C – explanation

Rules:
- Do NOT give only general advice when brand recommendations are requested
- Do NOT avoid naming brands
- Prioritize professional, clinic-grade, dermatologist-recommended skincare brands
""",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise AIServiceError("AI service returned an empty response.")

        return content

    except AIServiceError:
        raise
    except Exception as error:
        raise AIServiceError(f"AI request failed: {error}") from error


def evaluate_brand_visibility(
    answer: str,
    brand: str,
    model: str | None = None,
) -> dict:
    """
    Evaluates whether a specific brand appears in an AI answer.

    This function uses a separate evaluator prompt and returns a safe fallback
    if the AI response cannot be parsed as valid JSON.
    """
    selected_model = model or DEFAULT_MODEL

    evaluation_prompt = f"""
Analyze the AI answer below and evaluate how visible this brand is.

Brand:
{brand}

AI Answer:
{answer}

Return ONLY valid JSON with this exact structure:
{{
    "mentioned": true,
    "position": 1,
    "visibility_score": 90,
    "visibility_level": "Strong"
}}

Rules:
- "mentioned" must be true or false
- "position" is the order in the list if the brand appears in a ranked or numbered recommendation list
- use null if there is no clear ranking
- "visibility_score" must be 0–100

Scoring logic:
- 90–100 = top / first few brands
- 70–89 = clearly recommended
- 40–69 = mentioned but not emphasized
- 10–39 = weak mention
- 0 = not mentioned

- "visibility_level" must be one of:
  "Top", "Strong", "Moderate", "Weak", "Not Visible"
"""

    try:
        response = get_openai_client().chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": """
You are a strict JSON-only AI search visibility evaluator.

Your task is to evaluate whether a specific brand appears in an AI-generated answer.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.
Do not include brand recommendation lists.
""",
                },
                {
                    "role": "user",
                    "content": evaluation_prompt,
                },
            ],
            temperature=0,
        )

        result = response.choices[0].message.content.strip()
        data = json.loads(result)

        return {
            "mentioned": bool(data.get("mentioned", False)),
            "position": data.get("position"),
            "visibility_score": int(data.get("visibility_score", 0)),
            "visibility_level": data.get("visibility_level", "Not Visible"),
        }

    except Exception:
        return {
            "mentioned": False,
            "position": None,
            "visibility_score": 0,
            "visibility_level": "Not Visible",
        }