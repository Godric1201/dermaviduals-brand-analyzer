# Report Section Contract

For the higher-level report quality model, see [`report-quality-framework.md`](report-quality-framework.md).

This document defines the section-level requirements for AI Recommendation Readiness reports.

It applies to Markdown and DOCX report outputs. Exact section titles may differ by output format, but the report must preserve the same diagnostic spine, evidence hierarchy, and claim-safety rules.

---

## Contract Principles

Every section must support the central report objective:

> Explain whether the target brand entered the tested AI recommendation candidate set, which brands appeared instead, what evidence gaps may explain the result, and what should be built or validated next.

Each section should separate:

- observed benchmark signal
- inferred retrieval driver
- source-grounded evidence, when available
- recommended action
- validation method

A section must not convert benchmark observations into definitive market, sales, consumer preference, clinical, or product-performance claims.

---

## Required Report Spine

Recommendation Readiness reports should follow this conceptual sequence:

1. Report context and run mode
2. Recommendation readiness verdict
3. Brand understanding or entity clarity signal
4. Retrieved brands / visible reference brands
5. Retrieval role interpretation
6. Target vs retrieved brand gap
7. First evidence assets to build
8. Validation plan
9. Supporting benchmark data
10. Methodology and reliability notes
11. Optional source-grounded evidence summary
12. Optional appendix material

This spine prevents reports from becoming generic marketing advice or raw benchmark tables.

---

## Report Context / Overview

### Purpose

Define the audit scope and run mode before presenting findings.

### Required Content

- target brand
- category
- market
- audience, when available
- run mode
- prompt count or prompt limit when relevant
- deliverable status
- benchmark scope caveat

### Allowed Wording

- "Run mode"
- "Benchmark scope"
- "Within the tested prompt set"
- "Development-only limited-prompt output" for Quick Test Mode

### Disallowed Claims

- client-deliverable positioning for Quick Test Mode
- broad market conclusions before presenting measured evidence
- hiding prompt limitations

---

## Recommendation Readiness Verdict

### Purpose

State whether the target brand entered the tested recommendation candidate set and define the first strategic objective.

### Required Content

- visibility state
- candidate-set status
- total mentions
- prompts visible
- share of voice
- average visibility score, when available
- strategy mode
- reliability level
- first objective

### Required Logic

If the target has zero mentions or zero prompt visibility, the verdict must switch to first-detection logic:

- first objective is candidate-set inclusion
- share-of-voice growth is secondary
- non-detection does not prove the model has no knowledge of the brand

### Allowed Wording

- "Not Detected"
- "First Detection Strategy"
- "Candidate-set inclusion"
- "The target was not retrieved in the tested recommendation candidate set"
- "This does not prove that AI systems have no knowledge of the brand"

### Disallowed Claims

- "AI does not know the brand" as a definitive fact
- "the brand is not trusted"
- "the market does not recognize the brand"
- guaranteed future inclusion
- guaranteed share-of-voice improvement

---

## Brand Understanding / Entity Clarity

### Purpose

Explain whether the model appears to understand the target brand, its category, market, or buyer context.

### Required Content

- brand understanding signal, when available
- category clarity signal
- market or audience alignment signal
- distinction between entity understanding and recommendation retrieval
- validation caveat

### Allowed Wording

- "AI-inferred"
- "partial recognition"
- "requires validation"
- "entity clarity"
- "recommendation retrieval risk"

### Disallowed Claims

- claiming brand awareness as a verified market fact
- treating model-generated brand understanding as ground truth
- unsupported claims about customer awareness

---

## Retrieved Brands / Visible Reference Brands

### Purpose

Show which brands appeared instead of the target and how they should be interpreted.

### Required Content

- retrieved brand name
- measured benchmark signal
- prompt context or query type where available
- inferred tier or reference role, when useful
- caveat that retrieved brands are benchmark-based references unless validated

### Allowed Wording

- "retrieved brand"
- "visible reference brand"
- "benchmark-based retrieved brand"
- "category anchor"
- "diagnostic reference"
- "not verified direct competitor"

### Disallowed Claims

- calling all retrieved brands direct competitors without validation
- "market leader" unless externally validated and user-provided
- "best brand"
- "customers prefer"
- "dominates the category"

---

## Retrieval Role Interpretation

### Purpose

Explain what role each retrieved brand appears to satisfy in the tested answers.

### Required Content

- inferred retrieval role
- benchmark pattern supporting the role
- implication for the target brand
- hypothesis label unless source-grounded validation exists

### Allowed Wording

- "appears to act as"
- "is consistent with"
- "may indicate"
- "benchmark-based retrieval hypothesis"
- "requires validation"

### Disallowed Claims

- "caused retrieval"
- "the model selected this brand because..."
- "proves why the competitor appeared"
- definitive causal source attribution

---

## Target vs Retrieved Brand Gap

### Purpose

Translate benchmark patterns and optional source evidence into target evidence gaps.

### Required Content

- retrieved brand or reference group
- observed benchmark signal
- inferred target gap
- evidence asset implication
- required validation
- indication of whether the gap is benchmark-based, source-grounded, or both

### Allowed Wording

- "may lack"
- "gap signal"
- "evidence gap to validate"
- "source-grounded validation context"
- "required validation"

### Disallowed Claims

- "the target lacks credibility" as fact
- "competitors are objectively better"
- "this proves the reason for non-detection"
- unsupported business or market conclusions

---

## First Evidence Assets to Build

### Purpose

Prioritize concrete evidence assets designed to test candidate-set inclusion and recommendation readiness.

### Required Content

Each recommended asset must include:

- what to build
- why it matters
- target retrieval driver
- target prompt groups or query contexts
- validation method

### Allowed Wording

- "build AI-citable evidence"
- "intended to strengthen target-brand association"
- "designed for future benchmark validation"
- "check for candidate-set inclusion"
- "first measurable inclusion"

### Disallowed Claims

- guaranteed AI mentions
- guaranteed ranking gains
- guaranteed share-of-voice growth
- guaranteed revenue, sales, or conversion impact
- fixed timelines for AI inclusion

---

## Strategic Priorities

### Purpose

Translate visibility gaps into broader GEO priorities when the report includes a strategic planning layer.

### Required Content

- priority level
- query territory
- competitor or retrieved-brand focus
- recommended action
- intended benchmark influence
- validation method or future measurement focus

### Allowed Wording

- "intended benchmark influence"
- "target query territory"
- "recommended for future benchmark validation"
- "may improve measurable visibility in future runs"

### Disallowed Claims

- guaranteed ranking outcomes
- guaranteed share-of-voice gains
- unsupported revenue or sales impact
- generic marketing promises disconnected from benchmark evidence

---

## GEO Content Roadmap

### Purpose

Map evidence gaps and retrieval risks to content assets and execution timing.

### Required Content

- priority
- query intent
- content asset
- target association
- competitor or retrieved-brand signal
- evidence needed
- expected benchmark influence
- suggested timing

### Allowed Wording

- "evidence needed"
- "target association"
- "future benchmark validation"
- "intended benchmark influence"

### Disallowed Claims

- unsupported business impact
- unsupported product efficacy
- generic campaign promises
- guaranteed future ranking outcomes

---

## 30 / 60 / 90 Day Roadmap

### Purpose

Organize recommended actions into a phased execution plan.

### Required Content

- 30-day action
- 60-day action
- 90-day action
- target metric or directional benchmark focus
- competitor or retrieved-brand focus where relevant
- validation dependency

### Allowed Wording

- "begin improving"
- "build AI-citable evidence"
- "prepare for future benchmark comparison"
- "directional benchmark improvement"

### Disallowed Claims

- exact future numeric targets unless explicitly user-provided
- guaranteed visibility gains
- guaranteed business outcomes
- fixed timelines for model behavior changes

---

## Validation Plan

### Purpose

Define how to test whether evidence-building actions create measurable benchmark progress.

### Required Content

- what to rerun
- what counts as first progress
- what does not count as proof
- prompt groups to prioritize
- snapshot or future benchmark comparison guidance

### Allowed Wording

- "rerun comparable prompts"
- "check for first measurable inclusion"
- "validate whether the target enters the candidate set"
- "compare benchmark snapshots over time"

### Disallowed Claims

- treating one mention as durable visibility
- treating hallucinated or unrelated mentions as progress
- promising a fixed timeline
- guaranteeing future inclusion

---

## Supporting Benchmark Data

### Purpose

Provide the measured data behind the diagnosis.

### Required Content

- competitive benchmark table where available
- top brand winners by query type where available
- mentions
- prompts visible
- share of voice
- visibility score or state
- prompt-category context where available

### Allowed Wording

- "measured benchmark signal"
- "strongest measured brand signal"
- "within this benchmark run"
- "supporting data"

### Disallowed Claims

- replacing diagnosis with raw metrics only
- unsupported market share claims
- unsupported customer preference claims

---

## Measurement Plan

### Purpose

Define what should be monitored in the next benchmark cycle.

### Required Content

- current state
- next benchmark evaluation focus
- metrics to monitor
- comparison-over-time reminder
- reliability caveat

### Allowed Wording

- "evaluate whether visibility is beginning to improve"
- "track whether the visibility gap is narrowing"
- "compare benchmark snapshots over time"

### Disallowed Claims

- "achieve X% share of voice" unless clearly marked as a planning assumption
- guaranteed metric movement
- sales, revenue, or conversion claims

---

## Methodology / Reliability Notes

### Purpose

Explain the scope and limitations of the benchmark.

### Required Content

- benchmark is based on AI-generated answers
- visibility is calculated from mentions, estimated ranking, and prompt-level appearance
- share of voice reflects distribution of mentions among tracked competitors
- distinction between observed benchmark signal, inferred retrieval driver, and source-grounded evidence
- results are not market share, sales performance, consumer survey, or clinical evaluation
- results should be re-run over time

### Allowed Wording

- stable deterministic language
- clear limitation language
- benchmark-specific wording
- evidence hierarchy language

### Disallowed Claims

- removing disclaimers
- weakening limitations
- presenting output as definitive market research
- implying source evidence proves retrieval causality

---

## Source-Grounded Evidence Summary

### Purpose

Provide optional source-evidence validation context for target-vs-retrieved evidence gaps.

### Required Content

- source evidence coverage by brand
- target-vs-retrieved evidence gaps
- confidence levels where available
- supported retrieval drivers
- first source evidence assets to build
- causality caveat

### Allowed Wording

- "source evidence gap"
- "accepted source evidence"
- "validation context"
- "does not prove retrieval causality"
- "retrieved brands have evidence of this type"

### Disallowed Claims

- "this source caused retrieval"
- "the model used this source"
- "this proves why the competitor appeared"
- treating source evidence as verified competitive intelligence without analyst validation

---

## Brand Intelligence Appendix

### Purpose

Provide diagnostic interpretation of recommendation drivers, competitor associations, positioning gaps, and evidence opportunities.

### Required Content

- recommendation drivers
- competitor advantage signals
- target brand understanding
- positioning gap analysis
- distinction between tracked competitors and AI-discovered diagnostic references

### Allowed Wording

- "AI-inferred"
- "diagnostic"
- "not included in visibility scoring"
- "requires validation"
- "tracked competitors included in scoring"

### Disallowed Claims

- treating diagnostic inferences as scored visibility results
- presenting AI-discovered brands as tracked competitors
- claiming diagnostic content as market truth

---

## Quick Test Mode Contract

Quick Test Mode outputs must always remain clearly marked as development-only.

### Required Content

- "TEST VERSION ONLY"
- "Quick Test Mode - Not Client Deliverable"
- "Development-only limited-prompt output"
- prompt limit shown in report overview
- limited prompt set caveat

### Allowed Wording

- "directional QA output"
- "limited prompt set"
- "not a complete benchmark"
- "workflow testing"

### Disallowed Claims

- client-ready conclusions
- broad competitive conclusions
- strong future numeric targets
- market-wide claims