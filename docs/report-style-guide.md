# Report Style Guide

For the higher-level report quality model, see [`report-quality-framework.md`](report-quality-framework.md).

This guide defines language standards for AI Recommendation Readiness Diagnosis reports.

The goal is to make reports professional, cautious, commercially useful, and consistent across brands, categories, markets, and run modes.

---

## Core Principle

Reports must describe results as **AI visibility benchmark signals**, not as definitive market facts.

The tool evaluates how brands appear in AI-generated answers within a tested prompt set. It does not measure real market share, sales, consumer preference, clinical quality, product performance, or business performance.

Every report should preserve four levels of evidence:

1. **Observed benchmark signal** — what appeared in the tested AI-generated answers.
2. **Inferred retrieval driver** — a cautious hypothesis about why a brand may have appeared.
3. **Source-grounded evidence** — optional validation context from accepted source records.
4. **Recommended action** — an evidence-building step to test in future benchmark cycles.

Do not collapse these levels into one claim.

---

## Evidence Hierarchy Language

### Observed Benchmark Signal

Use when describing measured benchmark output.

Preferred phrases:

- "Within the tested prompt set..."
- "The benchmark recorded..."
- "The generated answers included..."
- "The target brand was not retrieved in this run..."
- "The strongest measured benchmark signal came from..."
- "The target produced limited measurable visibility in this benchmark."

Avoid:

- "AI does not know the brand."
- "The market does not recognize the brand."
- "Customers do not choose the brand."
- "The brand lacks credibility."
- "The brand is not trusted."

### Inferred Retrieval Driver

Use when explaining why a retrieved brand may have appeared.

Preferred phrases:

- "may indicate"
- "appears to act as"
- "is consistent with"
- "suggests a possible retrieval role"
- "benchmark-based retrieval hypothesis"
- "requires validation"

Avoid:

- "caused retrieval"
- "the model selected this brand because..."
- "this proves why the competitor appeared"
- "the source caused the answer"
- "AI recommended this brand because it is better"

### Source-Grounded Evidence

Use when optional source evidence records are available.

Preferred phrases:

- "source evidence gap"
- "accepted source evidence"
- "validation context"
- "retrieved brands have evidence of this type"
- "the target lacks this evidence type in the accepted source records"
- "does not prove retrieval causality"

Avoid:

- "this source caused retrieval"
- "the model used this source"
- "this proves why the competitor appeared"
- "verified competitive intelligence" unless separately validated
- "source evidence confirms the model's reasoning"

### Recommended Action

Use when translating gaps into next steps.

Preferred phrases:

- "build AI-citable evidence"
- "intended to strengthen target-brand association"
- "designed for future benchmark validation"
- "check for candidate-set inclusion"
- "validate whether measurable visibility improves"
- "prepare evidence assets for comparable future benchmark runs"

Avoid:

- "will improve AI rankings"
- "will increase share of voice"
- "guarantees more mentions"
- "will drive sales"
- "will improve conversion"
- "will generate revenue"

---

## Recommendation Readiness Tone

Reports should be written as diagnostic consulting outputs.

The tone should be:

- analytical
- cautious
- specific
- evidence-oriented
- commercially useful
- structured
- validation-focused

The tone should not be:

- promotional
- absolute
- speculative without labels
- overly technical
- generic
- salesy
- alarmist

Preferred framing:

- "The immediate objective is candidate-set inclusion."
- "The next step is to build evidence that can be validated in future benchmark runs."
- "The report should be read as a recommendation-readiness diagnosis, not a market performance report."

Avoid:

- "This brand is losing the market."
- "Competitors are better."
- "AI prefers the competitor."
- "The brand must do X to win AI search."
- "This guarantees visibility recovery."

---

## Zero-Visibility Language

When the target brand is not detected, the report must switch to first-detection language.

Preferred phrases:

- "Not Detected"
- "First Detection Strategy"
- "Candidate-set inclusion"
- "The target was not retrieved in the tested recommendation candidate set."
- "The first objective is not share-of-voice growth; it is candidate-set inclusion."
- "Non-detection does not prove that AI systems have no knowledge of the brand."

Avoid:

- "The brand has no AI presence."
- "AI does not know the brand."
- "The brand is invisible everywhere."
- "The brand lacks trust."
- "The brand is not credible."
- "The brand has failed in AI search."

Zero-visibility reports must prioritize:

- entity clarity
- category association
- market relevance
- comparison eligibility
- trust / proof evidence
- first measurable inclusion
- future validation

---

## Quick Test Mode Language

Quick Test Mode is development and QA mode only.

Required meaning:

- not client-deliverable
- limited prompt coverage
- directional reliability
- not a complete benchmark
- no broad market conclusions
- no fixed performance promises

Approved phrases:

- "TEST VERSION ONLY"
- "Quick Test Mode - Not Client Deliverable"
- "Development-only limited-prompt output"
- "limited prompt set"
- "directional QA output"
- "not a complete benchmark"
- "workflow testing"

Avoid in Quick Test Mode:

- client-ready conclusions
- broad competitive conclusions
- exact future numeric targets
- market-wide claims
- strong strategic recommendations detached from prompt coverage

---

## Full Report Mode Language

Full Report Mode may use more complete consulting-style language, but it must still preserve benchmark limitations.

Approved phrases:

- "Full Report Mode"
- "client-style report output"
- "portfolio-ready demo output"
- "source-supported directional diagnosis"
- "future comparable benchmark validation"

Avoid:

- treating the report as definitive market research
- implying the benchmark is exhaustive
- claiming measured AI visibility equals business performance
- claiming source evidence proves retrieval causality

---

## Retrieved Brand Language

Retrieved brands should be described carefully.

Preferred phrases:

- "retrieved brand"
- "visible reference brand"
- "benchmark-based retrieved brand"
- "category anchor"
- "diagnostic reference"
- "tracked competitor" only when the brand was configured as tracked
- "not verified direct competitor" when competitor status has not been validated

Avoid:

- "direct competitor" unless validated or user-provided
- "market leader" unless externally validated and user-provided
- "best brand"
- "category winner" as a market claim
- "customer preferred brand"
- "dominates the category"

---

## Recommended Asset Language

Recommended assets must be concrete and testable.

Each recommendation should answer:

- what to build
- why it matters
- which retrieval driver it supports
- which prompt groups or query contexts it targets
- how to validate it later

Preferred asset wording:

- "canonical category entity page"
- "proof and trust page"
- "comparison and alternatives page"
- "market relevance page"
- "use-case evidence page"
- "project proof page"
- "third-party corroboration asset"
- "decision-stage buyer guide"

Avoid vague recommendations such as:

- "improve SEO"
- "create more content"
- "do more marketing"
- "increase brand awareness"
- "build authority" without specifying evidence type and validation method

---

## Claim-Safety Rules

Never claim or imply:

- guaranteed AI visibility improvement
- guaranteed ranking improvement
- guaranteed share-of-voice growth
- guaranteed sales, revenue, conversion, or lead generation impact
- consumer preference
- clinical efficacy
- product superiority
- market leadership
- model source usage or retrieval causality

Use benchmark-safe alternatives:

| Risky wording | Safer wording |
| --- | --- |
| "will improve rankings" | "is intended to strengthen future benchmark visibility" |
| "AI trusts this brand" | "the brand appeared in trust-oriented prompt contexts" |
| "competitors are better" | "retrieved brands showed stronger benchmark signals in this run" |
| "this source caused retrieval" | "this source evidence supports a gap to validate" |
| "customers prefer this brand" | "the benchmark retrieved this brand more frequently in tested prompts" |
| "this will increase sales" | "this may support future recommendation-readiness validation" |

---

## Source Evidence Positioning

Source evidence JSON and CSV inputs are analyst-controlled workflow formats.

They support:

- deterministic demo fixtures
- internal source evidence review
- spreadsheet-style analyst workflows
- report validation and QA
- future semi-automated source discovery workflows

They are not the final client-facing input experience.

When discussing source evidence, use:

- "accepted source evidence"
- "source evidence record"
- "analyst-controlled input"
- "validation context"
- "evidence gap"
- "future source discovery automation"

Avoid:

- "client must upload JSON"
- "client must prepare CSV"
- "source evidence proves the answer"
- "source evidence identifies the exact model source"

---

## Methodology and Limitations

Reports must preserve methodology limitations.

Required ideas:

- The report is an AI visibility benchmark.
- It is not a market share report.
- It is not a sales performance report.
- It is not a consumer survey.
- It is not a clinical or product efficacy evaluation.
- Results may vary between model runs.
- Results should be tracked over comparable future benchmark cycles.
- Source evidence supports validation but does not prove retrieval causality.

---

## Final Output Standard

A report is acceptable when it is:

- clear about run mode
- clear about target visibility state
- clear about benchmark scope
- explicit about observed vs inferred evidence
- careful with source evidence claims
- specific about recommended evidence assets
- explicit about future validation
- free from unsupported market, sales, clinical, or causal claims
- useful even when the target has zero visibility

A report is not acceptable when it is:

- generic marketing advice
- a raw metric dump without diagnosis
- overconfident about causality
- unclear about Quick Test limitations
- vague about what to build next
- missing validation logic