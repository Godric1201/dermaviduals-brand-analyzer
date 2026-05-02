from analyzer import ask_ai


ROADMAP_COLUMNS = [
    "Priority",
    "Query Intent",
    "Content Asset",
    "Target Association",
    "Competitor / Market Signal",
    "Evidence Needed",
    "Expected Metric Impact",
    "Suggested Timing",
]


def _dataframe_preview(df, max_rows=40):
    if df is None:
        return "No data provided."

    if hasattr(df, "empty") and df.empty:
        return "No data provided."

    if hasattr(df, "head") and hasattr(df, "to_string"):
        return df.head(max_rows).to_string(index=False)

    return str(df)


def _brand_intelligence_preview(brand_intelligence):
    if not brand_intelligence:
        return "No Brand Intelligence output provided."

    return f"""
Recommendation Drivers:
{brand_intelligence.get("recommendation_drivers", "")}

AI-Inferred Target Brand Understanding:
{brand_intelligence.get("target_brand_understanding", "")}

Positioning Gap Analysis:
{brand_intelligence.get("positioning_gap_analysis", "")}
""".strip()


def build_geo_content_roadmap_prompt(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
    brand_intelligence,
    query_intent_categories,
):
    columns = " | ".join(ROADMAP_COLUMNS)

    return f"""
You are creating a GEO Content Roadmap for a consulting deliverable.

This is a strategic execution plan. It is not part of visibility scoring, share of voice, or benchmark calculations.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Tracked Competitors:
{", ".join(competitors)}

Query Intent Categories:
{", ".join(query_intent_categories)}

Summary Data:
{_dataframe_preview(summary_df)}

Detailed Prompt-Level Data:
{_dataframe_preview(detailed_df)}

Brand Intelligence:
{_brand_intelligence_preview(brand_intelligence)}

Task:
Create an actionable GEO Content Roadmap that links query intent, content assets, trust signals, competitor or market signals, evidence needs, and expected metric impact.

Return only a markdown table with these exact columns:
{columns}

Rules:
- Use concise consulting-ready wording.
- Include 5 to 8 roadmap rows.
- Tie each row to a query intent or strategic opportunity.
- Content Asset should name a concrete asset, page, PR angle, review initiative, comparison page, FAQ, or evidence-building item.
- Evidence Needed should describe proof points, trust signals, reviews, third-party references, expert input, or AI-citable sources.
- Expected Metric Impact should reference visibility, mentions, prompts visible, share of voice, query intent coverage, or target-brand association.
- Do not invent unsupported facts.
- Do not create or modify scores.
- Do not include narrative before or after the table.
""".strip()


def generate_geo_content_roadmap(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
    brand_intelligence,
    query_intent_categories,
    report_language="English",
):
    prompt = build_geo_content_roadmap_prompt(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        summary_df=summary_df,
        detailed_df=detailed_df,
        brand_intelligence=brand_intelligence,
        query_intent_categories=query_intent_categories,
    )

    return ask_ai(prompt, report_language)
