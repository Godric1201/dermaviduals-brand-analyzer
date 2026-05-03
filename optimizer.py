from analyzer import ask_ai


def generate_action_plan(
    brand,
    detailed_df,
    summary_df,
    raw_answers,
    report_language="English",
    category="category",
    market="target market",
    audience="target audience"
):
    summary_table = summary_df.to_string(index=False)

    trigger_pivot = detailed_df.pivot_table(
        index="prompt_category",
        columns="brand",
        values="visibility_score",
        aggfunc="mean"
    ).fillna(0).round(2)

    trigger_table = trigger_pivot.to_string()

    useful_columns = [
        "brand",
        "prompt_category",
        "prompt",
        "mentions",
        "estimated_rank",
        "visibility_score",
        "visibility_level",
        "is_target_brand"
    ]

    available_columns = [
        col for col in useful_columns
        if col in detailed_df.columns
    ]

    detailed_sample = (
        detailed_df[available_columns]
        .head(100)
        .to_string(index=False)
    )

    raw_answer_text = "\n\n".join(
        [
            f"""
Prompt Category: {item.get("prompt_category")}
Prompt: {item.get("prompt")}
AI Answer:
{item.get("answer")}
"""
            for item in raw_answers[:12]
        ]
    )

    prompt = f"""
You are a senior AI visibility strategist specializing in Generative Engine Optimization (GEO), AI recommendation behavior, and category visibility.

Your task:
Analyze AI-generated search visibility results and produce a decision-level AI visibility strategy report.

This is NOT a generic SEO report.
This is an AI recommendation intelligence report.

Context:
- Target brand: {brand}
- Market: {market}
- Audience: {audience}
- Category: {category}
- Business context: {category}, {market}, {audience}, category authority, high-intent use cases, comparison queries, local intent, decision-stage searches, and trust signals

Data:
Summary Table:
{summary_table}

Trigger-Level Visibility Table:
{trigger_table}

Detailed Prompt-Level Sample:
{detailed_sample}

Raw AI Answers Sample:
{raw_answer_text}

Important competitor rule:
- In sections 3, 4, 6, 7, 8, and 9, only use brands shown in the Summary Table as primary competitors.
- Do NOT list non-summary-table brands as dominant brands in Trigger-Level Mapping.
- If non-summary-table brands appear in raw AI answers, mention them only once in a short note called "Secondary Market Signals."
- Do NOT include La Roche-Posay, CeraVe, Avène, EltaMD, Obagi, SkinCeuticals, or SkinMedica as dominant competitors unless they appear in the Summary Table.
- The strategic focus must remain on {brand} versus the benchmark competitors in the Summary Table.

========================
OUTPUT STRUCTURE
========================

## 1. Executive Diagnosis

Explain the overall result in 4-6 bullets.

Must include:
- Whether {brand} appears or is absent
- Which Summary Table brands dominate AI recommendations
- Total mentions, average visibility score, prompts visible, and share of voice when available
- Whether the problem is awareness, positioning, semantic association, or content footprint
- What the most important strategic implication is

Use concrete numbers from the Summary Table.

---

## 2. AI Recommendation Logic

Explain how AI appears to choose brands or providers in the {category} category.

Analyze signals such as:
- category authority
- trusted experts, partners, reviewers, and decision-makers
- repeated online presence
- use-case fit
- comparison visibility
- {market} relevance
- credibility and trust signals

For each signal, use this format:
- Signal:
- Evidence from this analysis:
- Strategic implication for {brand}:

Each signal should cite at least one number from the Summary Table or Trigger-Level Visibility Table when possible.

Do not infer from general category knowledge alone. Tie the logic back to the Summary Table, Trigger-Level Visibility Table, Detailed Prompt-Level Sample, or Raw AI Answers Sample.

---

## 3. Trigger-Level Mapping

Analyze which prompt types or category themes trigger brand recommendations.

Use only the Trigger-Level Visibility Table, Detailed Prompt-Level Sample, and Summary Table when identifying dominant brands.
Do not infer dominant brands from general category knowledge.
Do not list non-summary-table brands as dominant brands.

For each relevant trigger, explain:
- Winning / dominant brands from the Summary Table
- Actual visibility scores from the Trigger-Level Visibility Table
- Whether {brand} appears
- What this means strategically

Include these themes if present in the data:
- high-intent use cases
- comparison queries
- local intent
- decision-stage searches
- trust signals
- {market} relevance
- {category} recommendations
- comparison queries

Format:

- Trigger:
  - Dominant brands and scores:
  - {brand} score/status:
  - Strategic implication:

Do not write broad claims like "dominates" unless supported by a score.

---

## 4. Competitive Positioning Map

Describe how AI appears to position major competitors.

Only use meaningful competitors from the Summary Table.

For each meaningful competitor, explain:
- AI-perceived role
- Total mentions
- Average visibility score
- Share of voice
- Strongest trigger categories, with actual scores
- Likely reason it is recommended
- Category need or authority territory it appears to own

Example style:
- iS Clinical:
  - AI-perceived role:
  - Evidence:
  - Owned territory:
  - Strategic implication:

Then explain where {brand} currently sits in this map using its actual numbers.

---

## 5. Visibility Barrier Diagnosis for {brand}

Explain why {brand} is missing or weak.

Do NOT just say "low SEO."

Diagnose AI-specific barriers:
- missing semantic association with high-value query themes
- weak market-relevant AI footprint
- insufficient third-party trust signals
- lack of comparison pages
- weak use-case mapping
- unclear category ownership
- weak {market} {category} association

Tie every major diagnosis to a number where possible, such as:
- total mentions
- prompts visible
- average visibility score
- trigger-level score
- share of voice

---

## 6. Brand Entry Strategy

Explain how {brand} can enter AI-generated recommendation lists.

Must include:
- The most realistic entry point
- The query territories to prioritize
- The brand associations to build
- The competitor territories to challenge first

Prioritize realistic entry routes over broad generic advice.

Only recommend territories supported by the prompt categories, trigger scores, summary results, or raw answer patterns.

Include actual trigger-level scores when choosing entry points.

---

## 7. Competitor Attack Strategy

Identify 2-4 competitors from the Summary Table that {brand} should target first.

For each:
- Why this competitor is the right target
- What AI territory they currently own
- Relevant visibility score or mention count
- What content angle can challenge them
- Example comparison or cluster content

Avoid vague suggestions.
Do not choose non-summary-table brands as main attack targets.

---

## 8. GEO Content Strategy

Recommend concrete content assets.

For each asset, include:
- Content title
- Target AI query
- Competitor to challenge
- Brand association to build
- Trigger/category score that justifies the asset
- Why it helps AI visibility

Include:
- comparison pages
- high-intent use-case content
- decision-stage content
- {market}-specific {category} content
- trusted expert, partner, reviewer, and decision-maker education content

Do not recommend broad SEO content unless it clearly supports AI recall, comparison presence, or semantic association.

---

## 9. 30 / 60 / 90 Day Execution Roadmap

Create a concrete roadmap.

For each phase:
- What to build
- Which query territory it targets
- Which Summary Table competitor it challenges
- Which current metric it is designed to improve
- Expected AI visibility effect

Avoid generic marketing actions such as influencer campaigns, webinars, email campaigns, partnerships, and broad website optimization unless directly connected to AI visibility.

If recommending partnerships or professional endorsements, explain exactly how they create:
- third-party mentions
- review language
- comparison pages
- AI-citable content
- professional recommendation signals

---

## 10. Secondary Market Signals

If non-summary-table brands appear in the raw AI answers, mention them briefly here only.

Explain:
- What they reveal about broader AI category bias
- Why they should not be treated as primary competitors in this report

If there are no relevant secondary signals, write:
"No major secondary market signals detected."

---

## 11. Final Strategic Conclusion

End with:
- The single biggest visibility problem
- The single best strategic entry point
- The next action the brand should take
- The 2-3 numeric metrics that should improve in the next benchmark

========================
NUMERIC EVIDENCE RULES
========================
- Use at least 10 specific numbers from the Summary Table or Trigger-Level Visibility Table.
- Every major section must include at least one concrete number when data is available.
- In Trigger-Level Mapping, include actual visibility scores for dominant brands.
- In Competitor Attack Strategy, include each competitor's relevant visibility score, total mentions, prompts visible, or share of voice.
- Do not write broad claims like "dominates", "strong", "weak", or "absent" unless supported by a number.
- If a trigger has all zero scores, say that clearly instead of inventing a winner.
- Do not make aggressive numeric performance promises.
- Numeric targets must be framed as directional next-benchmark goals, not guaranteed outcomes.
- Expected metric impact should reference total mentions, average visibility score, prompts visible, share of voice, or query intent visibility.
- Avoid claims that content will guarantee metric movement.
- If the target brand has 0 mentions, 0 prompts visible, or 0% share of voice:
  - use conservative next-benchmark targets
  - prefer "begin generating detectable mentions" over large numeric claims
  - prefer "visible in 1-3 relevant prompt categories" over broad visibility claims
  - avoid promising share of voice above 10% unless the benchmark data strongly supports it

========================
GENERAL RULES
========================
- Write in {report_language}
- Be analytical and specific
- Use actual data; do not invent results
- Avoid generic SEO advice
- Avoid generic marketing actions unless directly connected to AI visibility
- Focus on AI recommendation logic, semantic association, comparison content, professional third-party mentions, and query territory ownership
- Keep primary competitor discussion limited to Summary Table brands
- Be useful for a founder, marketer, or consultant making decisions
"""

    result = ask_ai(prompt, report_language)
    return result
