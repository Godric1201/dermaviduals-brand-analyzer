# Usage Guide

This guide explains how to use the AI Brand Visibility / GEO Audit Tool locally.

## 1. Start the App

Run:

```bash
python -m streamlit run app.py
```

The app opens in the browser and shows the analysis setup panel.

## 2. Configure the Audit

Use the sidebar to define:

- Target brand
- Product category
- Market
- Audience
- Competitor set
- Prompt mode
- Run mode

## 3. Select Run Mode

### Quick Test Mode

Use Quick Test Mode for fast workflow checks. It runs a smaller benchmark and is useful for testing configuration, scoring, and exports.

### Full Report Mode

Use Full Report Mode for a more complete portfolio-style audit. It generates richer analysis, Brand Intelligence findings, GEO recommendations, and exportable reports.

## 4. Run the Analysis

Click **Review & Run Analysis** after entering the setup fields.

The app will:

1. Generate or load benchmark prompts
2. Query the AI model
3. Analyze brand mentions
4. Score visibility and share of voice
5. Compare competitors
6. Generate strategy recommendations
7. Validate report output quality
8. Export reports and benchmark snapshots

## 5. Review Outputs

Depending on the run mode, outputs may include:

- Visibility scorecards
- Competitor benchmark tables
- Share of Voice analysis
- Brand Intelligence findings
- GEO Content Roadmap
- Markdown executive report
- DOCX executive report
- Benchmark snapshot JSON
- Snapshot comparison output

## 6. API Key Requirement

The app requires a local `.env` file with:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env` to GitHub.
