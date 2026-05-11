# Methodology

This document explains how the AI Brand Visibility GEO Audit tool measures brand visibility inside AI-generated recommendation answers.

The goal is not to estimate market share, SEO traffic, revenue, brand sentiment, or customer satisfaction. The goal is to benchmark whether a target brand appears in AI-generated answers when users ask recommendation-style questions, and how that visibility compares with tracked competitors.

---

## 1. What the Benchmark Measures

The benchmark measures visibility in AI-generated recommendation answers.

It evaluates:

- Whether a tracked brand is mentioned

- How often the brand is mentioned

- Where the brand appears in the generated answer

- Whether it appears across multiple prompt categories

- How the target brand compares with tracked competitors

- Which query types produce stronger or weaker visibility

- Which competitors dominate specific recommendation contexts

The benchmark is designed for Generative Engine Optimization (GEO), AI SEO research, competitor visibility analysis, and brand positioning diagnostics.

---

## 2. Core Inputs

Each audit run starts with five main inputs:

| Input | Purpose |

|---|---|

| Target Brand | The brand being audited |

| Category | The product, service, or market category being tested |

| Market | The geographic or market context |

| Audience | The intended buyer, user, or evaluator segment |

| Competitors | The tracked brands used for comparison |

These inputs shape the benchmark prompts and determine which brands are included in scoring.

Only the target brand and tracked competitors are included in share-of-voice scoring. AI-discovered brands may appear in diagnostic sections, but they are not scored unless they are selected as tracked competitors before the run.

---

## 3. Prompt Strategy

The tool uses recommendation-style prompts designed to simulate how users ask AI systems for brand, product, service, or vendor recommendations.

Prompt categories may include:

- Best options

- Local recommendations

- Audience-specific recommendations

- Alternatives

- Comparisons

- Decision-stage queries

- Use-case-specific queries

- Trust and authority queries

The exact prompt set depends on the run mode and prompt generation workflow.

Prompt design is intended to test whether the target brand is likely to appear in AI-generated recommendation contexts, not whether it ranks in traditional search results.

---

## 4. Quick Test Mode vs Full Report Mode

### Quick Test Mode

Quick Test Mode is a development and QA mode.

It uses a limited number of prompts so the workflow can be tested quickly and cheaply. It is useful for verifying:

- API key configuration

- Prompt generation

- AI answer collection

- Scoring behavior

- Report generation

- DOCX / Markdown exports

- Snapshot exports

Quick Test Mode should not be interpreted as a complete benchmark. Results may be directionally useful for debugging, but they are not intended as client-ready analysis.

### Full Report Mode

Full Report Mode runs the complete benchmark workflow and is the intended mode for meaningful analysis.

Use Full Report Mode for:

- Portfolio demonstrations

- More complete visibility analysis

- Competitive benchmarking

- Strategy and roadmap generation

- Snapshot tracking over time

---

## 5. Brand Mention Detection

The benchmark checks whether the target brand and tracked competitors appear in AI-generated answers.

Mention detection is used to calculate:

- Total mentions

- Prompt-level visibility

- Share of voice

- Visibility score inputs

A brand that is never mentioned receives zero visibility for that run.

Because LLM outputs can vary, mention detection should be interpreted as a benchmark signal, not an absolute truth about market awareness.

---

## 6. Visibility Score

The visibility score is a benchmark metric designed to capture more than simple mention count.

It reflects three main signals:

1\. **Mention presence**  

&#x20;  Whether the brand appears in the answer.

2\. **First appearance position**  

&#x20;  Whether the brand appears early or late in the generated answer.

3\. **Estimated rank within the answer**  

&#x20;  Whether the brand appears as a stronger recommendation or a weaker/later option.

A higher visibility score means the brand appeared more prominently in the tested AI answers.

A score of zero means the brand was not measurably visible in the tested prompt set.

Visibility score is not a measure of revenue, market share, customer preference, search volume, or clinical/product quality.

---

## 7. Total Mentions

Total mentions count how many times a tracked brand appears across the benchmark answers.

A higher mention count means the brand was recalled more often by the AI model within the tested prompt set.

Mention count should be interpreted together with visibility score and prompt-level visibility. A brand may be mentioned often but appear in weaker positions, or mentioned less often but in stronger recommendation positions.

---

## 8. Prompts Visible

Prompts visible measures how many tested prompts included the brand in the AI-generated answer.

This helps distinguish between:

- A brand that appears repeatedly in one context

- A brand that appears across multiple query categories

- A brand that does not appear at all

Prompts visible is especially useful for identifying whether the target brand has broad AI visibility or only narrow association with one query type.

---

## 9. Share of Voice

Share of voice measures the target brand’s share of total tracked brand mentions.

It is calculated within the selected competitor set for that run.

Example interpretation:

- If the target brand has 0% share of voice, it was not mentioned while at least one competitor was.

- If one competitor has 100% share of voice, it was the only tracked brand mentioned in that benchmark run.

- In Quick Test Mode, share-of-voice results should be treated as limited-sample signals.

Share of voice is not market share. It only reflects AI answer presence within the tested prompt set.

---

## 10. Trigger-Level Visibility

Trigger-level visibility shows which brands appear in specific query categories.

For example:

- Best options

- Local recommendations

- Audience-specific recommendations

- Comparison queries

- Decision-stage searches

This helps identify:

- Which query types the target brand wins

- Which query types competitors dominate

- Which prompt categories produce no target-brand visibility

- Where content or evidence gaps may exist

Trigger-level findings are useful for GEO strategy because they connect benchmark results to specific content opportunities.

---

## 11. Top Brand Winners by Query Type

The tool identifies which brand has the strongest visibility score within each query category.

This is not a universal ranking of brand quality. It is a benchmark-specific signal showing which tracked brand performed best in a tested prompt category.

If the target brand does not appear in any query category, it indicates that the brand currently lacks measurable visibility in that prompt set.

---

## 12. Brand Intelligence

Brand Intelligence is a diagnostic layer that analyzes benchmark answers and related brand-positioning signals.

It may identify:

- Recurring recommendation drivers

- Competitor-owned associations

- Trust signals

- Market or category demand signals

- Missing target-brand associations

- Content opportunities

- Evidence gaps

Brand Intelligence should be interpreted as a strategic diagnostic layer, not as primary scoring. The scoring is based on tracked brand visibility in benchmark answers.

---

## 13. GEO Content Roadmap

The GEO Content Roadmap translates visibility gaps into content and evidence-building opportunities.

It may recommend assets such as:

- Category guides

- Local recommendation pages

- Comparison pages

- Use-case-specific landing pages

- Expert commentary

- Review or testimonial collection

- Evidence pages

- Partner or authority pages

These recommendations are intended to influence future benchmark performance by making the target brand more relevant, more credible, and more AI-citable for specific query territories.

The roadmap does not guarantee future AI visibility improvement. It provides hypotheses that should be tested in later benchmark runs.

---

## 14. Benchmark Snapshots

Benchmark snapshots allow runs to be saved and compared over time.

Snapshots may include:

- Target brand

- Category

- Market

- Audience

- Competitor set

- Prompt categories

- Prompt count

- Run mode

- Summary metrics

- Brand Intelligence data

- API usage summary

- Optional raw answer evidence

Snapshot comparison can help evaluate whether visibility changes after content, PR, or positioning work.

---

## 15. Recommended Interpretation

Use the benchmark as a diagnostic signal.

Strong interpretation:

- “The target brand did not appear in the tested AI recommendation prompts.”

- “Competitor X had stronger measured visibility in this benchmark run.”

- “The target brand has weak measurable association with local recommendation queries.”

- “Future content should build evidence around specific query territories.”

Avoid overclaiming:

- “The target brand has no market awareness.”

- “Competitor X is objectively better.”

- “This proves customer preference.”

- “This predicts sales performance.”

- “This is equivalent to SEO ranking or market share.”

---

## 16. Limitations

The benchmark has important limitations:

- LLM outputs can vary between runs.

- Results depend on prompt design, model behavior, and competitor selection.

- The tool measures AI answer visibility, not business performance.

- The benchmark does not validate factual claims about product quality.

- The tool does not measure search volume or website traffic.

- Quick Test Mode is not a full benchmark.

- AI-discovered brands are diagnostic unless explicitly tracked.

- A low score may indicate weak AI recall, weak public evidence, narrow prompt coverage, or model-specific behavior.

The benchmark should be used as one input into a broader brand, content, SEO, and market analysis workflow.

---

## 17. Practical Use

A typical workflow is:

1\. Run a Full Report benchmark for the target brand and competitor set.

2\. Review visibility, share of voice, and trigger-level gaps.

3\. Identify competitor-owned query territories.

4\. Build content and evidence assets around missing associations.

5\. Re-run the benchmark after content changes or PR activity.

6\. Compare benchmark snapshots over time.

The goal is to create a repeatable measurement loop for AI visibility improvement.

