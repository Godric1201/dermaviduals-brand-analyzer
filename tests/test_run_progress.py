from run_progress import (
    build_progress_steps,
    format_progress_message,
    get_progress_mode_note,
)


def test_build_progress_steps_returns_expected_phases():
    steps = build_progress_steps("Full Report Mode")

    assert steps == [
        "Preparing analysis context",
        "Generating benchmark prompts",
        "Running AI visibility benchmark",
        "Scoring brand and competitor visibility",
        "Building Brand Intelligence diagnostics",
        "Generating GEO Content Roadmap",
        "Preparing exports and report outputs",
        "Analysis complete",
    ]


def test_format_progress_message_uses_step_count_and_label():
    assert (
        format_progress_message(3, 8, "Running AI visibility benchmark")
        == "Step 3 of 8 — Running AI visibility benchmark"
    )


def test_get_progress_mode_note_differs_by_run_mode():
    assert (
        get_progress_mode_note("Full Report Mode")
        == "Full Report Mode runs a multi-step AI visibility and strategy audit. This may take several minutes."
    )
    assert (
        get_progress_mode_note("Quick Test Mode")
        == "Quick Test Mode runs a limited prompt set for QA and preview."
    )
