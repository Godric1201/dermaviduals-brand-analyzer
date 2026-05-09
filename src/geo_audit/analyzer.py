import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai(prompt, language="English"):
    """
    Main AI answer generator.
    Used for generating skincare recommendation answers and strategic reports.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"ERROR: {str(e)}"


def evaluate_brand_visibility(answer, brand):
    """
    Evaluates whether a specific brand appears in an AI answer.
    This function uses a separate evaluator prompt and should return JSON only.
    """
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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
"""
                },
                {
                    "role": "user",
                    "content": evaluation_prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        data = json.loads(result)

        return {
            "mentioned": bool(data.get("mentioned", False)),
            "position": data.get("position"),
            "visibility_score": int(data.get("visibility_score", 0)),
            "visibility_level": data.get("visibility_level", "Not Visible")
        }

    except Exception:
        return {
            "mentioned": False,
            "position": None,
            "visibility_score": 0,
            "visibility_level": "Not Visible"
        }