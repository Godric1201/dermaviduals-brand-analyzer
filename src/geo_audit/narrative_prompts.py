import pandas as pd


NUMERIC_GROUNDING_RULES = """
Numeric grounding rules:
- Use only numeric metrics explicitly provided in the input tables/context.
- Do not invent mention counts, visibility scores, ranks, percentages, or positions.
- Do not treat character positions, first_position, or internal analysis positions as mention counts.
- If a metric is not provided, describe it qualitatively instead of assigning a number.
- When citing competitor performance, use only: total_mentions, average_visibility_score, prompts_visible, share_of_voice_percent, or visibility_score by prompt category if explicitly provided.
- Avoid unsupported phrases like "mention count 320", "visibility score of 320", or "100% visibility" unless that exact metric is provided.
- If uncertain, say "the benchmark indicates stronger visibility" rather than fabricating a number.
""".strip()


APPENDIX_C_LANGUAGE_CONTRACT = """
Appendix C language contract:
- Frame reasoning as prompt-set signal, not consumer behavior.
- Use the required labels: Benchmark signal behind visibility, Observed query territory signal, and Strategic implication for the target brand.
- Avoid consumer-behavior claims such as consumers are actively seeking, preferred choice, trusted among consumers, ready to purchase, and go-to option.
- Describe findings as within the tested prompt set and tied to measured visibility.
""".strip()


APPENDIX_D_LANGUAGE_CONTRACT = """
Appendix D language contract:
- Use "compete against brands with stronger measured visibility" as the strategic frame.
- Avoid replacement, attack, go-to brand, dominates, trusted option among consumers, and effectively compete in the market as framing language.
- Use "content angle to test in future benchmark cycles" instead of guaranteed positioning.
- Keep competitor names and useful diagnostic content, but frame them as benchmark-visible signals.
""".strip()


APPENDIX_E_LANGUAGE_CONTRACT = """
Appendix E language contract:
- Use the heading "Benchmark-Visible Associations Missing or Weak".
- Avoid old AI-recommendation rejection headings.
- Do not describe consumers as excluding, rejecting, or failing to connect with the brand.
- Use "the tested answers did not surface..." or "the benchmark did not detect..." for missing associations.
- Avoid unsupported market interpretation and describe gaps as benchmark-visible signals.
""".strip()


def _compact_table(df, columns, rename_map, max_rows=50):
    if df is None or getattr(df, "empty", False):
        return "No data provided."

    available_columns = [col for col in columns if col in df.columns]
    if not available_columns:
        return "No data provided."

    compact_df = df[available_columns].head(max_rows).copy().rename(columns=rename_map)
    return compact_df.to_string(index=False)


def build_narrative_summary_context(summary_df, max_rows=20):
    return _compact_table(
        summary_df,
        [
            "brand",
            "total_mentions",
            "average_visibility_score",
            "prompts_visible",
            "share_of_voice_percent",
        ],
        {
            "brand": "Brand",
            "total_mentions": "Total Mentions",
            "average_visibility_score": "Average Visibility Score",
            "prompts_visible": "Prompts Visible",
            "share_of_voice_percent": "Share of Voice %",
        },
        max_rows=max_rows,
    )


def build_narrative_top_brands_context(top_brands_df, max_rows=25):
    return _compact_table(
        top_brands_df,
        ["prompt_category", "brand", "visibility_score"],
        {
            "prompt_category": "Query Type",
            "brand": "Winning Brand",
            "visibility_score": "Visibility Score",
        },
        max_rows=max_rows,
    )


def build_narrative_detailed_context(detailed_df, max_rows=50):
    return _compact_table(
        detailed_df,
        [
            "prompt_category",
            "prompt",
            "brand",
            "mentions",
            "visibility_score",
            "visibility_level",
            "is_target_brand",
        ],
        {
            "prompt_category": "Query Type",
            "prompt": "Prompt",
            "brand": "Brand",
            "mentions": "Mentions",
            "visibility_score": "Visibility Score",
            "visibility_level": "Visibility Level",
            "is_target_brand": "Is Target Brand",
        },
        max_rows=max_rows,
    )


def build_ai_decision_explanation_prompt(
    brand,
    category,
    market,
    top_brands_df,
    detailed_df,
):
    return f"""
You are analyzing AI-generated {category} brand or provider recommendations in {market}.

Based on the data below, explain the benchmark signals behind each top brand's measured visibility.

Focus on:
- What signal triggers the brand
- What authority the brand has
- What makes it preferred over others
- What query type it wins
- Whether it is associated with high-intent use cases, comparison queries, local intent, decision-stage searches, or trust signals

{NUMERIC_GROUNDING_RULES}

{APPENDIX_C_LANGUAGE_CONTRACT}

Top brands per category:
{build_narrative_top_brands_context(top_brands_df)}

Detailed benchmark context:
{build_narrative_detailed_context(detailed_df)}

Explain in this format:

- Category: X
- Winning Brand: Y
- Benchmark signal behind visibility:
- Observed query territory signal:
- Strategic implication for {brand}:
""".strip()


def build_replacement_strategy_prompt(
    brand,
    category,
    market,
    audience,
    top_brands_df,
    summary_df,
    detailed_df,
    raw_answers,
):
    return f"""
You are a senior GEO strategist.

Based on the AI visibility data below, explain how {brand} can compete against brands with stronger measured visibility in AI-generated {category} recommendations in {market}.

Target brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

{NUMERIC_GROUNDING_RULES}

Brands with stronger measured visibility per category:
{build_narrative_top_brands_context(top_brands_df)}

{APPENDIX_D_LANGUAGE_CONTRACT}

Summary benchmark metrics:
{build_narrative_summary_context(summary_df)}

Detailed benchmark context:
{build_narrative_detailed_context(detailed_df)}

Raw AI answers:
{str(raw_answers[:10])}

For each major brand with stronger measured visibility, explain:

1. What observed query territory signal appears connected to the competitor
2. What benchmark signal appears behind the competitor's measured visibility
3. What {brand} should do to compete
4. What content should be created
5. What query or keyword cluster {brand} should target

Use this format:

## Competitor: [Brand Name]

- Observed query territory signal:
- Benchmark signal behind visibility:
- Weakness or opening:
- {brand} competitive positioning strategy:
- Content angle to test in future benchmark cycles:
- Target queries:

Focus on generic GEO territories such as high-intent use cases, comparison queries, local intent, decision-stage searches, and trust signals.
Be specific. Avoid generic SEO advice.
""".strip()


def build_gap_analysis_prompt(
    brand,
    category,
    market,
    audience,
    competitors,
    summary_df,
    detailed_df,
):
    return f"""
You are analyzing AI brand association patterns.

Based on the data below, explain:

1. What concepts each competitor is associated with
2. What concepts {brand} is missing
3. What benchmark-visible associations are missing or weak for {brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Focus on generic GEO concepts such as high-intent use cases, comparison queries, local intent, decision-stage searches, and trust signals.

{NUMERIC_GROUNDING_RULES}

{APPENDIX_E_LANGUAGE_CONTRACT}

Competitors:
{", ".join(competitors)}

Summary benchmark metrics:
{build_narrative_summary_context(summary_df)}

Detailed benchmark context:
{build_narrative_detailed_context(detailed_df)}

Use this heading:
## Benchmark-Visible Associations Missing or Weak

Answer in structured bullet points.
""".strip()
