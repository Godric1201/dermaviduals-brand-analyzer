import pandas as pd

from ui_formatters import format_display_text, replace_target_brand_for_display


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
