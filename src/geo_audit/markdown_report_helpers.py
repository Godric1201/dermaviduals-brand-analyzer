def normalize_markdown_table_headers(df, column_map):
    if df is None:
        return df

    return df.copy().rename(columns={
        column: label
        for column, label in column_map.items()
        if column in df.columns
    })


def build_methodology_notes_md(category, prompt_categories):
    notes = [
        f"- This AI visibility benchmark is based on fixed and AI-generated prompts designed to simulate {category} recommendation queries.",
        "- Visibility is calculated from brand mentions, estimated ranking, and prompt-level appearance within the tested prompt set.",
        "- Share of voice reflects the distribution of brand mentions among tracked competitors in this benchmark run.",
        "- Scores reflect AI answer visibility, not market share, product performance, customer satisfaction, or broader business performance outcomes.",
        "- The output should be interpreted as an AI visibility benchmark, not as a consumer survey, sales performance report, or clinical evaluation.",
        "- Results should be re-run periodically to track whether content and visibility interventions produce stronger benchmark signals over time.",
    ]

    if prompt_categories:
        notes.append("")
        notes.append("Query intent coverage included:")
        notes.extend(f"- {item}" for item in prompt_categories)

    return "\n".join(notes)


def get_probe_field(probe_result, field, default=""):
    if probe_result is None:
        return default

    if isinstance(probe_result, dict):
        return probe_result.get(field, default)

    return getattr(probe_result, field, default)


def format_key_value_bullets(items):
    return "\n".join(
        f"- {label}: {value}"
        for label, value in items
        if str(value or "").strip()
    )


def build_visible_market_fit_bullets(rows):
    bullets = []

    for row in rows or []:
        if not isinstance(row, dict):
            continue

        brand = str(row.get("brand", "")).strip()
        market_fit = str(row.get("market_fit", "")).strip()
        rationale = str(row.get("rationale", "")).strip()

        if not brand:
            continue

        if market_fit and rationale:
            bullets.append(f"- {brand} — {market_fit}: {rationale}")
        elif market_fit:
            bullets.append(f"- {brand} — {market_fit}")
        elif rationale:
            bullets.append(f"- {brand}: {rationale}")
        else:
            bullets.append(f"- {brand}")

    return "\n".join(bullets)
