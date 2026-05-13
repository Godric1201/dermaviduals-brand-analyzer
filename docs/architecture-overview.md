# Architecture Overview

This document explains the product architecture behind the AI Recommendation Readiness Diagnosis workflow.

The project is designed as a local-first analysis pipeline. It separates benchmark execution, scoring, diagnosis, source evidence comparison, and report generation so each layer can evolve independently.

---

## Pipeline Summary

```text
Recommendation Prompts
        ↓
AI Response Collection
        ↓
Brand Visibility Scoring
        ↓
Retrieved Brand Diagnosis
        ↓
Source Evidence Gap Analysis
        ↓
Markdown / DOCX Report Output