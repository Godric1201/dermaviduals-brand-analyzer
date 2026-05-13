# Examples

This directory contains public-facing example outputs for the AI Recommendation Readiness Diagnosis workflow.

## Available Example Outputs

- [Demo Executive Report](demo-executive-report.md)
- [Source Evidence Demo Report](source-evidence-demo-report.md)
- [Source Evidence Demo Fixture](source-evidence-demo.json)

The demo executive report is a fictional, anonymized, condensed Full Report Mode-style example. It demonstrates a zero-visibility / Not Detected scenario where the target brand does not enter the tested AI recommendation candidate set, while other retrieved brands appear instead.

The example is benchmark-based. It is not live client data, confidential brand data, Quick Test Mode output, or source-grounded competitive research. Retrieval roles, target gaps, and recommended evidence assets should be read as benchmark-based hypotheses that require validation.

## Source Evidence Demo

The source evidence demo is a deterministic fixture-based example for the future source-grounded research layer.

It demonstrates:

- accepted source evidence coverage by brand
- target-vs-retrieved evidence gaps
- first evidence assets to build
- source evidence appendix formatting
- cautious language separating observed source evidence from retrieval causality

The demo can be regenerated locally without Streamlit, OpenAI, web search, scraping, or live client data:

```bash
python scripts/render_source_evidence_demo.py
```

This writes:

```text
examples/source-evidence-demo-report.md
```

The fixture lives at:

```text
examples/source-evidence-demo.json
```

Source-grounded competitor and evidence research is a future extension, not part of the current live benchmark workflow. The current demo uses fictional source records to show the intended report structure and evidence-gap logic.

For more context, see:

- [Output Examples](../docs/output-examples.md)
- [Methodology](../docs/methodology.md)
- [Recommendation Readiness Report Spec](../docs/recommendation-readiness-report-spec.md)
- [Source-Grounded Research Spec](../docs/source-grounded-research-spec.md)
