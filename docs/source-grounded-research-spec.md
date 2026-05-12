# Source-Grounded Research Spec

## 1. Product Purpose

The source-grounded research module is a future product layer for AI Recommendation Readiness Diagnosis.

Its purpose is to upgrade benchmark-based retrieval hypotheses into source-grounded evidence analysis. Benchmark output can show what AI retrieved. Source-grounded research should help explain what public evidence may support those retrieval patterns.

The module should:

- Identify observable public evidence that may explain why retrieved brands are more retrievable.
- Identify which evidence assets the target brand is missing.
- Compare target evidence against retrieved-brand evidence without claiming causality.
- Support better Recommendation Readiness reporting by distinguishing observed benchmark signal, AI-inferred retrieval driver, source-supported claim, and recommended action.

This module must not claim that a specific source caused AI retrieval. It should state that public evidence may support retrievability and should be validated through future benchmark runs.

## 2. Scope Boundaries

In scope for the future module:

- Official website pages
- Service/category pages
- Case studies / reference projects
- Partner pages
- Certifications / awards / associations
- Third-party directories
- News / press mentions
- Structured data / schema / sameAs
- Review or community platforms where relevant

Out of scope for the first version:

- Paid SEO crawling at scale
- Private databases
- Scraping behind login
- Legal claims
- Review manipulation
- Guaranteed AI ranking or visibility improvement
- Replacing benchmark validation

The first version should prioritize explainable source evidence over broad crawling volume.

## 3. Research Targets

The module should support research for four target groups.

### Target Brand

The brand being audited. Research should identify what public evidence already supports entity clarity, category fit, market relevance, offerings, trust, comparison eligibility, and structured data.

Use when:

- The target is Not Detected.
- The target has weak or partial visibility.
- The report needs to prioritize the first evidence assets to build.

### Retrieved Brands

Brands that appeared in the benchmark answer set while the target did not, or appeared more strongly than the target.

Use when:

- The report needs to explain why AI may retrieve other brands.
- Retrieval role hypotheses need source-grounded support.
- The target-vs-retrieved gap needs stronger evidence.

### Tracked Competitors

Brands explicitly provided by the user for comparison and scoring.

Use when:

- The user wants a controlled competitor benchmark.
- Share-of-voice scoring depends on the competitor set.
- The report should compare target evidence against known market alternatives.

### Optional Category Anchors

Highly visible brands that may not be direct peers but shape the category answer set.

Use when:

- The model retrieves global or category-famous brands.
- Market Relevance Probe suggests global-default risk.
- The report needs to distinguish peer competitors from aspirational references or category anchors.

## 4. Source Types

### Owned Sources

Examples:

- Brand website pages
- About pages
- Service/category pages
- Product pages
- Case studies
- Resource pages

Reliability considerations:

- Useful for direct brand claims.
- May be incomplete, outdated, or promotional.
- Should be corroborated where possible with third-party sources.

### Third-Party Corroboration

Examples:

- Directories
- Partner pages
- Industry profiles
- Association listings
- Analyst or trade references

Reliability considerations:

- Stronger than owned claims when independent and specific.
- Quality varies by source authority and editorial standards.
- Must not be overread as endorsement unless the source clearly supports it.

### Structured Data

Examples:

- Organization schema
- Product/service schema
- sameAs links
- Local business data
- Consistent entity naming

Reliability considerations:

- Useful for machine-readable entity clarity.
- Does not prove quality or market strength.
- Should be assessed for consistency and relevance.

### Market / Community Evidence

Examples:

- Review platforms
- Community forums
- Local business directories
- User-generated references
- Relevant social/community mentions

Reliability considerations:

- Useful where community proof matters for the category.
- May be noisy, biased, outdated, or irrelevant.
- Should not be used for review manipulation or unsupported quality claims.

### News / Freshness Evidence

Examples:

- Press mentions
- Product announcements
- Project announcements
- Awards coverage
- Event participation

Reliability considerations:

- Useful for recency and external corroboration.
- Needs freshness dates.
- News mentions do not automatically prove market leadership or buyer preference.

## 5. Source-Grounded Evidence Taxonomy

### Entity Evidence

What it means:

Evidence that the brand is a recognizable entity with consistent naming, description, and identity.

Example sources:

- About page
- Organization profile
- Directory listing
- Structured organization data

Retrieval driver it may support:

- Basic entity recognition
- Candidate-set inclusion

### Category Evidence

What it means:

Evidence that connects the brand to the target category or industry.

Example sources:

- Category landing page
- Service overview
- Industry profile
- Product/service schema

Retrieval driver it may support:

- Category fit
- Recommendation eligibility

### Market Evidence

What it means:

Evidence that the brand is relevant to the specified geography, region, or market context.

Example sources:

- Market landing page
- Local office/location page
- Regional case study
- Local partner page

Retrieval driver it may support:

- Local market provider
- Market-specific retrieval

### Offering / Use-Case Evidence

What it means:

Evidence that explains what the brand offers and which buyer needs or use cases it serves.

Example sources:

- Service pages
- Product pages
- Use-case pages
- Buyer guides

Retrieval driver it may support:

- Technical infrastructure provider
- Niche specialist
- Planning / consulting authority

### Proof / Trust Evidence

What it means:

Evidence that supports credibility, experience, quality, or reliability.

Example sources:

- Case studies
- Reference projects
- Certifications
- Awards
- Testimonials
- Independent reviews where relevant

Retrieval driver it may support:

- Trust / premium reference
- Shortlist eligibility

### Comparison Evidence

What it means:

Evidence that explains how the brand compares with alternatives, when it is a relevant option, and what criteria buyers should use.

Example sources:

- Alternatives pages
- Comparison pages
- Buyer criteria pages
- Decision guides

Retrieval driver it may support:

- Comparison anchor
- Alternative prompt eligibility

### Third-Party Corroboration

What it means:

Independent public evidence that confirms the brand, category, market, offering, or proof claims.

Example sources:

- Directories
- Partner pages
- Association pages
- Trade publications
- Industry profiles

Retrieval driver it may support:

- Entity confidence
- Category confidence
- Trust and market relevance

### Structured Data Evidence

What it means:

Machine-readable evidence that clarifies the brand entity and its relationships.

Example sources:

- Organization schema
- Local business schema
- Product/service schema
- sameAs links
- Consistent naming across pages

Retrieval driver it may support:

- Entity clarity
- Disambiguation
- Category and market association

### Recency / Freshness Evidence

What it means:

Evidence that the brand is active, current, and recently associated with the category or market.

Example sources:

- Recent news
- Recent case studies
- Updated service pages
- Recent partner announcements

Retrieval driver it may support:

- Current market relevance
- Active offering signal

### Authority / Association Evidence

What it means:

Evidence that the brand is connected to credible organizations, industry groups, partners, certifications, or expert ecosystems.

Example sources:

- Association memberships
- Certification pages
- Partner ecosystem pages
- Award pages
- Expert panels or industry events

Retrieval driver it may support:

- Trust / premium reference
- Planning / consulting authority
- Category legitimacy

## 6. Evidence Object Schema

Each evidence item should use a structured schema.

| Field | Definition |
|---|---|
| brand | Brand the evidence item belongs to. |
| evidence_type | Evidence taxonomy label, such as Market Evidence or Comparison Evidence. |
| source_url | URL where the evidence was found. |
| source_title | Title of the source page or document. |
| source_domain | Domain of the source. |
| source_type | Source category, such as owned source, third-party directory, partner page, news, or structured data. |
| excerpt_or_summary | Short excerpt or summary of the observed evidence. |
| observed_claim | The specific claim or fact pattern visible in the source. |
| supported_retrieval_driver | Retrieval role or evidence gap the source may support. |
| confidence | High, Medium, Low, or Insufficient. |
| freshness_date | Publication, update, or observed freshness date when available. |
| validation_status | Status such as observed, needs review, stale, conflicting, or rejected. |
| notes | Analyst notes, caveats, or follow-up requirements. |

The schema should preserve the distinction between observed source content and analyst interpretation.

## 7. Evidence Quality and Confidence

Confidence levels:

- High: Specific, current, directly relevant evidence from an authoritative source.
- Medium: Relevant evidence with some limitation, such as partial specificity, older date, or weaker authority.
- Low: Weak, vague, stale, or only indirectly relevant evidence.
- Insufficient: No usable evidence or evidence that cannot support the claimed retrieval driver.

Factors:

- Source type
- Source authority
- Directness of claim
- Freshness
- Consistency across sources
- Relevance to target market/category/audience
- Whether evidence is owned or third-party

Confidence should be assigned to evidence quality, not to guaranteed AI retrieval outcomes.

## 8. Competitive Gap Logic

The module should compare:

- Retrieved brand evidence
- Target brand evidence
- Missing target evidence
- First evidence assets to build
- Evidence quality and confidence

Suggested logic:

1. Group evidence by brand and evidence type.
2. Identify which retrieved brands have source evidence that supports their benchmark-based retrieval roles.
3. Identify whether the target has comparable evidence for the same retrieval drivers.
4. Mark missing, weak, stale, or unsupported target evidence.
5. Prioritize target evidence assets by retrieval role relevance, source gap severity, confidence, and validation value.

Evidence gaps should map to retrieval roles:

- Comparison anchor: missing alternatives, comparison, buyer criteria, or shortlist evidence.
- Trust / premium reference: missing case studies, certifications, awards, reviews, or independent proof.
- Local market provider: missing market pages, regional case studies, local partners, or location evidence.
- Technical infrastructure provider: missing capability pages, technical proof, specifications, or implementation evidence.
- Planning / consulting authority: missing methodology, advisory, project planning, or decision-support evidence.
- Niche specialist: missing use-case, segment, audience, or specialist proof.
- Budget / practical option: missing practical buyer guidance, pricing-fit context, tradeoffs, or implementation checklists.

The gap logic should not claim that retrieved brands rank because of specific sources. It should say source evidence may support the retrieval role observed in the benchmark.

## 9. Integration With Current Report

The source-grounded module would upgrade:

From:

- Inferred retrieval driver

To:

- Source-supported retrieval evidence

Future report sections:

- Source-Grounded Evidence Summary
- Retrieved Brand Evidence Drivers
- Target Evidence Gap
- Evidence Asset Priority
- Source Evidence Appendix

Interaction with current sections:

- Recommendation Readiness Verdict: reliability can increase when benchmark signal and source evidence align.
- Why Those Brands Were Retrieved: benchmark-based role hypotheses can be supported with specific source evidence.
- Target vs Retrieved Brand Gap: inferred gaps can become source-supported evidence gaps when target and retrieved-brand evidence are compared.
- First 3 Evidence Assets to Build: priorities can use source evidence quality, missing evidence type, and retrieval role relevance.
- Methodology / Reliability Notes: notes should state whether source-grounded research was included and how it affected interpretation.

The report should still distinguish observed benchmark signal, observed source evidence, inference, and recommended action.

## 10. Reliability Upgrade Rules

### Strong

Meaning:

Benchmark signal and source evidence align.

Typical conditions:

- Full Report Mode or broad prompt coverage.
- Multiple visible retrieved brands.
- Source evidence supports the reported retrieval drivers.
- Target evidence gaps are specific and validated against sources.

Language implication:

The report may state stronger source-supported findings while still avoiding causality claims.

### Directional

Meaning:

Benchmark signal exists, but source evidence is partial or uneven.

Typical conditions:

- Retrieved brands have some supporting evidence.
- Target evidence gaps are plausible but not fully validated.
- Source coverage is incomplete.

Language implication:

Use appears, suggests, may indicate, and requires validation.

### Exploratory

Meaning:

Signal is sparse or source coverage is shallow.

Typical conditions:

- Few retrieved brands.
- Few sources reviewed.
- Evidence is mostly owned, stale, indirect, or low confidence.

Language implication:

Frame findings as early hypotheses and prioritize further research or reruns.

### Insufficient Evidence

Meaning:

Neither benchmark signal nor source evidence supports a useful diagnosis.

Typical conditions:

- No meaningful retrieved-brand reference set.
- Source data is missing, unusable, stale, or contradictory.
- Target and retrieved-brand evidence cannot be compared responsibly.

Language implication:

Avoid diagnosis beyond basic observations. Recommend corrected inputs, broader source review, or a comparable future benchmark.

Strong should only become available when benchmark signal and source evidence align. Source-grounded evidence should improve reliability only when it is relevant, specific, and properly qualified.

## 11. Language and Safety Rules

The module must distinguish:

- Observed source evidence
- Inferred retrieval driver
- Source-supported claim
- Unsupported claim
- Recommended action

The module must avoid:

- Claiming causality between a source and AI retrieval
- Guaranteeing AI mentions
- Claiming ranking or share-of-voice improvement
- Making legal, medical, financial, or safety judgments
- Asserting market leadership unless supported and carefully qualified

Safe wording examples:

- "Source review found evidence that supports this market association."
- "This may help explain why the brand is easier to retrieve, but it does not prove causality."
- "The target appears to lack comparable public proof for this retrieval driver."
- "This evidence asset should be validated through a future benchmark."

Unsafe wording examples:

- "This page caused the brand to be retrieved."
- "Publishing this evidence will make AI mention the brand."
- "The retrieved brand is the market leader."
- "This proves the target is less credible."

## 12. Implementation Phases

### Phase 0: Spec Only

Goal:

Define product scope, evidence schema, source taxonomy, report integration, language rules, and implementation boundaries.

Deliverables:

- Source-grounded research spec.
- Future implementation plan.

Non-goals:

- No source discovery.
- No scraping.
- No report integration.

### Phase 1: Manual Source Evidence Input / CSV Import

Goal:

Allow analysts to provide source evidence manually in a structured format.

Deliverables:

- Evidence CSV schema.
- Validation rules for required fields.
- Empty and malformed data fallbacks.

Non-goals:

- No automated discovery.
- No crawling.
- No external API dependency.

### Phase 2: Deterministic Evidence Scoring and Report Integration

Goal:

Score structured evidence deterministically and integrate source-supported findings into Markdown reports.

Deliverables:

- Evidence confidence scoring.
- Brand-level evidence summaries.
- Target-vs-retrieved evidence gap logic.
- Report sections for source-supported evidence.

Non-goals:

- No broad web search.
- No claim that source evidence caused AI retrieval.

### Phase 3: Optional Assisted Source Discovery

Goal:

Help analysts find candidate source pages while preserving human review and validation.

Deliverables:

- Candidate source discovery workflow.
- Source type classification.
- Review queue or acceptance status.

Non-goals:

- No paid SEO crawling at scale.
- No scraping behind login.
- No private database integration.

### Phase 4: Source-Grounded Competitive Report Appendix

Goal:

Provide a structured appendix that cites source evidence behind retrieved-brand drivers and target gaps.

Deliverables:

- Source Evidence Appendix.
- Retrieved Brand Evidence Drivers.
- Target Evidence Gap table.
- Methodology and reliability notes for source review.

Non-goals:

- No legal, medical, financial, or safety judgments.
- No guaranteed visibility outcomes.

## 13. Testing and Validation Strategy

Future tests should cover:

- Evidence object validation
- Source URL and source type validation
- Citation/source formatting
- No unsupported claims
- Confidence scoring
- Report language safety
- Empty source data fallbacks
- Integration with benchmark reliability labels

Suggested test categories:

- Valid evidence item parses into the expected schema.
- Missing required fields are flagged.
- Unknown evidence types normalize safely or fail with a clear validation message.
- Source-supported claims require at least one accepted evidence item.
- Report output distinguishes observed source evidence from inference.
- Empty source data keeps current benchmark-based report behavior.
- Strong reliability is unavailable without relevant source-grounded evidence.

## 14. Risks and Non-Goals

Risks:

- Causality risk: source evidence may support retrievability but should not be described as causing AI retrieval.
- Source quality risk: owned sources, directories, news, reviews, and structured data have different reliability levels.
- Source freshness risk: stale evidence may mislead the report if freshness is not tracked.
- Regulated-claim risk: legal, medical, financial, or safety claims require special caution and should not be judged by this module.
- Citation/excerpt risk: excerpts must be concise, accurate, and traceable to source URLs.
- Overclaim risk: reports must avoid guarantees, ranking claims, or unsupported market leadership claims.
- Operational cost risk: broad crawling and source review can become expensive without clear limits.

Non-goals:

- Paid SEO crawling at scale
- Scraping behind login
- Private database integration
- Review manipulation
- Legal claims evaluation
- Guaranteed AI visibility improvement
- Replacing benchmark validation

The module should improve evidence quality and confidence, not replace future benchmark reruns.
