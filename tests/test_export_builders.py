import pandas as pd

from geo_audit.ui.export_builders import (
    build_docx_top_brands_display_df,
    build_markdown_top_brands_display_df,
)


def test_build_markdown_top_brands_display_df_selects_report_columns_only():
    top_brands = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "espresso house",
            "visibility_score": 2,
            "extra_column": "not exported",
        }
    ])

    display_df = build_markdown_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )

    assert list(display_df.columns) == [
        "prompt_category",
        "brand",
        "visibility_score",
    ]
    assert display_df.iloc[0]["brand"] == "Espresso House"


def test_build_markdown_top_brands_display_df_returns_expected_empty_columns():
    top_brands = pd.DataFrame(
        columns=["prompt_category", "brand", "visibility_score", "extra_column"]
    )

    display_df = build_markdown_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )

    assert display_df.empty
    assert list(display_df.columns) == [
        "prompt_category",
        "brand",
        "visibility_score",
    ]


def test_build_docx_top_brands_display_df_preserves_additional_columns():
    top_brands = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "coffee fellows",
            "visibility_score": 2,
            "extra_column": "kept",
        }
    ])

    display_df = build_docx_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )

    assert list(display_df.columns) == [
        "prompt_category",
        "brand",
        "visibility_score",
        "extra_column",
    ]
    assert display_df.iloc[0]["brand"] == "Coffee Fellows"
    assert display_df.iloc[0]["extra_column"] == "kept"


def test_build_docx_top_brands_display_df_returns_empty_dataframe_unchanged():
    top_brands = pd.DataFrame(
        columns=["prompt_category", "brand", "visibility_score", "extra_column"]
    )

    display_df = build_docx_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )

    assert display_df is top_brands
    assert display_df.empty
    assert list(display_df.columns) == [
        "prompt_category",
        "brand",
        "visibility_score",
        "extra_column",
    ]


def test_top_brand_display_replacement_works_for_both_helpers():
    top_brands = pd.DataFrame([
        {
            "prompt_category": "Best Options",
            "brand": "espresso house",
            "visibility_score": 2,
        }
    ])

    markdown_df = build_markdown_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )
    docx_df = build_docx_top_brands_display_df(
        top_brands,
        brand="espresso house",
        display_brand="Espresso House",
    )

    assert markdown_df.iloc[0]["brand"] == "Espresso House"
    assert docx_df.iloc[0]["brand"] == "Espresso House"
