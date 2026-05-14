# Report Quality Framework

This framework defines the report-generation rules for AI Recommendation Readiness Diagnosis outputs.

The goal is to make every generated report consistent, evidence-aware, mode-safe, and commercially useful across different brands, categories, markets, and run modes.

This framework applies to:

- Markdown executive reports
- DOCX executive reports
- demo report fixtures
- source-grounded evidence summaries
- future report renderer and prompt changes

---

## 1. Core Report Objective

Every report must answer one central question:

> Why did the target brand appear, fail to appear, or appear weakly in AI recommendation-style answers, and what evidence should be built or validated next?

The report should not only describe visibility metrics. It should translate benchmark signals into a clear recommendation-readiness diagnosis.

A good report must show:

- whether the target brand entered the tested recommendation candidate set
- which brands were retrieved instead
- what retrieval roles those brands appear to satisfy
- what target evidence gaps may explain the missing or weak visibility
- which evidence assets should be built first
- how progress should be validated in a comparable future benchmark

---

## 2. Evidence Hierarchy

Reports must keep evidence levels separate.

### 2.1 Observed Benchmark Signal

Observed benchmark signals are measured directly from the benchmark run.

Examples:

- target brand mentions
- prompts visible
- share of voice
- average visibility score
- retrieved brands
- query categories where competitors appeared

Allowed wording:

- "The benchmark recorded..."
- "Within the tested prompt set..."
- "The generated answers included..."
- "The target was not retrieved in this run..."

Disallowed wording:

- "The market prefers..."
- "Customers choose..."
- "The brand is objectively weaker..."
- "AI does not know the brand..." as a definitive fact

### 2.2 Inferred Retrieval Driver

Inferred retrieval drivers are cautious hypotheses based on benchmark patterns.

Examples:

- comparison anchor
- trust / premium reference
- planning / consulting authority
- professional authority
- local market relevance

Allowed wording:

- "may indicate"
- "appears to act as"
- "is consistent with"
- "suggests a possible retrieval role"

Disallowed wording:

- "proves why the model selected..."
- "caused retrieval"
- "is the reason AI recommended..."
- "confirms competitive superiority"

### 2.3 Source-Grounded Evidence

Source-grounded evidence is optional validation context from accepted source records.

It can support evidence-gap diagnosis, but it must not be presented as proof of retrieval causality.

Allowed wording:

- "source evidence supports this gap for validation"
- "retrieved brands have evidence of this type"
- "the target lacks this evidence type in the accepted source records"
- "these gaps should be validated in future benchmark runs"

Disallowed wording:

- "this source caused retrieval"
- "the model used this source"
- "this source proves why the competitor appeared"

### 2.4 Recommended Action

Recommended actions are evidence-building hypotheses.

They should be specific, testable, and tied to future benchmark validation.

Required structure:

- what to build
- why it matters
- target retrieval driver
- prompt groups or query contexts affected
- validation method

Disallowed wording:

- guaranteed AI mentions
- guaranteed ranking gains
- guaranteed share-of-voice growth
- revenue, sales, conversion, clinical, or product-performance promises

---

## 3. Run Mode Rules

### 3.1 Quick Test Mode

Quick Test Mode is for development and QA only.

Every Quick Test Mode report must clearly communicate:

- not client-deliverable
- limited prompt coverage
- exploratory or directional reliability
- no broad market conclusions
- no strong strategic claims
- no fixed performance promises

Required ideas:

- "TEST VERSION ONLY"
- "Quick Test Mode - Not Client Deliverable"
- "Development-only limited-prompt output"
- "limited prompt set"

Quick Test Mode may be used to verify:

- workflow execution
- report structure
- export behavior
- early directional visibility signal
- UI and regression behavior

Quick Test Mode must not be positioned as a complete audit.

### 3.2 Full Report Mode

Full Report Mode can produce portfolio or client-style outputs, but still must preserve benchmark limitations.

Full Report Mode reports may include:

- fuller recommendation-readiness diagnosis
- retrieved-brand role interpretation
- evidence asset prioritization
- validation plan
- source-grounded evidence summary when available
- benchmark snapshot export

Full Report Mode must still avoid:

- definitive market conclusions
- unsupported causal claims
- guaranteed future performance
- sales, revenue, or clinical claims

---

## 4. Zero-Visibility Report Rules

When the target brand has zero mentions or is not retrieved, the report must switch to a first-detection strategy.

The primary objective is:

> Candidate-set inclusion before share-of-voice growth.

A zero-visibility report must include:

- clear "Not Detected" or equivalent visibility state
- explanation that non-detection does not prove the model has no knowledge of the brand
- retrieved brands or category anchors that appeared instead
- target-vs-retrieved evidence gap
- first evidence assets to build
- validation plan focused on first measurable inclusion

A zero-visibility report must not:

- over-focus on share-of-voice growth
- imply the brand is commercially weak
- imply the brand is not trusted
- promise a timeline for AI inclusion
- treat retrieved brands as verified direct competitors unless validated

---

## 5. Required Report Spine

Every Recommendation Readiness report should follow this conceptual spine, even if the exact section titles differ between Markdown and DOCX:

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

This spine exists to prevent reports from becoming generic marketing advice or raw benchmark tables.

---

## 6. Section-Level Requirements

### Recommendation Readiness Verdict

Must answer:

- Is the target detected?
- What is the visibility state?
- What is the first strategic objective?
- How reliable is the run?

Must include:

- target brand
- market
- category
- audience when available
- run mode
- mentions
- prompts visible
- share of voice
- candidate-set status

### Retrieved Brands Section

Must answer:

- Which brands appeared instead?
- What measured signal did each produce?
- Should they be treated as competitors, references, anchors, or diagnostic retrieved brands?

Must avoid:

- calling all retrieved brands direct competitors without validation
- implying retrieved brands are objectively superior

### Retrieval Role Section

Must answer:

- What role does each retrieved brand appear to satisfy?
- What benchmark pattern supports that interpretation?
- What does that imply for the target?

Must label role explanations as hypotheses unless source-grounded validation exists.

### Target vs Retrieved Gap Section

Must answer:

- What does the target appear to lack relative to retrieved brands?
- Is that gap benchmark-based, source-grounded, or both?
- What validation is required?

### First Evidence Assets Section

Each recommended asset must include:

- what to build
- why it matters
- target retrieval driver
- relevant prompt groups
- validation method

### Validation Plan

Must define:

- what to rerun
- what counts as first progress
- what does not count as proof
- how to compare future results

### Methodology / Reliability Notes

Must preserve:

- benchmark scope
- AI answer variability
- prompt-set limitations
- distinction from market research
- distinction from sales, revenue, consumer survey, or product-quality claims

---

## 7. Source Evidence Integration Rules

Source evidence should be treated as a validation layer, not as the primary benchmark result.

Source evidence can be used to:

- compare accepted evidence coverage by brand
- identify target-vs-retrieved evidence gaps
- prioritize first evidence assets
- support analyst review
- prepare future source discovery automation

Source evidence must not be used to claim:

- model source attribution
- retrieval causality
- proof that a specific source caused a model answer
- verified competitive intelligence without analyst validation

JSON and CSV source evidence inputs are analyst-controlled workflow formats. They are not the final client-facing input experience.

---

## 8. Claim-Safety Rules

Reports must not claim or imply:

- guaranteed AI visibility improvement
- guaranteed ranking improvement
- guaranteed share-of-voice growth
- guaranteed sales, revenue, conversion, or lead generation impact
- consumer preference
- clinical efficacy
- product superiority
- market leadership
- model source usage or retrieval causality

Reports should use:

- benchmark-specific language
- source-evidence validation language
- directional recommendation language
- future validation language

---

## 9. Output Quality Acceptance Criteria

A report is product-acceptable when it satisfies all of the following:

- The run mode is clear.
- The target visibility state is clear.
- Benchmark observations are separated from inference.
- Inferred retrieval roles are labeled as hypotheses unless validated.
- Source evidence is separated from benchmark evidence.
- Recommended assets are specific and testable.
- Validation steps are included.
- Methodology limitations are preserved.
- Claim-safety rules are not violated.
- The report avoids generic marketing filler.
- The report remains useful even when the target has zero visibility.

---

## 10. Implementation Guidance

Future renderer, prompt, and DOCX changes should be evaluated against this framework.

Recommended implementation sequence:

1. Add structure-level tests for required sections.
2. Add mode-specific tests for Quick Test and Full Report language.
3. Add claim-safety tests for disallowed wording.
4. Align Markdown report generation with the framework.
5. Align DOCX report generation with the framework.
6. Use real or fictional outputs only as validation samples, not as one-off patch targets.