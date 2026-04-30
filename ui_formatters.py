def format_display_text(value):
    value = " ".join(str(value).strip().split())

    if value.islower():
        return value.title()

    return value


def replace_target_brand_for_display(df, raw_brand, display_brand):
    display_df = df.copy()

    if "brand" not in display_df.columns:
        return display_df

    mask = display_df["brand"].astype(str).str.lower() == str(raw_brand).lower()
    display_df.loc[mask, "brand"] = display_brand

    return display_df


def translate_dataframe_columns(df):
    return df.rename(columns={
        "brand": "Brand",
        "total_mentions": "Total Mentions",
        "average_visibility_score": "Average Visibility Score",
        "prompts_visible": "Prompts Visible",
        "best_estimated_rank": "Best Estimated Rank",
        "share_of_voice_percent": "Share of Voice %",
        "analysis_timestamp": "Analysis Timestamp",
        "prompt_category": "Prompt Category",
        "prompt": "Prompt",
        "mentions": "Mentions",
        "first_position": "First Position",
        "estimated_rank": "Estimated Rank",
        "visibility_score": "Visibility Score",
        "visibility_level": "Visibility Level",
        "is_target_brand": "Is Target Brand",
        "answer": "AI Answer",
        "category": "Category",
    })


def df_to_markdown_table(df, max_rows=20):
    """
    Convert a dataframe into a simple markdown table without requiring extra packages.
    """
    if df is None or df.empty:
        return "_No data available._"

    df = df.head(max_rows).copy()

    columns = list(df.columns)

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    rows = []

    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")

    return "\n".join([header, separator] + rows)
