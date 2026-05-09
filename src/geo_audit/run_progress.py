def build_progress_steps(run_mode):
    return [
        "Preparing analysis context",
        "Generating benchmark prompts",
        "Running AI visibility benchmark",
        "Scoring brand and competitor visibility",
        "Building Brand Intelligence diagnostics",
        "Generating GEO Content Roadmap",
        "Preparing exports and report outputs",
        "Analysis complete",
    ]


def format_progress_message(step_index, total_steps, label):
    return f"Step {step_index} of {total_steps} — {label}"


def get_progress_mode_note(run_mode):
    if run_mode == "Quick Test Mode":
        return "Quick Test Mode runs a limited prompt set for QA and preview."

    return (
        "Full Report Mode runs a multi-step AI visibility and strategy audit. "
        "This may take several minutes."
    )
