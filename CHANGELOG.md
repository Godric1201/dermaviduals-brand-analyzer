# Changelog

All notable changes to this project are documented here.

## v0.2.0 - Repository Cleanup and Package Refactor

### Added

- Added `docs/usage-guide.md` with local usage instructions.
- Added `docs/output-examples.md` to document generated audit outputs.
- Added `.env.example` as a safe environment variable template.
- Added dashboard preview screenshot for the README.

### Changed

- Refactored root-level Python modules into the `src/geo_audit/` package.
- Kept `app.py` as the root Streamlit entrypoint.
- Updated imports across app modules and tests to use the new package structure.
- Improved README structure, project presentation, setup instructions, and documentation links.
- Updated project structure documentation to reflect the new `src/geo_audit/` layout.

### Removed

- Removed stray `t -q` diff output file from the repository.
- Removed root-level module clutter by moving core modules into the package folder.

### Validation

- Confirmed `streamlit run app.py` works after refactor.
- Confirmed the regression test suite passes: `203 passed`.

## v0.1.0 - Initial GEO Audit Prototype

### Added

- Streamlit-based AI visibility audit workflow.
- Target brand and competitor configuration.
- Prompt-based AI recommendation benchmark.
- Visibility scoring and Share of Voice analysis.
- Brand Intelligence analysis.
- GEO Content Roadmap generation.
- Markdown and DOCX executive report exports.
- Benchmark snapshot export and comparison support.
- Output quality validation layer.
- Regression test suite for core functionality.