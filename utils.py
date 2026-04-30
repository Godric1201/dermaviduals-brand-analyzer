import pandas as pd
from datetime import datetime
import re


def clean_competitors(text):
    """
    Clean competitor text into a unique list.
    Kept for future flexibility, even though the current app uses predefined competitors.
    """
    if isinstance(text, list):
        return [str(c).strip() for c in text if str(c).strip()]

    if not text:
        return []

    text = str(text)
    text = text.replace("\n", ",")
    text = re.sub(r"^\s*[-*\d.]+\s*", "", text, flags=re.MULTILINE)

    competitors = []

    for item in text.split(","):
        item = item.strip()
        item = item.replace("-", "").replace("*", "").strip()

        if item and len(item) <= 60:
            competitors.append(item)

    seen = set()
    cleaned = []

    for c in competitors:
        key = c.lower()

        if key not in seen:
            seen.add(key)
            cleaned.append(c)

    return cleaned[:10]


def add_timestamp(df):
    """
    Add analysis timestamp without mutating the original dataframe.
    """
    df = df.copy()
    df["analysis_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df


def convert_df_to_csv(df):
    """
    Convert dataframe to UTF-8-SIG CSV for Excel compatibility.
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def create_raw_answer_dataframe(raw_answers):
    """
    Convert raw AI answers into dataframe.
    """
    return pd.DataFrame(raw_answers)