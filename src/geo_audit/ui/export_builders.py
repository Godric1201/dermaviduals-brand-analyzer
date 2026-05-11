import pandas as pd

from geo_audit.ui_formatters import (
    format_brand_names_for_display,
    replace_target_brand_for_display,
)


def build_markdown_top_brands_display_df(top_brands, brand, display_brand):
    if not top_brands.empty:
        return replace_target_brand_for_display(
            format_brand_names_for_display(
                top_brands[["prompt_category", "brand", "visibility_score"]]
            ),
            raw_brand=brand,
            display_brand=display_brand
        )

    return pd.DataFrame(columns=["prompt_category", "brand", "visibility_score"])


def build_docx_top_brands_display_df(top_brands, brand, display_brand):
    if not top_brands.empty:
        return replace_target_brand_for_display(
            format_brand_names_for_display(top_brands),
            raw_brand=brand,
            display_brand=display_brand
        )

    return top_brands
