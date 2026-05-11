# Recommendation Readiness Report Spec

## 1. Product Positioning

The report direction is shifting:

- From: AI Brand Visibility Benchmark
- To: AI Recommendation Readiness Diagnosis

The report should not merely say whether a brand was mentioned. It should diagnose whether the brand is ready to be retrieved and recommended by AI systems for the target category, market, audience, and use-case context.

Core customer question:

Why does AI recommend other brands instead of the target, and what evidence should the target build first?

The intended customer is a niche brand, small company, founder, owner, or marketing team that needs a practical explanation of what AI appears to understand, what it retrieves instead, and which evidence assets should be built before expecting stronger recommendation visibility.

## 2. Customer Questions The Report Must Answer

The report must answer these questions directly:

- Does AI appear to understand who the target brand is?
- Does AI include the target brand in the recommendation candidate set?
- If not, who does AI retrieve instead?
- What roles do the retrieved brands appear to occupy?
- What gap exists between the target and retrieved brands?
- Which three evidence assets should the target build first?
- How should progress be validated?

The report should be decision-oriented. It should avoid stopping at "visibility is zero" and should avoid generic advice such as "improve marketing" or "create more content."

## 3. Current Report Limitations

The current zero-visibility report has useful diagnostics, including visibility state, First Detection Strategy, Brand Understanding Probe, Market Relevance Probe, Evidence Gap Map, Evidence-Building Task Roadmap, Validation Plan, and supporting benchmark tables.

Remaining limitations:

- The report is still benchmark/taxonomy-oriented rather than recommendation-readiness-oriented.
- Evidence Gap Map is useful supporting material, but it is not the main executive narrative.
- The roadmap is too broad for founder or owner decision-making because it can present many evidence tasks instead of the first three priorities.
- Retrieved brands are not yet differentiated by retrieval role.
- The target-vs-retrieved brand gap is not explicit enough.
- Benchmark reliability level is not visible enough in the main narrative.
- Source-grounded evidence is not currently available, so many retrieval explanations must remain benchmark-based and AI-inferred.

## 4. Proposed Report Structure

The next-generation Markdown report should use this order.

### 1. Recommendation Readiness Verdict

Purpose:

Summarize the report in a business-readable verdict.

Required inputs:

- Target visibility metrics
- Visibility state
- Strategy mode
- Brand Understanding Probe result, if available
- Market Relevance Probe result, if available
- Benchmark reliability level

Output content:

- Recommendation readiness verdict
- Whether the target entered the recommendation candidate set
- Primary diagnosis, such as entity understanding gap, recommendation retrieval gap, market relevance gap, evidence gap, or mixed diagnosis
- First measurable objective
- Reliability level and short rationale

Language constraints:

- Use benchmark-based and AI-inferred framing.
- Do not claim verified market facts.
- Do not promise timeline or outcomes.
- For zero visibility, candidate-set inclusion is the first objective, not share-of-voice dominance.

### 2. Brand Understanding Summary

Purpose:

Explain whether AI appears to understand the target brand before interpreting recommendation visibility.

Required inputs:

- Brand Understanding Probe result
- Target category
- Target market
- Target audience

Output content:

- Brand understanding status
- Category alignment
- Market alignment
- Audience alignment
- Short interpretation of whether the issue appears to be recognition, alignment, retrieval, evidence, or mixed

Language constraints:

- Use "AI-inferred" and "requires validation."
- Do not treat probe output as verified fact.
- If unavailable, say the report cannot separate entity understanding from retrieval failure with confidence.

### 3. Who AI Retrieved Instead

Purpose:

Identify the visible brands that appeared in recommendation answers.

Required inputs:

- Competitive benchmark summary
- Prompt-level winners
- Top visible brands
- Target brand metrics

Output content:

- Retrieved brands
- Their benchmark visibility signals
- Whether they appear to be peer competitors, aspirational competitors, category anchors, or unclear references

Language constraints:

- Use "retrieved brands," "visible reference brands," or "category anchors" where appropriate.
- Do not frame every visible brand as a direct competitor to attack.
- Do not imply market leadership from benchmark visibility alone.

### 4. Why Those Brands Were Retrieved

Purpose:

Translate visible brands into likely retrieval roles so the customer can understand what evidence patterns may be missing.

Required inputs:

- Retrieved brands
- Prompt categories where each brand appeared
- Market Relevance Probe result
- Optional future source-grounded evidence

Output content:

- Retrieval role classification for each visible brand
- Cautious explanation of why the brand may have been retrieved
- What the role implies for the target

Language constraints:

- Use "appears," "suggests," and "may indicate."
- If no source-grounded evidence exists, mark the explanation as inferred from benchmark output.
- Avoid definitive claims about competitor strengths.

### 5. Target vs Retrieved Brand Gap

Purpose:

Explain the practical gap between the target and each visible retrieved brand.

Required inputs:

- Target metrics
- Retrieved brand metrics
- Retrieval role classification
- Brand Understanding Probe result
- Market Relevance Probe result

Output content:

- Observed benchmark signal
- Inferred retrieval role
- Inferred target gap
- Evidence asset implication
- Required validation

Language constraints:

- Keep each gap concise.
- Distinguish observed data from inference.
- Do not present benchmark inference as verified competitive intelligence.

### 6. First 3 Evidence Assets to Build

Purpose:

Prioritize the first three concrete evidence assets the target should build or improve.

Required inputs:

- Observed benchmark gaps
- Retrieval role classifications
- Evidence taxonomy
- Brand Understanding Probe result
- Market Relevance Probe result
- Prompt categories

Output content:

- Three ranked evidence assets only
- For each asset: what to build, why it matters, target retrieval driver, target prompts, and validation method

Language constraints:

- Avoid generic advice.
- Each asset must map to a retrieval driver or observed benchmark gap.
- Do not claim the asset will cause AI mentions.

### 7. Validation Plan

Purpose:

Define how the customer should validate whether evidence improvements are becoming retrievable.

Required inputs:

- Prompt categories
- Target visibility state
- Recommended evidence assets
- Benchmark reliability level

Output content:

- What to rerun
- What counts as progress
- What does not count as proof
- First milestone
- Timing caution

Language constraints:

- No guaranteed timeline.
- First measurable inclusion is the initial milestone for zero-visibility brands.
- Share-of-voice growth should come after candidate-set inclusion.

### 8. Supporting Benchmark Data

Purpose:

Keep detailed benchmark data available without letting it dominate the main narrative.

Required inputs:

- Competitive benchmark table
- Trigger-level visibility results
- Top brand winners by query type
- Evidence Gap Map
- Optional raw diagnostic output

Output content:

- Supporting tables and diagnostic details
- Evidence Gap Map as appendix/supporting material

Language constraints:

- Label these sections as supporting evidence.
- Avoid making raw tables the primary executive story.

### 9. Methodology / Reliability Notes

Purpose:

Explain what the benchmark can and cannot support.

Required inputs:

- Run mode
- Prompt count
- Competitor set quality
- Probe availability
- Benchmark reliability level
- Source-grounded evidence availability

Output content:

- Reliability level
- Methodological caveats
- Distinction between observed benchmark signal, inference, and source-grounded evidence

Language constraints:

- Be explicit when source-grounded research is not available.
- Do not overstate precision.
- Do not present benchmark inference as verified market fact.

## 5. Evidence Hierarchy

The report must distinguish four evidence levels.

### 1. Observed Benchmark Signal

Definition:

Data measured in the benchmark output, such as mentions, prompts visible, share of voice, visibility score, prompt winners, and retrieved brands.

Safe wording:

- "In this benchmark, the target was not retrieved in the tested recommendation prompts."
- "The benchmark retrieved these visible reference brands."
- "Based on the tested prompt set, this brand had the strongest measured signal in this query category."

### 2. Inferred Retrieval Driver

Definition:

A cautious explanation of why a visible brand may have been retrieved, based on benchmark patterns, prompt categories, and probe results.

Safe wording:

- "This may indicate that the brand is acting as a comparison anchor in the tested prompt set."
- "The answer set appears to lean toward globally visible category leaders."
- "This suggests a possible market evidence gap, but it requires validation."

### 3. Source-Grounded Evidence

Definition:

Evidence verified from source material, such as official websites, case studies, partner pages, directories, industry associations, reviews, news, or structured data.

Safe wording:

- "Source review found case studies that support this market association."
- "The official website provides structured evidence for this offering."
- "Third-party directory listings corroborate the brand's category and market presence."

Current product status:

The current product does not yet provide source-grounded evidence review. This requires a future source-grounded research module.

### 4. Recommended Action

Definition:

A concrete evidence asset or validation step recommended because it addresses an observed benchmark gap or inferred retrieval driver.

Safe wording:

- "This asset is intended to test whether clearer retrievable evidence improves candidate-set inclusion."
- "Build this evidence before expecting reliable recommendation visibility."
- "Validate by rerunning comparable market-qualified and use-case prompts."

Current product support:

The current product mostly supports levels 1, 2, and 4. Level 3 requires future source-grounded research.

## 6. Retrieval Role Classification

Purpose:

The report must explain why each visible brand may have been retrieved, without making every competitor sound the same.

Role classification should be deterministic where possible and cautious where inference is required. If source-grounded evidence is unavailable, role labels should be described as benchmark-based.

### Planning / Consulting Authority

Meaning:

The brand appears in advisory, strategy, planning, implementation guidance, or expert-selection contexts.

Likely benchmark signals:

- Appears in prompts about planning, choosing, implementing, evaluating, or consulting.
- Wins decision-stage or strategy-oriented query categories.

Possible evidence assets the target may need:

- Advisory service pages
- Methodology pages
- Implementation guides
- Case studies showing decision support

Caution notes:

Do not claim the retrieved brand is a verified consulting authority unless source-grounded evidence confirms it.

### Technical Infrastructure Provider

Meaning:

The brand appears to be retrieved for technical capability, infrastructure, systems, platforms, facilities, or operational depth.

Likely benchmark signals:

- Appears in technical, implementation, infrastructure, platform, or capability prompts.
- Retrieved beside category leaders known for operational scale or technical depth.

Possible evidence assets the target may need:

- Technical capability pages
- Infrastructure specifications
- Certifications
- Architecture or process explainers
- Operational proof points

Caution notes:

Benchmark visibility does not prove technical superiority.

### Local Market Provider

Meaning:

The brand appears to be retrieved because it fits the specified market, geography, or local audience.

Likely benchmark signals:

- Appears in market-qualified prompts.
- Retrieved in local or regional recommendation contexts.
- Market Relevance Probe suggests market-specific adherence.

Possible evidence assets the target may need:

- Local market landing pages
- Regional customer examples
- Partner pages
- Location pages
- Local-language or market-specific proof

Caution notes:

Do not claim verified local market presence without source-grounded validation.

### Trust / Premium Reference

Meaning:

The brand appears to act as a high-trust, premium, established, or credible reference in the answer set.

Likely benchmark signals:

- Appears in best, trusted, leading, premium, enterprise, or decision-stage prompts.
- Has strong visibility across multiple prompt categories.

Possible evidence assets the target may need:

- Case studies
- Testimonials
- Certifications
- Awards
- Expert validation
- Independent reviews

Caution notes:

Do not claim the retrieved brand is a proven market leader from benchmark visibility alone.

### Budget / Practical Option

Meaning:

The brand appears to be retrieved for affordability, accessibility, practicality, small-business fit, or ease of adoption.

Likely benchmark signals:

- Appears in prompts about affordable options, practical alternatives, easy adoption, or smaller buyer needs.
- Retrieved in comparison prompts where large category anchors may not fit every use case.

Possible evidence assets the target may need:

- Pricing guidance
- Buyer guides
- Small-business use cases
- Practical comparison pages
- Implementation checklists

Caution notes:

Do not infer pricing or affordability unless source-grounded evidence exists.

### Niche Specialist

Meaning:

The brand appears to be retrieved because it is associated with a specific use case, audience, segment, or specialized category need.

Likely benchmark signals:

- Appears in use-case prompts or audience-specific prompts.
- Has narrower but relevant prompt-level visibility.

Possible evidence assets the target may need:

- Niche use-case pages
- Audience pages
- Segment-specific case studies
- Specialized comparison pages

Caution notes:

Do not overgeneralize niche visibility into broad category ownership.

### Comparison Anchor

Meaning:

The brand appears because AI uses it as a familiar point of comparison, alternative, or benchmark reference.

Likely benchmark signals:

- Appears in "alternatives to," "compare," "best options," or "shortlist" prompts.
- Retrieved across competitor-comparison contexts.

Possible evidence assets the target may need:

- Alternatives pages
- Comparison pages
- Category selection criteria
- Buyer guides
- Clear differentiation pages

Caution notes:

Comparison-anchor status does not prove direct buyer substitution.

### Unclear Retrieved Reference

Meaning:

The brand appears in the benchmark, but the reason for retrieval is not clear from current data.

Likely benchmark signals:

- Low or inconsistent visibility.
- Appears in only one prompt category.
- Probe results are weak or insufficient.

Possible evidence assets the target may need:

- Basic entity evidence
- Offering clarity
- Market relevance evidence
- Source-grounded validation before acting

Caution notes:

Use this label when the report cannot responsibly infer a stronger role.

### Competitor Tiering

The report should distinguish retrieved brands by competitive tier:

- Peer competitor: a brand that appears to serve a similar buyer, market, and category need.
- Aspirational competitor: a larger or more established brand that may not be a direct peer but acts as a reference point.
- Category anchor: a highly visible brand that shapes the category answer set.
- Unclear / needs validation: a retrieved brand whose role or relationship cannot be determined from benchmark data alone.

Tiering should be benchmark-based unless source-grounded research is available.

## 7. Target vs Retrieved Brand Gap Analysis

This section should explain what separates the target from visible retrieved brands in the benchmark.

For each visible retrieved brand, include:

- Observed benchmark signal
- Inferred retrieval role
- Inferred gap for the target
- Evidence asset implication
- Required validation

Generic example:

Retrieved brand: ExampleCo

Observed benchmark signal:

ExampleCo appeared in market-qualified and comparison prompts, while the target was not retrieved.

Inferred retrieval role:

ExampleCo appears to act as a comparison anchor for buyers evaluating options in the category.

Inferred gap for the target:

The target may lack retrievable comparison evidence that explains when it is a relevant alternative.

Evidence asset implication:

Create comparison and alternatives pages that explain category fit, buyer criteria, target use cases, and tradeoffs.

Required validation:

Rerun comparable comparison prompts and check whether the target appears beside relevant retrieved alternatives with accurate context.

Important constraint:

This is not verified competitive intelligence unless source-grounded research exists. Without source-grounded research, the section must describe benchmark-based inference only.

## 8. First 3 Evidence Assets to Build

The main report should recommend only three prioritized evidence assets.

Each asset must use this format:

Priority X — [Evidence asset name]

What to build:

Describe the concrete page, proof asset, structured data improvement, comparison asset, case study, or validation artifact.

Why it matters:

Explain which retrieval problem this asset addresses.

Target retrieval driver:

Name the retrieval role or evidence gap this asset is intended to influence.

Targets / prompt groups:

List the prompt categories or query types where improvement should be validated.

Validation:

Define what to rerun and what would count as progress.

Rules:

- Avoid generic advice such as "improve marketing" or "create more content."
- Each asset must be tied to an inferred retrieval driver or observed benchmark gap.
- Each asset must have a validation method.
- The first milestone should usually be candidate-set inclusion, not immediate share-of-voice dominance.
- Do not recommend more than three primary assets in the main narrative.
- Additional evidence tasks may appear in supporting material, but they should not dilute the executive recommendation.

## 9. Benchmark Reliability Levels

The report should assign a reliability level to the interpretation.

### Strong

Meaning:

The benchmark provides a stable and interpretable pattern.

Typical conditions:

- Full Report Mode or broad prompt coverage
- Clean competitor parsing
- Multiple visible retrieved brands
- Visible brands include relevant peers, aspirational competitors, or category anchors
- Brand Understanding Probe is clear or directionally useful
- Market Relevance Probe is clear or directionally useful
- Source-grounded evidence exists, if available in future versions

Report language implications:

The report may state stronger benchmark-based conclusions, while still avoiding verified market claims unless source-grounded evidence exists.

### Directional

Meaning:

The benchmark provides useful guidance, but interpretation should remain cautious.

Typical conditions:

- Moderate prompt coverage
- Some visible retrieved brands
- Target may have low or zero mentions
- Competitor set appears usable
- Probe results are partial, mixed, or cautious
- Source-grounded evidence is not available

Report language implications:

Use "suggests," "appears," and "may indicate." Recommend validation through comparable reruns.

### Exploratory

Meaning:

The benchmark provides early signal but should not drive major decisions alone.

Typical conditions:

- Low prompt count
- Few visible retrieved brands
- Quick Test Mode or constrained run
- Target has zero mentions
- Visible brands may be category anchors rather than peers
- Probe confidence is weak or insufficient

Report language implications:

Frame findings as hypotheses. Prioritize first validation steps before strategic claims.

### Insufficient Evidence

Meaning:

The benchmark does not provide enough reliable signal to support a diagnosis.

Typical conditions:

- Very few prompts
- No meaningful visible brands
- Competitor parsing quality is poor
- Target has zero mentions and no useful reference set
- Brand Understanding Probe is unavailable or not enough evidence
- Market Relevance Probe is unavailable or insufficient
- No source-grounded evidence exists

Report language implications:

Avoid diagnosis beyond basic observations. Recommend rerunning with corrected inputs, broader prompt coverage, or source-grounded research.

### Reliability Factors

Reliability should consider:

- Prompt count
- Number of visible retrieved brands
- Whether target had zero mentions
- Whether visible brands are peers, aspirational competitors, or category anchors
- Competitor parsing quality
- Strength of Brand Understanding Probe
- Strength of Market Relevance Probe
- Whether source-grounded evidence exists

Principle:

The report must not present benchmark inference as verified market fact.

## 10. Language Rules and Overclaim Prevention

Allowed cautious language:

- appears
- suggests
- may indicate
- based on this benchmark
- requires validation
- not verified market fact
- AI-inferred
- benchmark-based

Forbidden claims:

- guarantee AI mentions
- will get mentioned
- will improve share of voice
- proven market leader
- verified fact when only benchmark inference exists
- definitive causality without source-grounded evidence

Examples:

Bad:

"AI does not recommend this company."

Better:

"In this benchmark, the target was not retrieved in the tested recommendation prompts."

Bad:

"Build this page and AI will mention you."

Better:

"This asset is intended to test whether clearer retrievable evidence improves candidate-set inclusion."

Bad:

"The retrieved brand is the market leader."

Better:

"The retrieved brand acted as a visible category anchor in this benchmark. That does not prove market leadership."

Bad:

"The target needs better marketing."

Better:

"The target appears to lack retrievable comparison evidence that would make it eligible for alternative and shortlist prompts."

## 11. Supporting Appendix Data

The following should move to appendix or supporting data:

- Evidence Gap Map
- Full benchmark tables
- Prompt-level results
- Detailed score tables
- Methodology details
- Raw diagnostic outputs

These materials are still useful. They support the diagnosis and give analysts a way to audit the benchmark. They should not dominate the executive narrative.

The main narrative should answer:

- What happened?
- Why might AI retrieve other brands instead?
- What should the target build first?
- How should progress be validated?

## 12. Future Source-Grounded Research Module

This is out of scope for the current spec branch but necessary for commercial maturity.

Possible module names:

- source_research
- competitor_evidence_research

Sources to inspect later:

- Official website pages
- Case studies
- Reference projects
- News
- Third-party directories
- Partner pages
- Industry associations
- Structured data / schema / sameAs
- Relevant reviews or platform/community mentions where applicable

The source-grounded research module would upgrade:

- Inferred retrieval drivers

into:

- Source-grounded competitive evidence

Expected value:

- Validate whether visible brands have source-backed evidence for their inferred retrieval roles.
- Identify which evidence assets the target lacks relative to retrieved brands.
- Reduce hallucination risk.
- Improve confidence in retrieval role classification.
- Support stronger reliability labels.

Important boundary:

Even with source-grounded research, the report should not guarantee AI mentions. It should state that evidence improvements are intended to improve retrievability and should be validated through future benchmarks.

## 13. Implementation Sequence After Spec Approval

Recommended implementation sequence:

1. Add helper logic for verdict and reliability labels.
2. Add retrieval role scaffolding.
3. Update zero-visibility Markdown section order.
4. Replace broad roadmap with First 3 Evidence Assets.
5. Demote Evidence Gap Map and raw benchmark tables to supporting sections.
6. Add tests for section order, cautious language, first three assets, and reliability notes.
7. Add DOCX parity after Markdown structure is stable.
8. Add source-grounded research module in a later commercial branch.
