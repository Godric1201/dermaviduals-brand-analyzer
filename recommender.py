from analyzer import ask_ai


def generate_recommendations(
    brand,
    category,
    market,
    audience,
    summary_table,
    detailed_table,
    report_language="English"
):
    prompt = f"""
You are a senior Generative Engine Optimization (GEO) strategist.

Create a concise tactical recommendation section based on the actual AI visibility data below.

This section should be practical and action-oriented.
Do NOT repeat a long strategic diagnosis. The deeper diagnosis will appear later in the Level 3 Strategy Report.

Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Summary Table:
{summary_table}

Detailed Prompt-Level Table:
{detailed_table}

Competitor rule:
- Prioritize competitors shown in the Summary Table.
- If other brands appear indirectly, treat them only as secondary market signals.
- Do not make La Roche-Posay, CeraVe, Avène, EltaMD, Obagi, or SkinCeuticals the main competitors unless they appear in the Summary Table with meaningful visibility.

Your task:
Generate a concise GEO action section for improving {brand}'s visibility in AI-generated professional skincare recommendations.

Structure your response exactly like this:

## Strategic GEO Recommendations for {brand}

### 1. Immediate Visibility Problem
- 2-3 bullets only.
- Mention whether {brand} is missing, weak, or visible.
- Mention the strongest visible competitors from the Summary Table.

### 2. Priority Query Territories
Create a table with these columns:
- Query Territory
- Why It Matters
- Competitor to Challenge
- Recommended Content Angle

Include 5-6 territories only.

Focus on:
- sensitive skin
- barrier repair
- post-treatment care
- corneotherapy
- clinic-grade skincare
- Hong Kong professional skincare

### 3. Content Assets to Build First
Create a table with:
- Content Asset
- Target AI Query
- Competitor to Challenge
- AI Association to Build

Recommend 5-7 assets only.

### 4. 30-Day GEO Actions
List 5 concrete actions that can be started within 30 days.

Rules:
- Be concise.
- Be data-driven.
- Do not give generic SEO advice.
- Avoid broad marketing actions such as influencer campaigns or email campaigns unless clearly tied to AI visibility.
- Focus on AI recall, semantic association, comparison content, query territory ownership, and third-party professional mentions.
- Write in {report_language}.
"""

    return ask_ai(prompt, report_language)