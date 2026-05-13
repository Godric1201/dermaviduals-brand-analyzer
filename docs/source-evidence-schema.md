# Source Evidence Schema

This document describes the manual source evidence JSON format used by the source-grounded evidence workflow.

The schema is intentionally simple. It is designed for deterministic demos, manual evidence review, and future CSV / JSON import support.

---

## Purpose

Source evidence records describe public evidence that may support brand retrievability in AI recommendation-style answers.

They are used to compare the target brand against retrieved brands and identify evidence gaps.

The schema supports questions such as:

- What public evidence exists for the target brand?
- What evidence types are visible for retrieved brands?
- Which evidence types are missing for the target brand?
- Which evidence assets should be built first?

Source evidence is validation context. It does not prove that a specific source caused AI retrieval.

---

## Payload Shape

```json
{
  "target_brand": "Example Infrastructure Co.",
  "retrieved_brands": [
    "Reference Brand A",
    "Reference Brand B",
    "Reference Brand C"
  ],
  "category": "Data center infrastructure consulting and project support",
  "market": "Germany",
  "audience": "Enterprise infrastructure buyers",
  "evidence_items": []
}
```

### Top-Level Fields

| Field | Required | Description |
| --- | --- | --- |
| `target_brand` | Yes | Brand being audited. |
| `retrieved_brands` | Yes | Brands retrieved by AI instead of or alongside the target brand. |
| `category` | Recommended | Product, service, or market category being tested. |
| `market` | Recommended | Geographic or commercial market context. |
| `audience` | Recommended | Buyer, user, or decision-maker audience. |
| `evidence_items` | Yes | List of source evidence records. |

---

## Evidence Item Shape

```json
{
  "brand": "Reference Brand A",
  "evidence_type": "Comparison Evidence",
  "source_url": "https://reference-a.test/alternatives",
  "source_title": "Reference Brand A Alternatives Guide",
  "source_domain": "reference-a.test",
  "source_type": "Third-Party / Editorial",
  "excerpt_or_summary": "The page compares Reference Brand A with alternative infrastructure providers.",
  "observed_claim": "Reference Brand A has comparison-oriented public evidence.",
  "supported_retrieval_driver": "Comparison anchor",
  "confidence": "High",
  "freshness_date": "2025-03-01",
  "validation_status": "Observed",
  "notes": "Fictional demo source."
}
```

### Evidence Item Fields

| Field | Required | Description |
| --- | --- | --- |
| `brand` | Yes | Brand the source evidence belongs to. |
| `evidence_type` | Yes | Type of evidence the source supports. |
| `source_url` | Yes | URL for the source evidence. |
| `source_title` | Yes | Human-readable source title. |
| `source_domain` | Optional | Domain name of the source. |
| `source_type` | Yes | Type of source, such as owned page, case study, third-party editorial, or structured data. |
| `excerpt_or_summary` | Yes | Short summary of the relevant evidence. |
| `observed_claim` | Yes | Conservative claim supported by the source. |
| `supported_retrieval_driver` | Recommended | Retrieval driver this evidence may support. |
| `confidence` | Yes | Confidence level for the evidence record. |
| `freshness_date` | Optional | Date associated with the source or observation. |
| `validation_status` | Yes | Review status of the evidence record. |
| `notes` | Optional | Internal note or review context. |

---

## Supported Evidence Types

| Evidence Type | Use |
| --- | --- |
| `Entity Evidence` | Shows that the brand exists and can be identified. |
| `Category Evidence` | Connects the brand to the tested product or service category. |
| `Market Evidence` | Connects the brand to the target market or geography. |
| `Offering / Use-Case Evidence` | Explains concrete offerings, applications, or use cases. |
| `Proof / Trust Evidence` | Shows references, case studies, certifications, clients, or credibility signals. |
| `Comparison Evidence` | Helps AI understand alternatives, positioning, or selection criteria. |
| `Third-Party Corroboration` | Provides external confirmation from credible third-party sources. |
| `Structured Data Evidence` | Adds machine-readable entity, product, organization, or review signals. |
| `Recency / Freshness Evidence` | Shows recent activity, updates, launches, news, or current relevance. |
| `Authority / Association Evidence` | Shows partnerships, memberships, awards, industry associations, or authority signals. |

---

## Supported Confidence Levels

| Value | Meaning |
| --- | --- |
| `High` | Strong, direct, and clearly relevant evidence. |
| `Medium` | Useful evidence with some limitation or indirectness. |
| `Low` | Weak or partial evidence that may still be useful for review. |
| `Insufficient` | Not enough evidence to support a meaningful claim. |

---

## Supported Validation Statuses

| Value | Meaning |
| --- | --- |
| `Observed` | Evidence was reviewed and accepted. |
| `Needs Review` | Evidence may be useful but requires manual review. |
| `Stale` | Evidence exists but may be outdated. |
| `Conflicting` | Evidence conflicts with another source or claim. |
| `Rejected` | Evidence should not be used in reporting. |

---

## Recommended Review Rules

Use source evidence only when it is specific enough to support a conservative claim.

Prefer evidence that is:

- public
- source-specific
- category-relevant
- market-relevant
- tied to a concrete claim
- clear enough for manual review

Avoid evidence that is:

- vague
- unverifiable
- purely promotional with no concrete claim
- unrelated to the tested category
- copied without review
- used to imply retrieval causality

---

## Causality Boundary

Source evidence can support a hypothesis that a brand may be more retrievable for certain recommendation prompts.

It should not be used to claim:

- a source caused AI retrieval
- a source guarantees AI recommendation
- a brand is objectively the market leader
- a content asset will guarantee share-of-voice growth

Preferred wording:

- source-supported evidence gap
- validation context
- benchmark-based hypothesis
- candidate-set inclusion to test

---

## Example Fixture

See:

- [`examples/source-evidence-demo.json`](../examples/source-evidence-demo.json)
- [`examples/source-evidence-demo-report.md`](../examples/source-evidence-demo-report.md)
- [`examples/source-evidence-demo-report.md`](../examples/source-evidence-demo-report.md)


---

## CLI Rendering

Render a source evidence summary from any schema-compatible JSON payload:

```bash
python scripts/render_source_evidence_summary.py examples/source-evidence-demo.json examples/source-evidence-summary.md
```

Include the appendix:

```bash
python scripts/render_source_evidence_summary.py examples/source-evidence-demo.json examples/source-evidence-summary.md --include-appendix
```

The command is local and deterministic. It does not call OpenAI, Streamlit, web search, or scraping.