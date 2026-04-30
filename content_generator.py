from analyzer import ask_ai


def generate_level_2_content_pack(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_table,
    detailed_table,
    report_language="English"
):
    prompt = f"""
You are a senior GEO content strategist.

Generate an actionable Level 2 content asset pack designed to improve the AI visibility of the target brand.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Primary Competitors:
{", ".join(competitors)}

Summary Table:
{summary_table}

Detailed Prompt-Level Table:
{detailed_table}

Context:
The goal is to make {brand} more likely to appear in AI-generated answers for professional skincare, clinic-grade skincare, sensitive skin, barrier repair, post-treatment care, corneotherapy, and Hong Kong skincare recommendations.

Competitor rule:
- Prioritize the primary competitors listed above.
- Do not make La Roche-Posay, CeraVe, Avène, EltaMD, Obagi, or SkinCeuticals the main comparison targets unless they are part of the primary competitor list.
- Comparison content should be fair, factual, and not attack competitors.

Create a content pack with the following sections.

Return the answer as clear markdown sections.

---

## 1. SEO Blog Post

Create a full blog post draft.

Requirements:
- Title
- Meta description
- H1
- Short introduction
- H2 sections
- Practical advice
- Naturally position {brand}
- Mention professional skincare, sensitive skin, barrier repair, corneotherapy, and Hong Kong market relevance
- Do NOT make exaggerated medical claims
- Do NOT overpromote the brand
- Make the article helpful and credible

Suggested angle:
"Best Professional Skincare Brands for Sensitive Skin and Barrier Repair in Hong Kong"

---

## 2. Google Maps / Clinic Review Strategy

Create a review strategy for clinics, skin therapists, and professional partners.

Include:
- What types of authentic reviews to encourage
- Review phrases that help AI associate {brand} with key concepts
- 10 suggested review prompts
- Concepts to mention:
  - sensitive skin
  - barrier repair
  - post-treatment care
  - professional skincare
  - long-term skin improvement
  - Hong Kong humidity
  - skin therapist recommendation
  - corneotherapy

Important:
Do NOT suggest fake reviews.
Focus only on authentic customer experience prompts.

---

## 3. Social Posts

Create 8 short social media post ideas.

For each post:
- Hook
- Caption idea
- Target AI association
- Suggested CTA

Focus on:
- barrier repair
- sensitive skin
- corneotherapy
- post-treatment recovery
- professional skincare
- Hong Kong climate

---

## 4. FAQ Content

Create FAQ content optimized for AI answer engines.

Include at least 10 FAQs.

Each FAQ should include:
- Question
- Answer
- Target query / AI association

Focus on questions people might ask ChatGPT, Google AI Overview, or Perplexity.

---

## 5. Comparison Page Outline

Create comparison-page outlines that help {brand} enter AI recommendation lists.

Use competitors from the primary competitor list where relevant.

Include comparison ideas such as:
- {brand} vs PCA Skin
- {brand} vs iS Clinical
- {brand} vs ZO Skin Health
- {brand} vs Biologique Recherche
- Corneotherapy skincare vs traditional clinic-grade skincare

For each comparison page:
- Page title
- Target query
- Positioning angle
- Key sections
- How to fairly compare without attacking competitors
- Why this helps GEO visibility

---

## 6. AI Visibility Content Cluster

Create a content cluster map.

Include:
- Pillar page
- Supporting articles
- FAQ pages
- Comparison pages
- Review / testimonial themes

The content cluster should help {brand} become associated with:
- sensitive skin
- barrier repair
- corneotherapy
- professional skincare
- clinic-grade skincare
- post-treatment care
- Hong Kong skincare

---

Rules:
- Write in {report_language}
- Be specific and practical
- Avoid generic SEO advice
- Do not make unsupported medical claims
- Do not say competitors are bad
- Focus on building AI-search visibility and brand association
"""

    result = ask_ai(prompt, report_language)

    return {
        "seo_blog": extract_section(result, "## 1. SEO Blog Post", "## 2. Google Maps / Clinic Review Strategy"),
        "review_strategy": extract_section(result, "## 2. Google Maps / Clinic Review Strategy", "## 3. Social Posts"),
        "social_posts": extract_section(result, "## 3. Social Posts", "## 4. FAQ Content"),
        "faq_content": extract_section(result, "## 4. FAQ Content", "## 5. Comparison Page Outline"),
        "comparison_outline": extract_section(result, "## 5. Comparison Page Outline", "## 6. AI Visibility Content Cluster"),
    }


def extract_section(text, start_marker, end_marker=None):
    if not text:
        return ""

    start = text.find(start_marker)

    if start == -1:
        return text

    if end_marker:
        end = text.find(end_marker, start + len(start_marker))
        if end != -1:
            return text[start:end].strip()

    return text[start:].strip()