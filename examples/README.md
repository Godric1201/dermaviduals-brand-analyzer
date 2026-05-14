# Examples

This folder contains fictional demo artifacts for the AI Recommendation Readiness Diagnosis workflow.

The examples are designed for GitHub review, portfolio demonstration, and local validation. They are not live client data, confidential brand data, automated web research, or production benchmark results.

---

## Recommended Reading Order

Start with the executive report, then inspect the source evidence examples.

1. [`demo-executive-report.md`](demo-executive-report.md)
   Fictional executive report showing the full Recommendation Readiness narrative, including source-grounded evidence summary.

2. [`source-evidence-summary.md`](source-evidence-summary.md)
   Reusable source evidence summary section rendered by the local CLI from the generic JSON fixture.

3. [`skincare-source-evidence-summary.md`](skincare-source-evidence-summary.md)
   Fictional skincare vertical source evidence summary for a local-market recommendation scenario.

4. [`source-evidence-demo-report.md`](source-evidence-demo-report.md)
   Full deterministic source evidence demo report with coverage, gap analysis, priority assets, appendix, and methodology notes.

5. [`source-evidence-demo.json`](source-evidence-demo.json)
   Generic fictional source evidence JSON fixture used to generate source evidence demo outputs.

6. [`skincare-source-evidence-demo.json`](skincare-source-evidence-demo.json)
   Fictional skincare source evidence JSON fixture.

7. [`skincare-source-evidence-demo.csv`](skincare-source-evidence-demo.csv)
   Spreadsheet-friendly CSV version of the skincare source evidence fixture.

---

## File Overview

| File | Type | Purpose |
| --- | --- | --- |
| `demo-executive-report.md` | Report example | Shows the product-style Recommendation Readiness diagnosis. |
| `source-evidence-summary.md` | CLI-rendered section | Shows the reusable source-grounded evidence summary output from the generic fixture. |
| `skincare-source-evidence-summary.md` | CLI-rendered section | Shows a more realistic skincare vertical source evidence summary. |
| `source-evidence-demo-report.md` | Demo report | Shows the full source evidence demo with appendix and methodology notes. |
| `source-evidence-demo.json` | Fixture data | Provides generic fictional source evidence records for local rendering. |
| `skincare-source-evidence-demo.json` | Fixture data | Provides fictional skincare source evidence records for local rendering. |
| `skincare-source-evidence-demo.csv` | Fixture data | Provides the skincare source evidence fixture in spreadsheet-friendly CSV format. |

---

## Local Rendering

Render the full source evidence demo report:

```bash
python scripts/render_source_evidence_demo.py
```

Render the generic reusable source evidence summary from JSON:

```bash
python scripts/render_source_evidence_summary.py examples/source-evidence-demo.json examples/source-evidence-summary.md
```

Render the skincare source evidence summary from JSON:

```bash
python scripts/render_source_evidence_summary.py examples/skincare-source-evidence-demo.json examples/skincare-source-evidence-summary.md
```

Render a source evidence summary from the skincare CSV fixture:

```bash
python scripts/render_source_evidence_summary.py examples/skincare-source-evidence-demo.csv examples/skincare-source-evidence-summary-from-csv.md
```

The JSON and CSV fixtures are local, deterministic demo inputs. They do not call OpenAI, Streamlit, web search, scraping, or live client data.
