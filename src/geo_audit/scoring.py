import re
import pandas as pd


# -------- Basic cleanup --------
def normalize_text(text):
    return (
        str(text)
        .lower()
        .replace("-", " ")
        .replace("–", " ")
        .replace("—", " ")
        .replace("’", "'")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )


# -------- Generic aliases, without hardcoding brand-specific rules --------
def brand_aliases(brand):
    brand = str(brand).strip()

    aliases = [
        brand,
        brand.lower(),
        brand.replace("-", " "),
        brand.replace("–", " "),
        brand.replace("—", " "),
        brand.replace("’", "'"),
        brand.replace(".", ""),
        brand.replace("+", ""),
    ]

    cleaned = []
    seen = set()

    for alias in aliases:
        alias = normalize_text(alias).strip()
        if alias and alias not in seen:
            seen.add(alias)
            cleaned.append(alias)

    return cleaned


# -------- Split AI answer into lines --------
def split_answer_lines(answer):
    lines = str(answer).splitlines()
    return [line.strip() for line in lines if line.strip()]


# -------- Check whether a line is a list item --------
def is_list_item(line):
    line = line.strip()

    patterns = [
        r"^\d+[\.\)]\s+",     # 1. / 1)
        r"^[-*•]\s+",         # - / * / •
    ]

    return any(re.match(pattern, line) for pattern in patterns)


# -------- Remove numbering or bullet prefixes from list items --------
def clean_list_prefix(line):
    line = line.strip()
    line = re.sub(r"^\d+[\.\)]\s+", "", line)
    line = re.sub(r"^[-*•]\s+", "", line)
    return line.strip()


# -------- Estimate rank from numbered or bullet lists --------
def estimate_rank_from_list(answer, brand):
    lines = split_answer_lines(answer)
    rank = 0

    for line in lines:
        if not is_list_item(line):
            continue

        rank += 1
        clean_line = normalize_text(clean_list_prefix(line))

        for alias in brand_aliases(brand):
            if alias in clean_line:
                return rank

    return None


# -------- Find first brand position --------
def find_first_position(answer, brand):
    answer_text = normalize_text(answer)
    first_position = None

    for alias in brand_aliases(brand):
        pos = answer_text.find(alias)
        if pos != -1:
            if first_position is None or pos < first_position:
                first_position = pos

    return first_position


# -------- Count brand mentions --------
def count_mentions(answer, brand):
    answer_text = normalize_text(answer)
    mentions = 0

    for alias in brand_aliases(brand):
        pattern = re.escape(alias)
        mentions += len(re.findall(pattern, answer_text))

    return mentions


# -------- Score based on rank --------
def score_from_rank(rank, mentions):
    if mentions <= 0:
        return 0, "Not Visible"

    if rank == 1:
        return 100, "Top"
    elif rank == 2:
        return 90, "Strong"
    elif rank == 3:
        return 80, "Strong"
    elif rank in [4, 5]:
        return 65, "Moderate"
    elif rank is not None:
        return 45, "Weak"

    if mentions >= 3:
        return 55, "Moderate"
    elif mentions == 2:
        return 45, "Weak"
    else:
        return 35, "Weak"


# -------- Keyword + Rank scoring --------
def keyword_score(answer, brand):
    mentions = count_mentions(answer, brand)
    first_position = find_first_position(answer, brand)
    estimated_rank = estimate_rank_from_list(answer, brand)

    visibility_score, visibility_level = score_from_rank(
        estimated_rank,
        mentions
    )

    return {
        "mentions": mentions,
        "first_position": first_position,
        "estimated_rank": estimated_rank,
        "visibility_score": visibility_score,
        "visibility_level": visibility_level
    }


# -------- Main analysis --------
def analyze_answer(prompt_category, prompt, answer, brand, competitors):
    rows = []
    all_brands = [brand] + competitors

    cleaned_brands = []
    seen = set()

    for b in all_brands:
        key = normalize_text(b)
        if key not in seen:
            seen.add(key)
            cleaned_brands.append(b)

    for b in cleaned_brands:
        result = keyword_score(answer, b)

        rows.append({
            "brand": b,
            "prompt_category": prompt_category,
            "prompt": prompt,
            "mentions": result["mentions"],
            "first_position": result["first_position"],
            "estimated_rank": result["estimated_rank"],
            "visibility_score": result["visibility_score"],
            "visibility_level": result["visibility_level"],
            "is_target_brand": normalize_text(b) == normalize_text(brand)
        })

    return rows


# -------- Summary --------
def summarize_results(all_results):
    detailed_df = pd.DataFrame(all_results)

    if detailed_df.empty:
        summary_df = pd.DataFrame(columns=[
            "brand",
            "total_mentions",
            "average_visibility_score",
            "prompts_visible",
            "best_estimated_rank"
        ])
        return detailed_df, summary_df

    summary_df = detailed_df.groupby("brand").agg(
        total_mentions=("mentions", "sum"),
        average_visibility_score=("visibility_score", "mean"),
        prompts_visible=("mentions", lambda x: int((x > 0).sum())),
        best_estimated_rank=("estimated_rank", "min")
    ).reset_index()

    summary_df["average_visibility_score"] = (
        summary_df["average_visibility_score"]
        .fillna(0)
        .round(2)
    )

    summary_df["best_estimated_rank"] = (
        summary_df["best_estimated_rank"]
        .fillna(0)
    )

    return detailed_df, summary_df


# -------- Share of Voice --------
def calculate_share_of_voice(summary_df):
    total_mentions = summary_df["total_mentions"].sum()

    if total_mentions == 0:
        summary_df["share_of_voice_percent"] = 0
    else:
        summary_df["share_of_voice_percent"] = (
            summary_df["total_mentions"] / total_mentions * 100
        ).round(2)

    return summary_df
