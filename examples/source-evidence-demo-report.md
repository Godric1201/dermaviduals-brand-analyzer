# Source Evidence Demo Report

> Fictional, deterministic demo output. This report is generated from local fixture data only.
> It does not use OpenAI, Streamlit, web search, scraping, or live client data.

## Demo Context

| Field | Value |
|---|---|
| Target brand | Example Infrastructure Co. |
| Category | Data center infrastructure consulting and project support |
| Market | Germany |
| Audience | Enterprise infrastructure buyers |
| Retrieved brands | Reference Brand A, Reference Brand B, Reference Brand C |

## 1. Source Evidence Coverage

This section summarizes accepted source evidence available for the target and retrieved brands.

| Brand | Total items | Accepted items | High-confidence items | Evidence type count | Evidence types |
| --- | --- | --- | --- | --- | --- |
| Example Infrastructure Co. | 2 | 2 | 0 | 2 | Entity Evidence, Market Evidence |
| Reference Brand A | 2 | 2 | 2 | 2 | Comparison Evidence, Proof / Trust Evidence |
| Reference Brand B | 2 | 2 | 1 | 2 | Authority / Association Evidence, Offering / Use-Case Evidence |
| Reference Brand C | 2 | 2 | 0 | 2 | Recency / Freshness Evidence, Third-Party Corroboration |

## 2. Target vs Retrieved Evidence Gap

This section identifies evidence types that appear for retrieved brands but are missing for the target brand.

| Missing evidence type | Retrieved brands with evidence | Source count | Highest confidence | Supported retrieval drivers |
| --- | --- | --- | --- | --- |
| Comparison Evidence | Reference Brand A | 1 | High | Comparison anchor |
| Offering / Use-Case Evidence | Reference Brand B | 1 | High | Planning / consulting authority |
| Proof / Trust Evidence | Reference Brand A | 1 | High | Trust / premium reference |
| Authority / Association Evidence | Reference Brand B | 1 | Medium | Planning / consulting authority |
| Recency / Freshness Evidence | Reference Brand C | 1 | Medium | Current market relevance |
| Third-Party Corroboration | Reference Brand C | 1 | Medium | Trust / premium reference |

These gaps are source-evidence gaps to validate. They are not proof that specific sources caused AI retrieval.

## 3. First Evidence Assets to Build

**Priority 1 - Comparison Evidence**
- Why it matters: Retrieved brands have source evidence for this type, while the target does not.
- Retrieved-brand signal: Reference Brand A
- Supported retrieval drivers: Comparison anchor
- Recommended asset: Build comparison and alternatives evidence that explains when the brand is a relevant option.
- Validation: Build or improve the evidence asset, then rerun comparable recommendation prompts to check for candidate-set inclusion.

**Priority 2 - Offering / Use-Case Evidence**
- Why it matters: Retrieved brands have source evidence for this type, while the target does not.
- Retrieved-brand signal: Reference Brand B
- Supported retrieval drivers: Planning / consulting authority
- Recommended asset: Build offering and use-case evidence that explains where the brand is relevant.
- Validation: Build or improve the evidence asset, then rerun comparable recommendation prompts to check for candidate-set inclusion.

**Priority 3 - Proof / Trust Evidence**
- Why it matters: Retrieved brands have source evidence for this type, while the target does not.
- Retrieved-brand signal: Reference Brand A
- Supported retrieval drivers: Trust / premium reference
- Recommended asset: Build proof and trust evidence such as case studies, certifications, project examples, or credible third-party support.
- Validation: Build or improve the evidence asset, then rerun comparable recommendation prompts to check for candidate-set inclusion.

## 4. Source Evidence Appendix

### Example Infrastructure Co.

| Evidence type | Source type | Confidence | Status | Source title | Domain |
| --- | --- | --- | --- | --- | --- |
| Entity Evidence | Owned Source | Medium | Observed | About Example Infrastructure Co. | example-infrastructure.test |
| Market Evidence | Owned Source | Low | Needs Review | Germany infrastructure support | example-infrastructure.test |

### Reference Brand A

| Evidence type | Source type | Confidence | Status | Source title | Domain |
| --- | --- | --- | --- | --- | --- |
| Comparison Evidence | Service / Category Page | High | Observed | Data center infrastructure alternatives | reference-a.test |
| Proof / Trust Evidence | Case Study / Reference Project | High | Observed | Reference data center projects | reference-a.test |

### Reference Brand B

| Evidence type | Source type | Confidence | Status | Source title | Domain |
| --- | --- | --- | --- | --- | --- |
| Offering / Use-Case Evidence | Service / Category Page | High | Observed | Data center planning support | reference-b.test |
| Authority / Association Evidence | Partner Page | Medium | Observed | Infrastructure partner ecosystem | reference-b.test |

### Reference Brand C

| Evidence type | Source type | Confidence | Status | Source title | Domain |
| --- | --- | --- | --- | --- | --- |
| Third-Party Corroboration | Third-Party Directory | Medium | Observed | Reference Brand C directory profile | directory.test |
| Recency / Freshness Evidence | News / Press Mention | Medium | Observed | Recent data center project update | reference-c.test |

## 5. Methodology Notes

This demo distinguishes observed source evidence from inference and recommended action.

- Observed source evidence: fixture records with source type, confidence, and validation status.
- Source-supported evidence gap: evidence type present for retrieved brands but missing for the target.
- Recommended action: evidence asset to build and validate in a future benchmark.
- Boundary: this report does not claim causality between a source and AI retrieval.
