from ui_formatters import format_display_text


def test_format_display_text_title_cases_lowercase_values():
    assert format_display_text("espresso house") == "Espresso House"
    assert format_display_text("berlin") == "Berlin"
    assert format_display_text("remote worker") == "Remote Worker"


def test_format_display_text_preserves_existing_uppercase_values():
    assert format_display_text("iS Clinical") == "iS Clinical"
    assert format_display_text("SaaS CRM") == "SaaS CRM"


def test_format_display_text_trims_and_collapses_spaces():
    assert format_display_text("  espresso   house  ") == "Espresso House"
