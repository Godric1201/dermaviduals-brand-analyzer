from app_constants import CLIENT_PRESETS


def test_client_presets_have_expected_shape():
    required_keys = {
        "brand",
        "category",
        "market",
        "audience",
        "competitors",
    }

    assert "Custom" not in CLIENT_PRESETS

    for preset in CLIENT_PRESETS.values():
        assert set(preset) == required_keys
        assert preset["brand"]
        assert preset["category"]
        assert preset["market"]
        assert preset["audience"]
        assert isinstance(preset["competitors"], list)
        assert preset["competitors"]
