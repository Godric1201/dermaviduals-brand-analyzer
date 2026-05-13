# Product Roadmap

This roadmap describes how the project is evolving from an AI visibility benchmark into a product-grade AI Recommendation Readiness diagnosis tool.

The current focus is not broad web scraping or UI complexity. The priority is to make the report logic, evidence model, and demo outputs credible enough for productized consulting, portfolio review, and future commercial use.

---

## Current Product Positioning

The tool answers one core question:

> Why does AI recommend competitors instead of your brand, and what evidence should you build first?

It does this by combining:

- recommendation-style prompt benchmarking
- target-brand visibility scoring
- retrieved-brand diagnosis
- retrieval role interpretation
- source-grounded evidence gap analysis
- first evidence assets to build
- validation planning for future benchmark runs

---

## Completed Foundations

### 1. Recommendation Readiness Report

The formal Markdown report now supports a zero-visibility diagnosis flow with:

- Recommendation Readiness verdict
- brand understanding summary
- retrieved-brand diagnosis
- retrieval role explanation
- target vs retrieved brand gap
- first evidence assets to build
- validation plan
- methodology and reliability notes
- supporting benchmark data

### 2. Retrieved Brand Role Diagnosis

Retrieved brands are classified through deterministic role scoring rather than generic market-fit matching.

The report can distinguish signals such as:

- comparison anchor
- trust / premium reference
- technical authority
- planning / consulting authority
- market-relevant provider
- budget / value option

### 3. Source-Grounded Evidence Model

The project includes a local source evidence model for manually supplied evidence records.

It supports:

- evidence item normalization
- validation
- source type tracking
- confidence levels
- validation status
- target vs retrieved brand evidence comparison
- evidence gap aggregation

### 4. Source Evidence Demo

The repository includes a deterministic fictional source evidence demo that runs locally without:

- OpenAI calls
- Streamlit
- web search
- scraping
- live client data

### 5. Formal Markdown Integration

The formal Markdown report can optionally include a source-grounded evidence summary section.

This section adds:

- source evidence coverage
- target vs retrieved evidence gap
- first source evidence assets to build
- non-causality caution wording

---

## Near-Term Roadmap

### Phase 1 — Product-Grade Report Output

Goal: make the report feel credible enough for a consulting deliverable or product demo.

Planned work:

- refine public demo reports
- improve first evidence asset wording
- improve source evidence summary readability
- add more realistic fictional demo cases
- add before / after benchmark snapshot examples
- keep report language cautious and evidence-based

Success criteria:

- a GitHub visitor can understand the product from the README and demo reports
- a recruiter or potential client can see a concrete use case within 60 seconds
- the report clearly separates observed benchmark signals, inferred retrieval drivers, source evidence, and recommended actions

### Phase 2 — Manual Source Evidence Workflow

Goal: make source-grounded diagnosis usable without automated scraping.

Planned work:

- support manual CSV or JSON source evidence import
- preview source evidence coverage in the app
- allow source evidence inclusion in Markdown export
- validate source evidence records before report generation
- document the fixture schema

Success criteria:

- a user can provide source evidence manually
- the app can generate a source-supported Recommendation Readiness report
- invalid evidence inputs fail safely with clear messages

### Phase 3 — Demo and Portfolio Maturity

Goal: make the repository compelling for GitHub visitors, internship applications, and product conversations.

Planned work:

- add more realistic fictional industry examples
- add screenshots of the Streamlit workflow
- add a concise architecture diagram
- add sample benchmark snapshots
- add a short product walkthrough
- clarify commercial use cases

Success criteria:

- the repository reads like a focused product prototype, not a loose experiment
- demo artifacts show concrete business value
- the project can be used as a portfolio anchor for AI, consulting, and industrial digitalization roles

### Phase 4 — Streamlit Integration

Goal: connect the source evidence workflow into the app after the report logic is stable.

Planned work:

- upload source evidence JSON or CSV
- show validation errors in the UI
- preview source evidence coverage
- include source evidence in exported Markdown reports
- later add DOCX parity

Success criteria:

- source evidence can be used from the UI without manual code changes
- Markdown export remains the first supported output
- DOCX support follows only after Markdown behavior is stable

### Phase 5 — Optional Research Automation

Goal: explore source discovery only after the manual workflow is stable.

Possible future work:

- guided source checklist generation
- source candidate collection
- domain-level evidence summaries
- citation review workflow
- limited source quality scoring

Non-goals for now:

- broad web scraping
- uncontrolled automated claims
- black-box source attribution
- claims that a source caused AI retrieval

---

## Product Principles

### Local-first

The tool should remain usable locally with a user-owned API key and deterministic fixture demos.

### Evidence-aware

The report should distinguish:

- observed benchmark signal
- inferred retrieval driver
- source-grounded evidence
- recommended action

### Causality-safe

The tool should not claim that a specific source caused AI retrieval.

Preferred wording:

- source-supported evidence gap
- benchmark-based hypothesis
- validation context
- candidate-set inclusion to test

Avoided wording:

- this source caused retrieval
- this will make AI recommend the brand
- this proves market leadership
- this guarantees share-of-voice growth

### Productized consulting fit

The output should be useful for:

- GEO audits
- AI visibility diagnostics
- competitor retrieval analysis
- content strategy
- consulting deliverables
- internal marketing strategy
- portfolio demonstration

---

## Current Priority

The current priority is to mature the public-facing product narrative and demo outputs before adding more UI complexity.

The next best improvements are:

1. make the README and demo reports immediately understandable
2. add product roadmap and methodology clarity
3. add screenshots or visual walkthroughs
4. add manual source evidence import only after report behavior is stable
