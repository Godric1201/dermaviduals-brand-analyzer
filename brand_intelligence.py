import re

from analyzer import ask_ai
from brand_intelligence_prompts import (
    build_target_diagnostic_prompts,
    parse_user_brand_strengths,
)
from output_quality import (
    OutputQualityContext,
    sanitize_brand_intelligence_text as oq_sanitize_brand_intelligence_text,
    sanitize_claim_safety_text,
)


VALIDATION_NOTE = (
    "AI-inferred diagnostic output. Validate before using as client-facing fact."
)

SOURCE_LABEL_PATTERN = re.compile(
    r"\*?\(?\s*Source:\s*(Tracked competitor|AI-discovered market signal|Mixed tracked competitor / AI-discovered market signal)\s*\)?\*?",
    re.IGNORECASE,
)
SOURCE_LABEL_ONLY_PATTERN = re.compile(
    r"^\s*\*?\(?(?:Source:\s*(Tracked competitor|AI-discovered market signal|Mixed tracked competitor / AI-discovered market signal))\)?\*?\s*$",
    re.IGNORECASE,
)
MARKET_SIGNAL_HEADING_PATTERN = re.compile(
    r"^\s*(?:#+\s*)?(?:[-*]\s*)?AI-Discovered Market Signals Not Included in Scoring\s*:?\s*$",
    re.IGNORECASE,
)
TRACKED_COMPETITOR_HEADING_PATTERN = re.compile(
    r"^\s*(?:#+\s*)?(?:[-*]\s*)?Tracked Competitors Included in Scoring\s*:?\s*$",
    re.IGNORECASE,
)
AI_DISCOVERED_BRANDS_HEADING_PATTERN = re.compile(
    r"^\s*(?:#+\s*)?(?:[-*]\s*)?AI-Discovered Brands Not Included in Scoring\s*:?\s*$",
    re.IGNORECASE,
)
MARKET_TRENDS_HEADING_PATTERN = re.compile(
    r"^\s*(?:#+\s*)?(?:[-*]\s*)?Market Trends / Demand Signals\s*:?\s*$",
    re.IGNORECASE,
)
HEALTH_ADJACENT_TERMS = (
    "skin",
    "skincare",
    "beauty",
    "wellness",
    "medical",
    "clinic",
    "health",
    "derma",
    "cosmetic",
)
COMPETITOR_ADVANTAGE_COLUMNS = [
    "Advantage Signal",
    "Evidence Source",
    "Example Brands",
    "Source Type",
]
NON_BRAND_MARKET_SIGNAL_PATTERNS = [
    r"market research",
    r"distribution strategy",
    r"marketing campaigns?",
    r"local claims support documentation",
    r"conduct studies",
    r"explore partnerships",
    r"launch targeted campaigns?",
    r"consider conducting",
    r"demand for",
    r"interest in",
    r"increased focus",
]


def _normalize_user_brand_strengths(user_brand_strengths):
    if user_brand_strengths is None:
        return []

    if isinstance(user_brand_strengths, str):
        return parse_user_brand_strengths(user_brand_strengths)

    return list(user_brand_strengths)


def normalize_brand_name(value):
    return " ".join(str(value or "").strip().lower().split())


def is_tracked_competitor(brand_name, tracked_competitors):
    normalized_brand = normalize_brand_name(brand_name)
    normalized_tracked = {
        normalize_brand_name(item)
        for item in (tracked_competitors or [])
        if normalize_brand_name(item)
    }
    return normalized_brand in normalized_tracked


def _extract_labeled_brand_name(line):
    if "(Source:" not in line:
        return None

    bold_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*\*\*(?P<brand>[^*]+)\*\*",
        line,
    )
    if bold_match:
        return bold_match.group("brand").strip()

    plain_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*(?P<brand>[^–—:\-()]+?)\s*(?:[–—:-])",
        line,
    )
    if plain_match:
        return plain_match.group("brand").strip()

    return None


def _extract_candidate_brands_from_phrase(text):
    candidates = []

    for part in re.split(r",|\band\b|/|;", str(text or "")):
        candidate = part.strip(" -*:().")
        if not candidate:
            continue
        if not re.search(r"[A-ZÀ-ÖØ-Þ]", candidate):
            continue
        if len(candidate.split()) > 6:
            continue
        trimmed_tokens = []
        for token in candidate.split():
            if trimmed_tokens and token.islower():
                break
            if re.search(r"[A-ZÀ-ÖØ-Þ]", token) or token.lower() in {"iS", "dr."}:
                trimmed_tokens.append(token)
                continue
            if trimmed_tokens:
                break
        if trimmed_tokens:
            candidates.append(" ".join(trimmed_tokens))

    return candidates


def extract_brand_mentions_from_line(
    line,
    known_tracked_competitors,
    known_market_signal_brands=None,
):
    line_text = str(line or "")
    detected = []
    seen = set()

    def add_brand(value):
        normalized_value = normalize_brand_name(value)
        if normalized_value and normalized_value not in seen:
            seen.add(normalized_value)
            detected.append(value.strip())

    for brand in known_tracked_competitors or []:
        if re.search(re.escape(str(brand)), line_text, flags=re.IGNORECASE):
            add_brand(str(brand))

    for brand in known_market_signal_brands or []:
        if re.search(re.escape(str(brand)), line_text, flags=re.IGNORECASE):
            add_brand(str(brand))

    found_cue_brands = False
    for cue in ("such as", "like", "including"):
        cue_match = re.search(
            rf"\b{cue}\b(?P<phrase>.*?)(?:\(|[.;]|$)",
            line_text,
            flags=re.IGNORECASE,
        )
        if cue_match:
            found_cue_brands = True
            for candidate in _extract_candidate_brands_from_phrase(
                cue_match.group("phrase")
            ):
                add_brand(candidate)

    if not found_cue_brands:
        for match in re.findall(r"\*\*([^*]+)\*\*", line_text):
            add_brand(match)

    return detected


def classify_line_source(
    line,
    tracked_competitors,
    known_market_signal_brands=None,
):
    brand_mentions = extract_brand_mentions_from_line(
        line,
        tracked_competitors,
        known_market_signal_brands=known_market_signal_brands,
    )

    tracked_mentions = [
        brand_name
        for brand_name in brand_mentions
        if is_tracked_competitor(brand_name, tracked_competitors)
    ]
    non_tracked_mentions = [
        brand_name
        for brand_name in brand_mentions
        if not is_tracked_competitor(brand_name, tracked_competitors)
    ]

    if tracked_mentions and non_tracked_mentions:
        return "Mixed tracked competitor / AI-discovered market signal"
    if tracked_mentions:
        return "Tracked competitor"
    if non_tracked_mentions:
        return "AI-discovered market signal"

    return None


def classify_source_type_from_example_brands(
    example_brands,
    tracked_competitors,
    fallback_text="",
):
    fallback_lower = str(fallback_text or "").lower()

    if "user-provided" in fallback_lower:
        return "User-provided"

    if not example_brands:
        return "AI-discovered market signals"

    tracked_mentions = [
        brand_name
        for brand_name in example_brands
        if is_tracked_competitor(brand_name, tracked_competitors)
    ]
    non_tracked_mentions = [
        brand_name
        for brand_name in example_brands
        if not is_tracked_competitor(brand_name, tracked_competitors)
    ]

    if tracked_mentions and non_tracked_mentions:
        return "Mixed tracked competitors / AI-discovered market signals"
    if tracked_mentions:
        return "Tracked competitors"
    if non_tracked_mentions:
        return "AI-discovered market signals"

    return "AI-discovered market signals"


def sanitize_competitor_advantage_tables(text, tracked_competitors):
    lines = str(text or "").splitlines()
    sanitized_lines = []
    index = 0

    while index < len(lines):
        line = lines[index]
        header_parts = [part.strip() for part in line.split("|")[1:-1]]
        is_competitor_table = (
            line.strip().startswith("|")
            and header_parts
            and header_parts[0].lower() == "advantage signal"
            and any(part.lower() in {"source", "source type"} for part in header_parts)
        )

        if not is_competitor_table:
            sanitized_lines.append(line)
            index += 1
            continue

        table_lines = [line]
        index += 1
        while index < len(lines) and lines[index].strip().startswith("|"):
            table_lines.append(lines[index])
            index += 1

        sanitized_lines.append("| " + " | ".join(COMPETITOR_ADVANTAGE_COLUMNS) + " |")
        sanitized_lines.append("|---|---|---|---|")

        for row in table_lines[2:]:
            row_parts = [part.strip() for part in row.split("|")[1:-1]]
            if len(row_parts) < 2:
                continue

            if len(row_parts) >= 4:
                signal = row_parts[0]
                evidence_source = row_parts[1]
                example_brands_cell = row_parts[2]
                source_value = row_parts[3]
            else:
                signal = row_parts[0]
                evidence_source = "Diagnostic inference"
                example_brands_cell = ""
                source_value = row_parts[1]

            signal = SOURCE_LABEL_PATTERN.sub("", signal).strip()
            source_value = SOURCE_LABEL_PATTERN.sub("", source_value).strip()
            example_brands = extract_brand_mentions_from_line(
                example_brands_cell or signal,
                tracked_competitors,
            )
            example_brand_text = ", ".join(example_brands) if example_brands else "None listed"

            if not example_brands and "tracked competitor" in source_value.lower():
                evidence_source = "Diagnostic inference"

            if "user-provided" in source_value.lower() or "user-provided" in evidence_source.lower():
                evidence_source = "User-provided context"
            elif not evidence_source:
                evidence_source = "Diagnostic inference"

            source_type = classify_source_type_from_example_brands(
                example_brands,
                tracked_competitors,
                fallback_text=f"{evidence_source} {source_value}",
            )

            sanitized_lines.append(
                "| "
                + " | ".join([
                    signal,
                    evidence_source,
                    example_brand_text,
                    source_type,
                ])
                + " |"
            )

    return "\n".join(sanitized_lines)


def correct_competitor_source_labels(text, tracked_competitors):
    corrected_lines = []
    previous_context_line = ""

    for line in str(text).splitlines():
        label_match = SOURCE_LABEL_PATTERN.search(line)

        if not label_match and "source:" not in line.lower():
            if line.strip():
                previous_context_line = line
            corrected_lines.append(line)
            continue

        source_context = (
            previous_context_line
            if SOURCE_LABEL_ONLY_PATTERN.match(line.strip())
            else line
        )
        expected_label = classify_line_source(
            source_context,
            tracked_competitors,
        )

        if not expected_label:
            expected_label = (
                "AI-discovered market signal"
                if "tracked competitor" in line.lower()
                else None
            )

        if not expected_label:
            corrected_lines.append(line)
            continue

        corrected_lines.append(
            SOURCE_LABEL_PATTERN.sub(
                f"(Source: {expected_label})",
                line,
                count=1,
            )
        )

    return "\n".join(corrected_lines)
def _extract_labeled_brand_name(line):
    if "(Source:" not in line:
        return None

    bold_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*\*\*(?P<brand>[^*]+)\*\*",
        line,
    )
    if bold_match:
        return bold_match.group("brand").strip()

    plain_match = re.match(
        r"^\s*(?:[-*]|\d+[.)])\s*(?P<brand>[^:()\-]+?)\s*(?:-|:)",
        line,
    )
    if plain_match:
        return plain_match.group("brand").strip()

    return None


def _is_health_adjacent_category(category):
    normalized_category = normalize_brand_name(category)
    return any(term in normalized_category for term in HEALTH_ADJACENT_TERMS)


def sanitize_claim_safety(text, category):
    if not _is_health_adjacent_category(category):
        return str(text)

    replacements = [
        (
            r"Absence of claims support documentation, where substantiated and compliant showing product effectiveness in local skin concerns",
            "claims support documentation, consumer feedback, or expert validation for Hong Kong market claims",
        ),
        (
            r"Absence of studies demonstrating product effectiveness for common skin concerns in the local market\.?",
            "Absence of claims support documentation, consumer feedback, or expert validation for Hong Kong market claims.",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing product effectiveness in local skin concerns",
            "claims support documentation, consumer feedback, or expert validation for Hong Kong market claims",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing product effectiveness",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"Absence of claims support documentation, where substantiated and compliant validating product efficacy specific to the Hong Kong demographic\.?",
            "Absence of claims support documentation, consumer feedback, or expert validation specific to the Hong Kong market.",
        ),
        (
            r"Absence of claims support documentation, where substantiated and compliant validating product efficacy",
            "Absence of claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"Promote the efficacy of products through claims support documentation, where substantiated and compliant and consumer testimonials\.",
            "Support product claims with compliant documentation, consumer testimonials, and expert validation.",
        ),
        (
            r"Promote the efficacy of products",
            "Support product claims",
        ),
        (
            r"Professional and Clinical Endorsement",
            "Professional Trust Signals",
        ),
        (
            r"Medical-Grade Efficacy",
            "Evidence-Supported Product Positioning",
        ),
        (
            r"Clinical studies or data demonstrating product efficacy in the local context",
            "Claims support documentation, consumer feedback, or expert validation, where substantiated and compliant",
        ),
        (
            r"Clinical studies or data demonstrating product efficacy",
            "Claims support documentation, consumer feedback, or expert validation, where substantiated and compliant",
        ),
        (
            r"Clinical studies or consumer feedback validating product effectiveness",
            "Claims support documentation, consumer feedback, or expert validation, only where substantiated and compliant",
        ),
        (
            r"clinical studies or consumer feedback validating product effectiveness",
            "claims support documentation, consumer feedback, or expert validation, only where substantiated and compliant",
        ),
        (
            r"Invest in claims support documentation, only where substantiated and compliant or studies to substantiate efficacy claims",
            "Develop claims support documentation and consumer evidence where substantiated and compliant",
        ),
        (
            r"published studies demonstrating product effectiveness",
            "substantiated evidence or consumer study documentation",
        ),
        (
            r"Collaborate with local dermatologists for studies",
            "Collaborate with qualified professionals to review evidence and claims support materials",
        ),
        (
            r"Collaborate with dermatologists for clinical studies",
            "Collaborate with qualified professionals to review evidence and claims support materials",
        ),
        (
            r"Studies or data demonstrating efficacy in Hong Kong",
            "consumer feedback, expert validation, ingredient documentation, or compliant claims support",
        ),
        (
            r"Studies or data demonstrating efficacy",
            "consumer feedback, expert validation, ingredient documentation, or compliant claims support",
        ),
        (
            r"studies to substantiate efficacy claims",
            "claims support documentation where substantiated and compliant",
        ),
        (
            r"validate efficacy claims",
            "support product claims where substantiated and compliant",
        ),
        (
            r"validating product effectiveness",
            "supporting product claims where substantiated and compliant",
        ),
        (
            r"clinical validations",
            "expert validation and claims support documentation",
        ),
        (
            r"clinical trials",
            "claims support documentation, only where substantiated and compliant",
        ),
        (
            r"clinical studies",
            "claims support documentation, where substantiated and compliant",
        ),
        (
            r"clinical evidence",
            "claims support documentation and expert validation",
        ),
        (
            r"clinical data",
            "claims support documentation",
        ),
        (
            r"clinical support",
            "evidence support",
        ),
        (
            r"clinical efficacy",
            "substantiated product evidence",
        ),
        (
            r"proven effectiveness",
            "evidence-supported product claims",
        ),
        (
            r"clinically effective",
            "evidence-supported",
        ),
        (
            r"clinically proven",
            "evidence-supported",
        ),
        (
            r"medical-grade efficacy",
            "evidence-supported product positioning",
        ),
        (
            r"Strong clinical backing",
            "Strong evidence-supported positioning",
        ),
        (
            r"clinical backing",
            "evidence-supported positioning",
        ),
        (
            r"clinically backed",
            "evidence-supported",
        ),
        (
            r"clinical approach",
            "professional evidence approach",
        ),
        (
            r"clinical endorsements",
            "professional endorsements",
        ),
        (
            r"prove effectiveness",
            "support product claims",
        ),
        (
            r"medical-grade claims",
            "professional-grade positioning, where substantiated",
        ),
        (
            r"substantiated product evidence Data",
            "Claims Support Documentation",
        ),
        (
            r"showcasing ingredient efficacy",
            "showcasing ingredient documentation and claims support",
        ),
        (
            r"ingredient efficacy",
            "ingredient documentation and claims support",
        ),
    ]

    sanitized = str(text)
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    cleanup_replacements = [
        (r"where substantiated and compliant and", "where substantiated and compliant, with"),
        (r"claims support documentation, where substantiated and compliant validating", "claims support documentation, consumer feedback, or expert validation"),
        (r"substantiated product evidence Data", "Claims Support Documentation"),
        (r"product efficacy specific to the Hong Kong demographic", "product claims specific to the Hong Kong market, where substantiated and compliant"),
    ]

    for pattern, replacement in cleanup_replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def _remove_tracked_names_from_sentence(line, tracked_competitors):
    updated_line = line
    removed_any = False

    for competitor in tracked_competitors or []:
        pattern = re.compile(re.escape(str(competitor)), re.IGNORECASE)
        if pattern.search(updated_line):
            updated_line = pattern.sub("", updated_line)
            removed_any = True

    if not removed_any:
        return line

    updated_line = re.sub(r"\s*,\s*,+", ", ", updated_line)
    updated_line = re.sub(r",\s*(and\s*)?,", ", ", updated_line, flags=re.IGNORECASE)
    updated_line = re.sub(r"\s{2,}", " ", updated_line)
    updated_line = re.sub(r"\blike\s*(?:,|\band\b)?\s*", "like ", updated_line, flags=re.IGNORECASE)
    updated_line = re.sub(r"\blike\s*[.]", ".", updated_line, flags=re.IGNORECASE)
    updated_line = re.sub(r"\blike\s*$", "", updated_line, flags=re.IGNORECASE)
    updated_line = re.sub(r"\s+\.", ".", updated_line)
    updated_line = re.sub(r"\s+,", ",", updated_line)
    updated_line = updated_line.strip()

    if "Consider adding" in line and not re.search(r"[A-Za-z]{2,}", updated_line.split("like")[-1] if "like" in updated_line else ""):
        return "No additional non-tracked market signals were identified in this section."

    return updated_line


def remove_tracked_competitors_from_market_signals(text, tracked_competitors):
    lines = str(text).splitlines()
    cleaned_lines = []
    in_market_signal_section = False
    market_signal_lines = []

    def flush_market_signal_section():
        if not market_signal_lines:
            return

        brand_lines = []
        trend_lines = []

        for raw_line in market_signal_lines:
            stripped_line = raw_line.strip()
            if not stripped_line:
                continue

            if "Consider adding" in raw_line:
                updated_line = _remove_tracked_names_from_sentence(
                    raw_line,
                    tracked_competitors,
                )
                if updated_line == "No additional non-tracked market signals were identified in this section.":
                    continue
                raw_line = updated_line
                stripped_line = raw_line.strip()

            if SOURCE_LABEL_ONLY_PATTERN.match(stripped_line):
                continue

            mentioned_brands = extract_brand_mentions_from_line(
                raw_line,
                tracked_competitors,
            )

            if mentioned_brands:
                brand_lines.append(raw_line)
            else:
                trend_lines.append(raw_line)

        cleaned_lines.append("AI-Discovered Brands Not Included in Scoring")
        if brand_lines:
            cleaned_lines.extend(brand_lines)
        else:
            cleaned_lines.append("No additional non-tracked brands were identified.")

        if trend_lines:
            cleaned_lines.append("Market Trends / Demand Signals")
            cleaned_lines.extend(trend_lines)

    for line in lines:
        stripped_line = line.strip()

        if MARKET_SIGNAL_HEADING_PATTERN.match(stripped_line):
            in_market_signal_section = True
            continue

        if TRACKED_COMPETITOR_HEADING_PATTERN.match(stripped_line):
            flush_market_signal_section()
            market_signal_lines.clear()
            in_market_signal_section = False
            cleaned_lines.append(line)
            continue

        if in_market_signal_section:
            brand_name = _extract_labeled_brand_name(line)
            if brand_name and is_tracked_competitor(brand_name, tracked_competitors):
                continue
            market_signal_lines.append(line)
            continue

        cleaned_lines.append(line)

    flush_market_signal_section()

    return "\n".join(cleaned_lines)


def _is_non_brand_market_signal_line(line):
    stripped_line = str(line or "").strip()
    if not stripped_line:
        return False

    for pattern in NON_BRAND_MARKET_SIGNAL_PATTERNS:
        if re.search(pattern, stripped_line, flags=re.IGNORECASE):
            return True

    return False


def sanitize_ai_discovered_brands_sections(text, tracked_competitors):
    lines = str(text or "").splitlines()
    cleaned_lines = []
    section_mode = None
    section_buffer = []

    def flush_section():
        nonlocal section_buffer, section_mode

        if section_mode == "brands":
            valid_brand_lines = []
            for raw_line in section_buffer:
                stripped_line = raw_line.strip()
                if not stripped_line:
                    continue
                if _is_non_brand_market_signal_line(raw_line):
                    continue
                if extract_brand_mentions_from_line(raw_line, tracked_competitors):
                    valid_brand_lines.append(raw_line)

            if valid_brand_lines:
                cleaned_lines.extend(valid_brand_lines)
            else:
                cleaned_lines.append("No additional non-tracked brands were identified.")

        elif section_mode == "trends":
            for raw_line in section_buffer:
                if _is_non_brand_market_signal_line(raw_line):
                    cleaned_lines.append(raw_line)

        section_buffer = []
        section_mode = None

    for line in lines:
        stripped_line = line.strip()

        if AI_DISCOVERED_BRANDS_HEADING_PATTERN.match(stripped_line):
            flush_section()
            cleaned_lines.append("AI-Discovered Brands Not Included in Scoring")
            section_mode = "brands"
            continue

        if MARKET_TRENDS_HEADING_PATTERN.match(stripped_line):
            flush_section()
            cleaned_lines.append("Market Trends / Demand Signals")
            section_mode = "trends"
            continue

        if (
            TRACKED_COMPETITOR_HEADING_PATTERN.match(stripped_line)
            or MARKET_SIGNAL_HEADING_PATTERN.match(stripped_line)
        ):
            flush_section()
            cleaned_lines.append(line)
            continue

        if section_mode in {"brands", "trends"}:
            section_buffer.append(line)
            continue

        cleaned_lines.append(line)

    flush_section()

    return "\n".join(cleaned_lines)


def _sanitize_brand_intelligence_text(text, tracked_competitors, category):
    sanitized = correct_competitor_source_labels(text, tracked_competitors)
    sanitized = sanitize_competitor_advantage_tables(
        sanitized,
        tracked_competitors,
    )
    sanitized = remove_tracked_competitors_from_market_signals(
        sanitized,
        tracked_competitors,
    )
    sanitized = sanitize_ai_discovered_brands_sections(
        sanitized,
        tracked_competitors,
    )
    sanitized = sanitize_claim_safety(sanitized, category)
    return oq_sanitize_brand_intelligence_text(
        sanitized,
        OutputQualityContext(
            category=category,
            tracked_competitors=list(tracked_competitors or []),
        ),
    )


def sanitize_claim_safety(text, category):
    return sanitize_claim_safety_text(
        text,
        OutputQualityContext(category=category),
    )


def _dataframe_preview(df, max_rows=40):
    if df is None:
        return "No data provided."

    if hasattr(df, "empty") and df.empty:
        return "No data provided."

    if hasattr(df, "head") and hasattr(df, "to_string"):
        return df.head(max_rows).to_string(index=False)

    return str(df)


def _raw_answers_preview(raw_answers, max_items=10):
    if not raw_answers:
        return "No benchmark answers provided."

    return str(raw_answers[:max_items])


def _get_target_benchmark_visibility_context(summary_df, brand):
    if summary_df is None or getattr(summary_df, "empty", False):
        return "No benchmark visibility summary was provided."

    if "brand" not in summary_df.columns:
        return "No benchmark visibility summary was provided."

    brand_rows = summary_df[
        summary_df["brand"].astype(str).str.lower() == str(brand).lower()
    ]

    if brand_rows.empty:
        return f"No benchmark summary row was found for {brand}."

    row = brand_rows.iloc[0]

    mentions = row.get("total_mentions", 0)
    average_visibility = row.get("average_visibility_score", 0)
    prompts_visible = row.get("prompts_visible", 0)
    share_of_voice = row.get("share_of_voice_percent", 0)

    return (
        f"Unbranded benchmark visibility for {brand}: "
        f"{mentions} total mentions, "
        f"{average_visibility} average visibility score, "
        f"{prompts_visible} prompts visible, "
        f"{share_of_voice}% share of voice."
    )


def build_recommendation_driver_prompt(
    brand,
    category,
    market,
    audience,
    competitors,
    raw_answers,
    summary_df,
    detailed_df,
):
    return f"""
You are analyzing benchmark AI answers for Brand Intelligence and Positioning Gap Analysis.

This analysis is derived from benchmark answers; not a visibility score.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Competitors:
{", ".join(competitors)}

Summary Data:
{_dataframe_preview(summary_df)}

Detailed Data:
{_dataframe_preview(detailed_df)}

Benchmark Raw Answers:
{_raw_answers_preview(raw_answers)}

Task:
Extract the recurring recommendation drivers that appear in the benchmark answers.

Return:
- Top 5 recurring recommendation drivers
- Top 5 competitor advantage signals in a markdown table with these exact columns:
  Advantage Signal | Evidence Source | Example Brands | Source Type
- Evidence patterns from benchmark answers
- Unmet query intents
- Tracked Competitors Included in Scoring
- AI-Discovered Market Signals Not Included in Scoring
- Do not label abstract advantage signals directly as tracked competitors
- Source Type must depend on Example Brands

Format:
- Prefer compact tables or bullet lists over long paragraphs.
- Clearly label each signal as Benchmark-derived, AI-inferred, or User-provided where relevant.

Rules:
- Do not treat this as a scoring calculation.
- Do not create visibility scores, share of voice, or rankings.
- Treat competitors listed above as tracked competitors used for benchmark scoring.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not list tracked competitors as AI-discovered market signals.
- Before suggesting a brand for the next benchmark run, verify it is not already in the tracked competitor list.
- If no non-tracked brands are available, say no additional non-tracked market signals were identified.
- For Competitor Advantage Signals, use the schema Advantage Signal | Evidence Source | Example Brands | Source Type.
- Evidence Source must be Benchmark answers, Diagnostic inference, or User-provided context.
- Source Type must be Tracked competitors, AI-discovered market signals, Mixed tracked competitors / AI-discovered market signals, or User-provided.
- If other brands appear in raw answers, describe them as AI-discovered market signals only.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Do not call non-tracked brands competitors included in benchmark.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
- Avoid unsupported factual claims.
- Label uncertain observations clearly.
""".strip()


def build_target_understanding_prompt(
    brand,
    category,
    market,
    audience,
    diagnostic_answers,
    benchmark_visibility_context,
):
    return f"""
You are synthesizing target-brand diagnostic answers for Brand Intelligence and Positioning Gap Analysis.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Benchmark Visibility Context:
{benchmark_visibility_context}

Diagnostic Answers:
{diagnostic_answers}

Task:
Summarize how AI appears to understand the target brand.

Return:
- AI-inferred strengths
- Weak associations
- Missing evidence
- Uncertainties
- Prompted Diagnostic Fit
- Top competitor-owned associations
- Tracked Competitors Included in Scoring
- AI-Discovered Market Signals Not Included in Scoring
- Action implications

Format:
- Prefer compact tables or bullet lists over long paragraphs.
- Clearly label signals as Benchmark-derived, AI-inferred, or User-provided where relevant.

Rules:
- AI-inferred; validate before using as client-facing fact.
- Distinguish inferred observations from verified facts.
- Natural benchmark visibility comes from the unbranded benchmark.
- Prompted diagnostic fit is a target-branded diagnostic assessment requiring validation.
- Distinguish tracked competitors from AI-discovered market signals.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not list tracked competitors as AI-discovered market signals.
- Before suggesting a brand for the next benchmark run, verify it is not already in the tracked competitor list.
- If no non-tracked brands are available, say no additional non-tracked market signals were identified.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
- If the benchmark shows 0 mentions or 0 share of voice, describe fit as potential, prompted, or subject to validation, not as natural recommendation visibility.
- Avoid unsupported factual claims.
""".strip()


def build_positioning_gap_prompt(
    brand,
    category,
    market,
    audience,
    recommendation_drivers,
    target_brand_understanding,
    user_brand_strengths,
):
    return f"""
You are creating a positioning gap analysis for Brand Intelligence.

Target Brand:
{brand}

Category:
{category}

Market:
{market}

Audience:
{audience}

Recommendation Drivers:
{recommendation_drivers}

Target Brand Understanding:
{target_brand_understanding}

User-Provided Brand Strengths:
{user_brand_strengths}

Task:
Compare category recommendation drivers, competitor advantage signals, AI-inferred target brand understanding, and user-provided brand strengths.

Return:
- Missing associations
- For each missing association include:
  - Association
  - Source: benchmark-derived / AI-inferred / user-provided
  - Why It Matters
  - Evidence Needed
  - Recommended Action
- Strongest opportunity territories
- Review / Trust Signal Gaps
- Content priorities
- PR / trust signal priorities
- Recommended next steps

Rules:
- Prefer compact tables or bullet lists over long paragraphs.
- Do not produce unsupported factual claims.
- Label AI-inferred findings clearly.
- Clearly label each signal as Benchmark-derived, AI-inferred, or User-provided.
- Distinguish tracked competitors from AI-discovered market signals.
- The tracked competitor list is the only source of truth for Source: Tracked competitor.
- Never label a non-tracked brand as Source: Tracked competitor.
- Do not list tracked competitors as AI-discovered market signals.
- Before suggesting a brand for the next benchmark run, verify it is not already in the tracked competitor list.
- If no non-tracked brands are available, say no additional non-tracked market signals were identified.
- Do not imply AI-discovered market signals are included in visibility scoring unless they are tracked competitors.
- Include separate sections titled Tracked Competitors Included in Scoring and AI-Discovered Market Signals Not Included in Scoring where relevant.
- If non-tracked brands are mentioned, label them as Source: AI-discovered market signal.
- Prefer tracked competitors first when listing competitor signals.
- Consider adding these brands as tracked competitors before the benchmark run if they are strategically relevant.
- Do not call non-tracked brands competitors included in benchmark.
- Treat user-provided strengths as client-provided notes that still need evidence.
- Avoid generic advice unless it is tied to a benchmark driver, competitor signal, or evidence gap.
- Do not create or modify visibility scores, share of voice, or rankings.
""".strip()


def run_brand_intelligence_analysis(
    brand,
    category,
    market,
    audience,
    competitors,
    raw_answers,
    summary_df,
    detailed_df,
    user_brand_strengths=None,
    answer_language="English",
    report_language="English",
    on_progress=None,
):
    user_brand_strengths = _normalize_user_brand_strengths(user_brand_strengths)

    diagnostic_prompts = build_target_diagnostic_prompts(
        brand=brand,
        category=category,
        market=market,
        audience=audience,
        competitors=competitors,
        user_brand_strengths=user_brand_strengths,
    )

    if on_progress is not None:
        on_progress("diagnostic_prompts")

    diagnostic_answers = []

    for item in diagnostic_prompts:
        answer = ask_ai(item["prompt"], answer_language)
        diagnostic_answers.append({
            "category": item["category"],
            "prompt": item["prompt"],
            "answer": answer,
        })

    if on_progress is not None:
        on_progress("recommendation_drivers")

    recommendation_drivers = ask_ai(
        build_recommendation_driver_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            competitors=competitors,
            raw_answers=raw_answers,
            summary_df=summary_df,
            detailed_df=detailed_df,
        ),
        report_language,
    )
    recommendation_drivers = _sanitize_brand_intelligence_text(
        recommendation_drivers,
        competitors,
        category,
    )

    if on_progress is not None:
        on_progress("target_understanding")

    target_brand_understanding = ask_ai(
        build_target_understanding_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            diagnostic_answers=diagnostic_answers,
            benchmark_visibility_context=_get_target_benchmark_visibility_context(
                summary_df,
                brand,
            ),
        ),
        report_language,
    )
    target_brand_understanding = _sanitize_brand_intelligence_text(
        target_brand_understanding,
        competitors,
        category,
    )

    if on_progress is not None:
        on_progress("positioning_gap")

    positioning_gap_analysis = ask_ai(
        build_positioning_gap_prompt(
            brand=brand,
            category=category,
            market=market,
            audience=audience,
            recommendation_drivers=recommendation_drivers,
            target_brand_understanding=target_brand_understanding,
            user_brand_strengths=user_brand_strengths,
        ),
        report_language,
    )
    positioning_gap_analysis = _sanitize_brand_intelligence_text(
        positioning_gap_analysis,
        competitors,
        category,
    )

    return {
        "diagnostic_prompts": diagnostic_prompts,
        "diagnostic_answers": diagnostic_answers,
        "recommendation_drivers": recommendation_drivers,
        "target_brand_understanding": target_brand_understanding,
        "positioning_gap_analysis": positioning_gap_analysis,
        "user_brand_strengths": user_brand_strengths,
        "validation_note": VALIDATION_NOTE,
    }
