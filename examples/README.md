# Examples

This folder contains fictional demo artifacts for the AI Recommendation Readiness Diagnosis workflow.

The examples are designed for GitHub review, portfolio demonstration, and local validation. They are not live client data, confidential brand data, automated web research, or production benchmark results.

---

## Recommended Reading Order

Start with the executive report, then inspect the source evidence examples.

1. [`demo-executive-report.md`](demo-executive-report.md)
   Fictional executive report showing the full Recommendation Readiness narrative, including source-grounded evidence summary.

2. [`source-evidence-summary.md`](source-evidence-summary.md)
   Reusable source evidence summary section rendered by the local CLI from the demo JSON fixture.

3. [`skincare-source-evidence-summary.md`](skincare-source-evidence-summary.md)
   Fictional skincare vertical source evidence summary for a local-market recommendation scenario.

4. [`source-evidence-demo-report.md`](source-evidence-demo-report.md)
   Full deterministic source evidence demo report with coverage, gap analysis, priority assets, appendix, and methodology notes.

5. [`source-evidence-demo.json`](source-evidence-demo.json)
   Fictional source evidence fixture used to generate source evidence demo outputs.

---

## File Overview

| File | Type | Purpose |
| --- | --- | --- |
| `demo-executive-report.md` | Report example | Shows the product-style Recommendation Readiness diagnosis. |
| `source-evidence-summary.md` | CLI-rendered section | Shows the reusable source-grounded evidence summary output. |
| `source-evidence-demo-report.md` | Demo report | Shows the full source evidence demo with appendix and methodology notes. |
| `source-evidence-demo.json` | Fixture data | Provides fictional source evidence records for local rendering. |

---

## Local Rendering

Render the full source evidence demo report:

```bash
python scripts/render_source_evidence_demo.py


Render the skincare source evidence summary:

```bash
python scripts/render_source_evidence_summary.py examples/skincare-source-evidence-demo.json examples/skincare-source-evidence-summary.md
```