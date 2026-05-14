# Markdown Report Framework Audit

This audit compares `src/geo_audit/markdown_report.py` against the report quality framework.

The purpose is to identify structural gaps before changing renderer logic. The goal is not to patch one generated report, but to align the Markdown report generator with a reusable Recommendation Readiness report framework.

---

## Current Renderer Shape

`markdown_report.py` currently contains two major report paths:

1. **Zero-visibility path**
   - built through `_build_zero_visibility_markdown_report`
   - used when the target brand has no measurable visibility
   - already follows a Recommendation Readiness-style spine

2. **Non-zero visibility path**
   - built directly inside `build_executive_markdown_report`
   - used when the target brand has measurable visibility
   - still follows the older AI Visibility / GEO Audit structure

This creates an uneven report model: zero-visibility reports are more aligned with Recommendation Readiness, while non-zero reports still read more like general visibility audits.

---

## Alignment: Zero-Visibility Path

The zero-visibility path is mostly aligned with the framework.

Current aligned sections:

- Recommendation Readiness Verdict
- Brand Understanding Summary
- Who AI Retrieved Instead
- Why Those Brands Were Retrieved
- Target vs Retrieved Brand Gap
- First 3 Evidence Assets to Build
- Validation Plan
- Supporting Benchmark Data
- Methodology / Reliability Notes
- Optional Source-Grounded Evidence Summary

Current aligned behaviors:

- switches to first-detection strategy
- prioritizes candidate-set inclusion before share-of-voice growth
- separates benchmark signal from retrieval-role hypothesis
- uses validation caveats for AI-inferred probes
- includes future benchmark validation language
- avoids direct retrieval causality claims
- supports source evidence as optional validation context

This path should be treated as the reference implementation for future Recommendation Readiness report structure.

---

## Gaps: Non-Zero Visibility Path

The non-zero path is useful, but it is not fully aligned with the Recommendation Readiness framework.

Current sections:

- Report Overview
- Executive Summary
- Competitive Benchmark
- Trigger-Level Visibility Findings
- Top Brand Winners by Query Type
- Visibility Gap Diagnosis
- Strategic Priorities
- GEO Content Roadmap, when available
- 30 / 60 / 90 Day Roadmap
- Measurement Plan
- Recommended Next Step
- Methodology Notes
- Optional appendices

Framework gaps:

- No explicit Recommendation Readiness Verdict
- No retrieved-brand / visible-reference-brand interpretation section
- No retrieval-role section
- No target-vs-retrieved evidence gap section
- No first evidence assets section
- Source-grounded evidence summary is not currently integrated into the non-zero path
- Report title remains "AI Visibility Report" rather than "AI Recommendation Readiness Diagnosis"
- Diagnosis is more metric-led than evidence-gap-led

This does not mean the non-zero report is wrong. It means the non-zero path still reflects the older visibility-audit model and should be migrated toward the shared Recommendation Readiness spine.

---

## File Structure Risk

`markdown_report.py` is becoming too large and contains several different responsibilities:

- Markdown formatting helpers
- probe rendering
- zero-visibility report builder
- non-zero report builder
- source evidence integration
- generated text sanitation
- report assembly

This makes future framework changes harder to apply consistently.

A future refactor should split the renderer into smaller units.

Potential target modules:

- `markdown_report.py`
  - public entrypoint and orchestration
- `markdown_sections.py`
  - reusable section builders
- `markdown_zero_visibility_report.py`
  - zero-visibility Recommendation Readiness path
- `markdown_visibility_report.py`
  - non-zero visibility path
- `markdown_report_context.py`
  - shared report context, metrics, and prepared tables

The split should be behavior-preserving at first.

---

## Recommended Refactor Order

### Phase 1 — Add Structural Tests

Add tests that enforce the shared report spine without relying on exact full-section wording.

Priority tests:

- zero-visibility report includes Recommendation Readiness sections
- non-zero report includes mode, benchmark scope, validation, and methodology language
- Quick Test output stays non-client-deliverable
- prohibited claim patterns remain absent
- source evidence summary appears when source evidence payload is provided

### Phase 2 — Extract Section Builders

Extract reusable Markdown section builders without changing output behavior.

Recommended first extraction:

- report overview / verdict metadata
- methodology and reliability notes
- source evidence appendix integration
- validation language helpers

### Phase 3 — Align Non-Zero Path

Migrate the non-zero path toward the Recommendation Readiness spine.

Recommended changes:

- rename title to Recommendation Readiness Diagnosis or explicitly position AI Visibility as a subtype
- add a Recommendation Readiness Verdict section
- add visible-reference-brand interpretation where top competitor data is available
- add target-vs-visible-brand gap logic for non-zero reports
- add first evidence assets or evidence-priority section
- support source-grounded evidence summary in the non-zero path

### Phase 4 — DOCX Parity

After Markdown behavior is stable, align DOCX output with the same conceptual spine.

DOCX does not need identical formatting, but it should preserve:

- run mode clarity
- visibility state
- benchmark vs inference separation
- recommended evidence assets
- validation plan
- methodology limitations
- source evidence appendix parity

---

## Current Recommendation

Do not rewrite the renderer immediately.

The next implementation step should be structural tests and behavior-preserving extraction. The zero-visibility path should be used as the reference model, and the non-zero path should be migrated gradually toward the same framework.