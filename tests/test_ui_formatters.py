import pandas as pd

from ui_formatters import (
    build_export_filename,
    format_brand_names_for_display,
    format_display_text,
    replace_target_brand_for_display,
    slugify_filename_part,
)


def test_format_display_text_title_cases_lowercase_values():
    assert format_display_text("espresso house") == "Espresso House"
    assert format_display_text("berlin") == "Berlin"
    assert format_display_text("remote worker") == "Remote Worker"


def test_format_display_text_preserves_existing_uppercase_values():
    assert format_display_text("iS Clinical") == "iS Clinical"
    assert format_display_text("SaaS CRM") == "SaaS CRM"


def test_format_display_text_trims_and_collapses_spaces():
    assert format_display_text("  espresso   house  ") == "Espresso House"


def test_replace_target_brand_for_display_updates_target_without_mutating_original():
    df = pd.DataFrame([
        {"brand": "espresso house", "score": 1},
        {"brand": "starbuks", "score": 2},
    ])

    result = replace_target_brand_for_display(
        df,
        raw_brand="espresso house",
        display_brand="Espresso House",
    )

    assert result.loc[0, "brand"] == "Espresso House"
    assert result.loc[1, "brand"] == "starbuks"
    assert df.loc[0, "brand"] == "espresso house"


def test_replace_target_brand_for_display_matches_case_insensitively():
    df = pd.DataFrame([
        {"brand": "ESPRESSO HOUSE", "score": 1},
    ])

    result = replace_target_brand_for_display(
        df,
        raw_brand="espresso house",
        display_brand="Espresso House",
    )

    assert result.loc[0, "brand"] == "Espresso House"


def test_replace_target_brand_for_display_handles_missing_brand_column():
    df = pd.DataFrame([
        {"name": "espresso house", "score": 1},
    ])

    result = replace_target_brand_for_display(
        df,
        raw_brand="espresso house",
        display_brand="Espresso House",
    )

    assert result.equals(df)
    assert result is not df


def test_format_brand_names_for_display_formats_competitors_without_mutating_original():
    df = pd.DataFrame([
        {"brand": "coffee fellows", "score": 1},
        {"brand": "einstein kaffee", "score": 2},
        {"brand": "starbuks", "score": 3},
        {"brand": "iS Clinical", "score": 4},
    ])

    result = format_brand_names_for_display(df)

    assert result["brand"].tolist() == [
        "Coffee Fellows",
        "Einstein Kaffee",
        "Starbuks",
        "iS Clinical",
    ]
    assert df["brand"].tolist() == [
        "coffee fellows",
        "einstein kaffee",
        "starbuks",
        "iS Clinical",
    ]


def test_format_brand_names_for_display_handles_missing_brand_column():
    df = pd.DataFrame([
        {"name": "coffee fellows", "score": 1},
    ])

    result = format_brand_names_for_display(df)

    assert result.equals(df)
    assert result is not df


def test_build_export_filename_uses_brand_market_and_export_type():
    filename = build_export_filename(
        "Espresso House",
        "Berlin",
        "summary",
        "csv",
    )

    assert filename == "espresso_house_berlin_summary.csv"


def test_build_export_filename_marks_quick_test_mode():
    filename = build_export_filename(
        "Espresso House",
        "Berlin",
        "summary",
        "csv",
        run_mode="Quick Test Mode",
    )

    assert filename == "espresso_house_berlin_quick_test_summary.csv"


def test_build_export_filename_does_not_mark_full_report_mode():
    filename = build_export_filename(
        "Espresso House",
        "Berlin",
        "summary",
        "csv",
        run_mode="Full Report Mode",
    )

    assert "quick_test" not in filename


def test_slugify_filename_part_handles_unsafe_chars():
    assert slugify_filename_part('Espresso/House: "Berlin"*') == "espresso_house_berlin"


def test_build_export_filename_does_not_correct_typos():
    filename = build_export_filename(
        "starbuks",
        "berlin",
        "summary",
        "csv",
    )

    assert filename == "starbuks_berlin_summary.csv"
