from dataclasses import dataclass
import copy
import re


@dataclass
class OutputQualityContext:
    category: str | None = None
    run_mode: str | None = None
    brand: str | None = None
    market: str | None = None
    audience: str | None = None
    tracked_competitors: list[str] | None = None
    target_brand_metrics: dict | None = None


@dataclass
class OutputQualityIssue:
    code: str
    message: str
    severity: str = "error"
    section: str | None = None
    phrase: str | None = None


FAILED_LLM_SECTION_PLACEHOLDER = (
    "This section could not be generated because the LLM request failed. Re-run the report."
)

RAW_ERROR_OUTPUT_PATTERNS = (
    r"^\s*ERROR\s*:",
    r"\bConnection error\.?\b",
    r"\bAPIConnectionError\b",
    r"\bRateLimitError\b",
    r"\bAuthenticationError\b",
    r"\bTraceback\b",
    r"\bException\s*:",
    r"\bNoneType\b",
    r"\bOpenAI\b",
)


HEALTH_ADJACENT_CATEGORY_TERMS = (
    "skincare",
    "skin care",
    "beauty",
    "cosmetics",
    "wellness",
    "health",
    "medical",
    "dermatology",
    "aesthetic",
    "clinical",
    "supplement",
    "nutrition",
)

FORBIDDEN_CLAIM_PHRASES = (
    "clinical backing",
    "clinically proven",
    "clinical-grade",
    "medical-grade efficacy",
    "medical-grade",
    "product efficacy",
    "showing efficacy",
    "ingredient efficacy",
    "product effectiveness",
    "validate product claims",
    "clinical collaboration",
    "clinical studies",
    "clinical evidence",
    "clinical data",
    "clinical validations",
    "efficacy claims",
    "proven results",
    "clinical trial",
    "clinical trials",
    "clinically backed",
    "clinic-grade",
    "clinical results",
    "scientifically-backed",
    "scientific backing",
    "visible results",
    "dermatologist-recommended",
    "efficacy",
    "effectiveness",
)

FORBIDDEN_BUSINESS_KPI_PATTERNS = (
    r"conversion rate",
    r"\brevenue\b",
    r"\bsales\b",
    r"session duration",
    r"engagement rate",
    r"traffic increase",
    r"increase by \d+(?:\.\d+)?%",
    r"boost by \d+(?:\.\d+)?%",
    r"capture \d+(?:\.\d+)?% share of voice",
    r"reach \d+(?:\.\d+)?% share of voice",
    r"achieve \d+(?:\.\d+)?% share of voice",
    r"target \d+(?:\.\d+)?% share of voice",
    r"at least \d+(?:\.\d+)?% share of voice",
    r"goal of achieving at least \d+(?:\.\d+)?% share of voice",
    r"goal of achieving \d+(?:\.\d+)?% share of voice",
    r"share of voice above \d+(?:\.\d+)?%?",
    r"share of voice over \d+(?:\.\d+)?%?",
    r"SOV above \d+(?:\.\d+)?%?",
    r"aim for at least \d+\s*(?:-\s*\d+)? mentions",
    r"at least \d+\s*(?:-\s*\d+)? detectable mentions",
    r"at least \d+\s*(?:-\s*\d+)? mentions",
    r"visible in at least \d+\s*(?:-\s*\d+)? prompt categories",
    r"move toward being visible in \d+\s*-\s*\d+ relevant prompt categories",
    r"achieve visibility in \d+\s*-\s*\d+ relevant prompt categories",
    r"achieve initial mentions",
    r"visibility score above \d+(?:\.\d+)?%?",
    r"average visibility score above \d+(?:\.\d+)?%?",
    r"increase average visibility score to above \d+(?:\.\d+)?%?",
    r"increase visibility score above \d+(?:\.\d+)?%?",
    r"improve visibility score above \d+(?:\.\d+)?%?",
    r"goal of achieving begin generating detectable mentions",
    r"guarantee",
)

INVALID_AI_DISCOVERED_BRAND_BULLET_PATTERNS = (
    r"\beducation\b",
    r"\btestimonial(?:s)?\b",
    r"\bcollect testimonials?\b",
    r"\bvalidation\b",
    r"\bvalidation efforts?\b",
    r"\bcollection\b",
    r"\bfeedback\b",
    r"\buser feedback\b",
    r"\buser feedback collection\b",
    r"\buser-generated content\b",
    r"\buser generated content\b",
    r"\bconsumer education\b",
    r"\bconsumer engagement\b",
    r"\buser engagement\b",
    r"\binfluencer engagement\b",
    r"\bengagement\b",
    r"\befforts?\b",
    r"\binitiative\b",
    r"\binitiatives\b",
    r"\bcampaigns?\b",
    r"\bresearch\b",
    r"\banalysis\b",
    r"\bcontent\b",
    r"\bcontent strategy\b",
    r"\bcontent marketing\b",
    r"\bpartnerships?\b",
    r"\bstrategy\b",
    r"\broadmap\b",
    r"\brecommendation\b",
    r"\brecommendations\b",
    r"\boptimization\b",
    r"\boptimisation\b",
    r"\bawareness\b",
    r"\boutreach\b",
    r"\bcommunity\b",
    r"\btraining\b",
    r"\bworkshops?\b",
    r"\bwebinars?\b",
    r"\bdocumentation\b",
    r"\bmarket research\b",
    r"\bdistribution strategy\b",
    r"\bmarketing campaigns?\b",
    r"\bevidence building\b",
    r"\blocal claims support documentation\b",
    r"\btrend of\b",
    r"\bincreased focus\b",
    r"\binterest in\b",
    r"\bdemand for\b",
    r"\bcompetitive analysis\b",
    r"\bconduct studies\b",
    r"\bexplore partnerships\b",
    r"\blaunch targeted campaigns?\b",
    r"\bconsider conducting\b",
    r"\bclinical collaboration\b",
    r"\bmarket awareness\b",
    r"\bprogram\b",
    r"\bsystem\b",
    r"\bprocess\b",
    r"\bmonitor competitors?\b",
    r"\bmonitoring competitors?\b",
    r"\bcompetitor monitoring\b",
    r"\bbrand positioning\b",
    r"\bpositioning\b",
    r"\bmarketing strategies?\b",
    r"\benhance marketing strategies?\b",
    r"\badditional brands\b",
    r"\bconsider adding brands\b",
    r"\bbrands like\b",
    r"\bhighlight amenities\b",
    r"\bamenities\b",
    r"\bcommunicate wi-?fi quality\b",
    r"\bwork-friendly features\b",
    r"\bmarketing materials\b",
)

ACTION_ENTITY_START_RE = re.compile(
    r"^(?:add|assess|audit|benchmark|build|collect|communicate|compare|conduct|"
    r"consider|create|develop|educate|engage|enhance|evaluate|expand|explore|"
    r"feature|gather|highlight|identify|improve|increase|launch|monitor|"
    r"optimize|optimise|partner|promote|publish|review|showcase|support|"
    r"track|validate)\b",
    re.IGNORECASE,
)

GENERIC_ACTION_ENTITY_NOUN_RE = re.compile(
    r"\b(?:action|actions|advantage|advantages|amenities|analysis|associations|"
    r"awareness|benchmark|campaign|campaigns|collection|community|competitor|"
    r"competitors|content|documentation|education|effort|efforts|engagement|"
    r"evidence|feedback|initiative|initiatives|marketing|materials|monitoring|"
    r"partnership|partnerships|positioning|program|recommendation|"
    r"recommendations|research|roadmap|strategy|strategies|survey|system|task|"
    r"testimonial|testimonials|validation|visibility)\b",
    re.IGNORECASE,
)

WRAPPER_ENTITY_RE = re.compile(
    r"\b(?:additional brands|other brands|non-tracked brands|market signals|"
    r"brand examples|example brands|benchmark brands)\b",
    re.IGNORECASE,
)

ACTION_TASK_LINE_RE = re.compile(
    r"\b(?:consider adding|gain deeper insights|competitive advantages|"
    r"marketing materials|work-friendly features|clearly communicate|keep an eye|"
    r"gather feedback|collect testimonials|build trust|enhance marketing|"
    r"benchmark against|monitor competitors)\b",
    re.IGNORECASE,
)

BRAND_LEGAL_SUFFIX_RE = re.compile(
    r"\b(?:gmbh|inc\.?|ltd\.?|llc|co\.?|corp\.?|company|group|plc)\b",
    re.IGNORECASE,
)

BRAND_SYMBOL_RE = re.compile(r"(?:&|\+|\.com\b|\.io\b|\.ai\b|\.)", re.IGNORECASE)

QUICK_TEST_TARGET_LANGUAGE_RE = re.compile(
    r"\b(?:aim|aiming|target|goal|benchmark target|achieve|reach|increase|improve|"
    r"raise|lift|move from|generate|gain|establish|capture|visible in|"
    r"visibility in|mentions from|conservative targets?|expected ai visibility effect|"
    r"expected visibility effect|next benchmark target|should improve|should increase|"
    r"designed to improve|to improve|to increase|expected metric impact|begin to capture)\b",
    re.IGNORECASE,
)

QUICK_TEST_NUMERIC_TARGET_RE = re.compile(
    r"(?:\d+(?:\.\d+)?%|\b\d+\s*-\s*\d+\b|\b\d+\.\d+\b|"
    r"\bat least\s+\d+|\babove\s+\d+|\bfrom\s+\d+(?:\.\d+)?\s+to\s+\d+)",
    re.IGNORECASE,
)

BUSINESS_TARGET_RE = re.compile(
    r"\b(?:revenue|sales|conversion|conversion rate|session duration|engagement rate|traffic)\b",
    re.IGNORECASE,
)

CURRENT_STATE_DIAGNOSTIC_RE = re.compile(
    r"\b(?:currently|records|with 0 total mentions|has 0 mentions|0 total mentions|"
    r"0\.0 average visibility|0 prompts visible|0% share of voice|"
    r"leaving the brand at 0% share of voice|currently not visible|"
    r"not visible across the tested|no benchmark competitor generated measurable visibility)\b",
    re.IGNORECASE,
)

EXPLICIT_FUTURE_TARGET_RE = re.compile(
    r"\b(?:aim|aiming|target|goal|expected|next benchmark|conservative targets?|"
    r"should improve|should increase|designed to improve|to improve|to increase|"
    r"achieve|reach|gain|generate|establish|capture|move from|increase from|"
    r"begin to capture)\b",
    re.IGNORECASE,
)

KNOWN_TARGET_ARTIFACT_RE = re.compile(
    r"\b(?:aim for begin generating|aiming for begin generating|increase begin generating|"
    r"improve begin generating|a begin generating)\b",
    re.IGNORECASE,
)

AI_DISCOVERED_BRANDS_HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:[-*]\s*)?"
    r"(?:AI-Discovered Brands Not Included in Scoring|"
    r"AI-Discovered Market Signals Not Included in Scoring)\s*:?\s*$",
    re.IGNORECASE,
)

MARKET_TRENDS_HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:[-*]\s*)?Market Trends / Demand Signals\s*:?\s*$",
    re.IGNORECASE,
)

TRACKED_COMPETITORS_HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:[-*]\s*)?Tracked Competitors Included in Scoring\s*:?\s*$",
    re.IGNORECASE,
)

SECTION_HEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+|[A-Z][^|]{0,90}:?\s*$)")
MARKDOWN_HORIZONTAL_RULE_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")


def normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def is_raw_error_output(value: str | None) -> bool:
    if value is None:
        return False

    text = str(value)
    if not text.strip():
        return False

    return any(
        re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in RAW_ERROR_OUTPUT_PATTERNS
    )


def is_quick_test_mode(run_mode: str | None) -> bool:
    normalized = normalize_text(run_mode)
    return normalized in {
        "quick test mode",
        "quick test",
        "quick_test",
        "quick",
    }


def guard_generated_section_text(
    value: str | None,
    context: OutputQualityContext | None = None,
    module_name: str = "Generated section",
) -> str | None:
    if not is_raw_error_output(value):
        return value

    context = context or OutputQualityContext()
    if is_quick_test_mode(context.run_mode):
        return FAILED_LLM_SECTION_PLACEHOLDER

    raise ValueError(
        f"{module_name} could not be generated because the LLM request failed. "
        "Re-run the report."
    )


def _tracked_set(tracked_competitors):
    return {
        normalize_text(item)
        for item in (tracked_competitors or [])
        if normalize_text(item)
    }


def _is_tracked_brand(value, tracked_competitors):
    return normalize_text(value) in _tracked_set(tracked_competitors)


def is_health_adjacent_category(category: str | None) -> bool:
    normalized = normalize_text(category)
    return any(term in normalized for term in HEALTH_ADJACENT_CATEGORY_TERMS)


def _apply_replacements(text, replacements):
    sanitized = str(text or "")
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def dedupe_empty_section_placeholders(text: str) -> str:
    placeholders = {
        "No additional non-tracked brands were identified.",
        "No additional non-tracked market signals were identified.",
    }
    lines = str(text or "").splitlines()
    result = []
    seen_in_scope = set()

    for line in lines:
        stripped = line.strip()

        if (
            AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped)
            or MARKET_TRENDS_HEADING_RE.match(stripped)
            or TRACKED_COMPETITORS_HEADING_RE.match(stripped)
            or re.match(r"^\s*#{1,6}\s+", line)
            or MARKDOWN_HORIZONTAL_RULE_RE.match(line)
        ):
            seen_in_scope = set()

        if stripped in placeholders:
            if stripped in seen_in_scope:
                continue
            seen_in_scope.add(stripped)

        result.append(line)

    return "\n".join(result)


def _sanitize_malformed_claim_sentences(text: str) -> str:
    sanitized = str(text or "")

    sentence_rewrites = [
        (
            r"(?P<prefix>^\s*(?:[-*]\s+|\d+[.)]\s*)?)"
            r"[^.\n]*Research studies or claims support documentation, where substantiated and compliant[^.\n]*\.?",
            r"\g<prefix>Claims support documentation, consumer feedback, or expert validation.",
        ),
        (
            r"(?P<prefix>^\s*(?:[-*]\s+|\d+[.)]\s*)?)"
            r"[^.\n]*Publishing results from claims support documentation, where substantiated and compliant[^.\n]*\.?",
            r"\g<prefix>Publish compliant claims support documentation, consumer feedback, or expert validation where available.",
        ),
        (
            r"(?P<prefix>^\s*(?:[-*]\s+|\d+[.)]\s*)?)"
            r"[^.\n]*claims support documentation, where substantiated and compliant supporting product claims[^.\n]*\.?",
            r"\g<prefix>Claims support documentation, consumer feedback, or expert validation.",
        ),
        (
            r"(?P<prefix>^\s*(?:[-*]\s+|\d+[.)]\s*)?)"
            r"[^.\n]*claims support documentation, where substantiated and compliant or research[^.\n]*\.?",
            r"\g<prefix>Claims support documentation, consumer feedback, or expert validation.",
        ),
        (
            r"(?P<prefix>^\s*(?:[-*]\s+|\d+[.)]\s*)?)"
            r"[^.\n]*claims support documentation, where substantiated and compliant Data[^.\n]*\.?",
            r"\g<prefix>Claims support documentation and supporting evidence.",
        ),
    ]

    for pattern, replacement in sentence_rewrites:
        sanitized = re.sub(
            pattern,
            replacement,
            sanitized,
            flags=re.IGNORECASE | re.MULTILINE,
        )

    heading_rewrites = [
        (
            r"(?m)^(\s*(?:#{1,6}\s*)?)Evidence of Effectiveness\s*$",
            r"\1Evidence Support",
        ),
        (
            r"(?m)^(\s*(?:[-*]\s+|\d+[.)]\s*)?)Evidence of Effectiveness\s*[:\-–—]?\s*$",
            r"\1Evidence Support",
        ),
    ]

    for pattern, replacement in heading_rewrites:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    phrase_rewrites = [
        (
            r"claims support documentation, where substantiated and compliant showing product effectiveness in local skin concerns",
            "claims support documentation, consumer feedback, or expert validation for Hong Kong market claims",
        ),
        (
            r"claims support documentation, consumer feedback, or expert validation in local skin concerns",
            "claims support documentation, consumer feedback, or expert validation for Hong Kong market claims",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing efficacy",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing product effectiveness",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant supporting product claims",
            "Claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"business outcomes Performance Metrics",
            "market performance indicators",
        ),
        (
            r"business outcome Performance Metrics",
            "market performance indicators",
        ),
        (
            r"claims support documentation, where substantiated and compliant Data",
            "Claims support documentation and supporting evidence",
        ),
        (
            r"claims support documentation, where substantiated and compliant data",
            "claims support documentation and supporting evidence",
        ),
        (
            r"where substantiated and compliant showing",
            "supported by",
        ),
        (
            r"where substantiated and compliant product claims",
            "product claims, where substantiated and compliant",
        ),
    ]

    for pattern, replacement in phrase_rewrites:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def sanitize_claim_safety_text(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    context = context or OutputQualityContext()
    if not is_health_adjacent_category(context.category):
        return str(text or "")

    sanitized = _sanitize_malformed_claim_sentences(str(text or ""))

    replacements = [
        (r"Clinical Study References", "Claims Support Documentation"),
        (
            r"Pollution Defense:\s*How (?P<brand>[^|\n]+?) Protects Your Skin",
            r"\g<brand> Ingredient Guide for Pollution-Exposed Skin",
        ),
        (
            r"The Science Behind (?P<brand>[^|\n]+?) for Skin Health",
            r"\g<brand> Professional Trust Signals and Ingredient Documentation",
        ),
        (
            r"The Science Behind (?P<brand>[^:\n|]+): Professional Endorsements and Efficacy",
            r"\g<brand> Professional Trust Signals and Ingredient Documentation",
        ),
        (
            r"The Efficacy of (?P<brand>[^|\n]+?) Against Hong Kong's Environmental Stressors",
            r"\g<brand> Ingredient Guide for Hong Kong Environmental Stressors",
        ),
        (
            r"Efficacy Against Environmental Stressors",
            "Evidence-Supported Environmental Stressor Positioning",
        ),
        (
            r"Absence of studies demonstrating product effectiveness for common skin concerns in the local market\.?",
            "Absence of claims support documentation, consumer feedback, or expert validation for local market claims.",
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
            r"Absence of claims support documentation, where substantiated and compliant Data",
            "Absence of claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"Promote the efficacy of products through claims support documentation, where substantiated and compliant and consumer testimonials\.?",
            "Support product claims with compliant documentation, consumer testimonials, and expert validation.",
        ),
        (
            r"Clinical studies or data demonstrating product efficacy(?: in the local context)?",
            "Claims support documentation, consumer feedback, or expert validation, where substantiated and compliant",
        ),
        (
            r"Clinical studies or consumer feedback validating product effectiveness",
            "Claims support documentation, consumer feedback, or expert validation, only where substantiated and compliant",
        ),
        (
            r"Invest in claims support documentation, only where substantiated and compliant or studies to substantiate efficacy claims",
            "Develop claims support documentation and consumer evidence where substantiated and compliant",
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
            r"Studies or data demonstrating efficacy(?: in Hong Kong)?",
            "consumer feedback, expert validation, ingredient documentation, or compliant claims support",
        ),
        (
            r"published studies demonstrating product effectiveness",
            "consumer study documentation or compliant claims support",
        ),
        (r"Professional and Clinical Endorsement", "Professional Trust Signals"),
        (
            r"Professional Endorsements and Efficacy",
            "Professional Trust Signals and Ingredient Documentation",
        ),
        (r"Medical-Grade Efficacy", "Evidence-Supported Product Positioning"),
        (r"medical-grade efficacy", "evidence-supported product positioning"),
        (r"clinic-grade", "professional-grade"),
        (r"clinical-grade", "professional-grade"),
        (r"medical-grade claims", "professional-grade positioning, where substantiated"),
        (r"medical-grade", "professional-grade"),
        (r"strong clinical backing", "Strong evidence-supported positioning"),
        (r"clinical backing", "evidence-supported positioning"),
        (r"clinical results", "documented outcomes, where substantiated and compliant"),
        (r"clinically backed", "evidence-supported"),
        (r"clinically proven", "evidence-supported"),
        (r"clinically effective", "evidence-supported"),
        (r"clinical collaboration", "professional evidence review"),
        (r"clinical validations", "expert validation and claims support documentation"),
        (r"clinical evidence", "claims support documentation and expert validation"),
        (r"clinical data", "claims support documentation"),
        (r"clinical support", "evidence support"),
        (r"clinical studies", "claims support documentation, where substantiated and compliant"),
        (r"clinical trials?", "claims support documentation, where substantiated and compliant"),
        (r"clinical approach", "professional evidence approach"),
        (r"clinical endorsements", "professional endorsements"),
        (r"validate product claims", "support product claims where substantiated and compliant"),
        (r"validating product effectiveness", "supporting product claims where substantiated and compliant"),
        (r"studies to substantiate efficacy claims", "claims support documentation where substantiated and compliant"),
        (r"efficacy claims", "product claims, where substantiated and compliant"),
        (r"proven effectiveness", "evidence-supported product claims"),
        (r"prove effectiveness", "support product claims"),
        (r"proven results", "documented results, where substantiated and compliant"),
        (
            r"Comparative analysis data on product effectiveness",
            "Comparison table data and claims support documentation",
        ),
        (
            r"Comparison table data showcasing ingredient efficacy",
            "Comparison table data showcasing ingredient documentation and claims support",
        ),
        (
            r"Ingredient documentation supporting product efficacy",
            "Ingredient documentation and claims support materials",
        ),
        (
            r"showcasing ingredient efficacy",
            "showcasing ingredient documentation and claims support",
        ),
        (r"ingredient efficacy", "ingredient documentation and claims support"),
        (r"showing efficacy", "supporting product claims"),
        (r"product efficacy", "product claims"),
        (r"product effectiveness", "product claims"),
        (r"substantiated product evidence Data", "Claims Support Documentation"),
        (r"substantiated product evidence", "claims support documentation"),
        (r"scientifically-backed", "evidence-supported"),
        (r"scientific backing", "evidence support"),
        (r"visible results", "documented outcomes, where substantiated and compliant"),
        (r"dermatologist-recommended", "professionally recommended"),
        (r"\befficacy-focused\b", "evidence-focused"),
        (r"\beffectiveness-focused\b", "evidence-focused"),
        (r"\bEfficacy\b", "product claims"),
        (r"\befficacy\b", "product claims"),
        (r"\bEffectiveness\b", "Evidence Support"),
        (r"\beffectiveness\b", "evidence support"),
    ]

    sanitized = _apply_replacements(sanitized, replacements)

    cleanup_replacements = [
        (
            r"claims support documentation, consumer feedback, or expert validation supporting product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"Claims support documentation, consumer feedback, or expert validation supporting product claims",
            "Claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, consumer feedback, or expert validation product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"Claims support documentation, consumer feedback, or expert validation product claims",
            "Claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, supported by product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, supported by claims support",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, supported by evidence support",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, product claims, where substantiated and compliant",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant validating",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant showing",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant supporting",
            "Claims support documentation, consumer feedback, or expert validation supporting",
        ),
        (
            r"claims support documentation, where substantiated and compliant product claims",
            "claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"claims support documentation, where substantiated and compliant Data",
            "Claims support documentation and supporting evidence",
        ),
        (
            r"claims support documentation, where substantiated and compliant data",
            "claims support documentation and supporting evidence",
        ),
        (
            r"Research studies or claims support documentation, where substantiated and compliant",
            "Claims support documentation, consumer feedback, or expert validation",
        ),
        (
            r"ingredient documentation and claims support and Innovation",
            "Ingredient Documentation and Evidence-Supported Innovation",
        ),
        (
            r"ingredient documentation and claims support and innovation",
            "ingredient documentation and evidence-supported innovation",
        ),
        (r"Professional and professional-grade", "Professional-Grade"),
        (r"professional and professional-grade", "professional-grade"),
        (r"High-Evidence Support", "Evidence-Supported"),
        (r"High-evidence support", "evidence-supported"),
        (r"where substantiated and compliant and", "where substantiated and compliant, plus"),
        (r"\bproduct claims product claims\b", "product claims"),
        (r"\bprofessional-grade evidence support\b", "evidence-supported product positioning"),
        (r"\bprofessional-grade claims support\b", "evidence-supported product positioning"),
        (r"\bprofessional-grade efficacy\b", "evidence-supported product positioning"),
        (r"\bevidence support claims\b", "product claims"),
        (r"\bEvidence Support-focused\b", "Evidence-focused"),
        (r"\bevidence support-focused\b", "evidence-focused"),
        (r"\bClaims Support-focused\b", "Evidence-focused"),
        (r"\bclaims support-focused\b", "evidence-focused"),
        (r"[ \t]{2,}", " "),
        (r"\s+\.", "."),
    ]

    sanitized = _apply_replacements(sanitized, cleanup_replacements)
    sanitized = _sanitize_malformed_claim_sentences(sanitized)

    return sanitized.strip()


def _is_quick_test_numeric_target_statement(value: str) -> bool:
    text = str(value or "")
    if KNOWN_TARGET_ARTIFACT_RE.search(text):
        return True
    if CURRENT_STATE_DIAGNOSTIC_RE.search(text) and not EXPLICIT_FUTURE_TARGET_RE.search(text):
        return False
    return bool(QUICK_TEST_TARGET_LANGUAGE_RE.search(text) and QUICK_TEST_NUMERIC_TARGET_RE.search(text))


def _directional_quick_test_replacement(value: str) -> str | None:
    text = str(value or "")
    lowered = normalize_text(text)

    if (
        ("total mentions" in lowered and "average visibility" in lowered and "prompts visible" in lowered)
        or ("conservative targets" in lowered and "mention" in lowered and ("visible" in lowered or "prompt categor" in lowered))
    ):
        return "Total mentions, average visibility score, and prompts visible should improve directionally in a future full benchmark."

    if "total mentions" in lowered and "average visibility" in lowered and "share of voice" in lowered:
        return (
            "Total mentions: begin generating detectable mentions in a future full benchmark. "
            "Average visibility score: begin improving average visibility score in a future full benchmark. "
            "Share of voice: Begin generating measurable share of voice in a future full benchmark."
        )

    if "share of voice" in lowered or re.search(r"\bsov\b", text, flags=re.IGNORECASE) or "capture share" in lowered:
        return "Begin generating measurable share of voice in a future full benchmark."

    if (
        "average visibility" in lowered
        or "visibility score" in lowered
        or re.search(r"\bvisibility\s+to\s+\d+(?:\.\d+)?", text, flags=re.IGNORECASE)
    ):
        return "Begin improving average visibility score in a future full benchmark."

    if "mention" in lowered or "mention count" in lowered:
        return "Begin generating detectable mentions in a future full benchmark."

    if (
        "prompt categor" in lowered
        or "prompts visible" in lowered
        or "visible in" in lowered
        or "visibility in" in lowered
        or "visibility" in lowered
    ):
        return "Begin generating prompt-level visibility in relevant prompt categories."

    if BUSINESS_TARGET_RE.search(text):
        return "Improve the relevant benchmark metric directionally."

    return None


def _sanitize_quick_test_target_unit(unit: str) -> str:
    text = str(unit or "")

    grammar_replacements = [
        (
            r"\b(?:Aim for|aiming for|Increase|Improve)\s+(Begin generating .+)",
            r"\1",
        ),
        (
            r"\ba begin generating\b",
            "begin generating",
        ),
    ]
    text = _apply_replacements(text, grammar_replacements)

    if not _is_quick_test_numeric_target_statement(text):
        return text

    replacement = _directional_quick_test_replacement(text)
    if not replacement:
        return text

    prefix_match = re.match(r"^(?P<prefix>\s*(?:[-*]\s+|\d+[.)]\s*)?)", text)
    prefix = prefix_match.group("prefix") if prefix_match else ""
    trailing_space = " " if text.endswith(" ") else ""
    return f"{prefix}{replacement}{trailing_space}"


def _sanitize_quick_test_numeric_targets(text: str, context: OutputQualityContext) -> str:
    if not is_quick_test_mode(context.run_mode):
        return str(text or "")

    sanitized_lines = []
    for line in str(text or "").splitlines():
        if "|" in line and line.strip().startswith("|"):
            cells = line.split("|")
            sanitized_cells = [
                _sanitize_quick_test_target_unit(cell)
                for cell in cells
            ]
            sanitized_lines.append("|".join(sanitized_cells))
            continue

        parts = re.split(r"(?<=[.!?])(\s+)", line)
        if len(parts) == 1:
            sanitized_lines.append(_sanitize_quick_test_target_unit(line))
            continue

        rebuilt = []
        index = 0
        while index < len(parts):
            sentence = parts[index]
            separator = parts[index + 1] if index + 1 < len(parts) else ""
            rebuilt.append(_sanitize_quick_test_target_unit(sentence))
            rebuilt.append(separator)
            index += 2
        sanitized_lines.append("".join(rebuilt).rstrip())

    return "\n".join(sanitized_lines)


def _iter_text_quality_units(text: str):
    for line in str(text or "").splitlines():
        if "|" in line and line.strip().startswith("|"):
            for cell in line.split("|"):
                if cell.strip():
                    yield cell
            continue

        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            if part.strip():
                yield part


def sanitize_business_kpi_text(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    context = context or OutputQualityContext()
    sanitized = _sanitize_quick_test_numeric_targets(str(text or ""), context)

    target_replacements = [
        (
            r"\bIncrease mentions from \d+(?:\.\d+)? to \d+\s*-\s*\d+\.?",
            "Begin generating detectable mentions in a future full benchmark.",
        ),
        (
            r"\bMove from \d+(?:\.\d+)? visibility to \d+(?:\.\d+)? or more\.?",
            "Begin improving average visibility score in a future full benchmark.",
        ),
        (
            r"\bEstablish presence in \d+\s*-\s*\d+ relevant prompt categories\.?",
            "Begin generating prompt-level visibility in relevant prompt categories.",
        ),
        (
            r"\bAchieve visibility in at least \d+\s*-\s*\d+ relevant prompt categories\.?",
            "Begin generating prompt-level visibility in relevant prompt categories.",
        ),
        (
            r"\bGain visibility in \d+\s*-\s*\d+ prompt categories\.?",
            "Begin generating prompt-level visibility in relevant prompt categories.",
        ),
        (
            r"\bGenerate \d+\s*-\s*\d+ mentions(?: from [^.]+)?\.?",
            "Begin generating detectable mentions in a future full benchmark.",
        ),
        (
            r"\bEstablish a recognizable presence in local searches and begin to capture share of voice\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"\bTotal mentions, average visibility score, and prompts visible should each aim to increase from \d+(?:\.\d+)? to at least \d+\s*-\s*\d+\.?",
            "Total mentions, average visibility score, and prompts visible should improve directionally in a future full benchmark.",
        ),
        (
            r"target a benchmark of \d+(?:\.\d+)?% share of voice(?: in [^.]+)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"total mentions\s*\(aim to reach at least \d+\s*(?:-\s*\d+)?\)",
            "Total mentions (begin generating detectable mentions in a future full benchmark)",
        ),
        (
            r"average visibility score\s*\(target \d+(?:\.\d+)?\)",
            "average visibility score (begin improving average visibility score in a future full benchmark)",
        ),
        (
            r"share of voice\s*\(aim for \d+(?:\.\d+)?%\)",
            "share of voice (begin generating measurable share of voice in a future full benchmark)",
        ),
        (
            r"aim to reach at least \d+\s*(?:-\s*\d+)?",
            "begin generating detectable mentions in a future full benchmark",
        ),
        (
            r"target \d+(?:\.\d+)?\)",
            "begin improving average visibility score in a future full benchmark)",
        ),
        (
            r"aim for \d+(?:\.\d+)?%\)",
            "begin generating measurable share of voice in a future full benchmark)",
        ),
        (
            r"(?:Reach|Achieve|Target|Capture)\s+(?:at least\s+)?\d+(?:\.\d+)?%?\s+share of voice(?: in [^.]+)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"goal of achieving\s+(?:at least\s+)?\d+(?:\.\d+)?%?\s+share of voice(?: in [^.]+)?",
            "goal of beginning to generate measurable share of voice in a future full benchmark",
        ),
        (
            r"(?:at least|above|over)\s+\d+(?:\.\d+)?%?\s+share of voice",
            "measurable share of voice in a future full benchmark",
        ),
        (
            r"share of voice\s+(?:above|over|of at least|to at least)\s+\d+(?:\.\d+)?%?",
            "measurable share of voice in a future full benchmark",
        ),
        (
            r"SOV\s+(?:above|over|of at least|to at least)\s+\d+(?:\.\d+)?%?",
            "measurable share of voice in a future full benchmark",
        ),
        (
            r"(?:Increase|Improve|Raise|Lift)\s+(?:average\s+)?visibility score\s+(?:to\s+)?(?:above|over|at least)\s+\d+(?:\.\d+)?%?\.?",
            "Begin improving average visibility score in a future full benchmark.",
        ),
        (
            r"(?:Increase|Improve|Raise|Lift)\s+(?:average\s+)?visibility score\s+to\s+\d+(?:\.\d+)?%?\.?",
            "Begin improving average visibility score in a future full benchmark.",
        ),
        (
            r"(?:average\s+)?visibility score\s+(?:to\s+)?(?:above|over|at least)\s+\d+(?:\.\d+)?%?",
            "measurable visibility improvement in a future full benchmark",
        ),
        (
            r"(?:Aim for|Target|Achieve|Reach)\s+(?:at least\s+)?\d+\s*(?:-\s*\d+)?\s+detectable mentions?\.?",
            "Begin generating detectable mentions in a future full benchmark.",
        ),
        (
            r"(?:Aim for|Target|Achieve|Reach)\s+(?:at least\s+)?\d+\s*(?:-\s*\d+)?\s+mentions?\.?",
            "Begin generating detectable mentions in a future full benchmark.",
        ),
        (
            r"(?:at least|above|over)\s+\d+\s*(?:-\s*\d+)?\s+detectable mentions?",
            "detectable mentions in a future full benchmark",
        ),
        (
            r"(?:at least|above|over)\s+\d+\s*(?:-\s*\d+)?\s+mentions?",
            "detectable mentions in a future full benchmark",
        ),
        (
            r"Visible in at least \d+\s*(?:-\s*\d+)? prompt categories",
            "Begin generating prompt-level visibility in a future full benchmark",
        ),
        (
            r"visible in at least \d+\s*(?:-\s*\d+)? prompt categories",
            "begin generating prompt-level visibility in a future full benchmark",
        ),
        (
            r"Move toward being visible in \d+\s*-\s*\d+ relevant prompt categories",
            "Begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"move toward being visible in \d+\s*-\s*\d+ relevant prompt categories",
            "begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"Achieve visibility in \d+\s*-\s*\d+ relevant prompt categories",
            "Begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"achieve visibility in \d+\s*-\s*\d+ relevant prompt categories",
            "begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"visibility in \d+\s*-\s*\d+ relevant prompt categories",
            "Begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"(?<!prompt-level )\bvisibility in relevant prompt categories\b",
            "Begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"Gain initial mentions and recognition among target queries",
            "Begin generating detectable mentions in relevant target queries",
        ),
        (
            r"Achieve initial mentions",
            "Begin generating detectable mentions",
        ),
        (
            r"achieve initial mentions",
            "begin generating detectable mentions",
        ),
        (
            r"Above \d+(?:\.\d+)?",
            "Begin improving average visibility score in a future full benchmark",
        ),
        (
            r"above \d+(?:\.\d+)?",
            "begin improving average visibility score in a future full benchmark",
        ),
        (
            r"At least \d+(?:\.\d+)?%",
            "Begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"at least \d+(?:\.\d+)?%",
            "begin generating measurable share of voice in a future full benchmark",
        ),
    ]

    for pattern, replacement in target_replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    general_replacements = [
        (
            r"capture \d+(?:\.\d+)?% share of voice",
            "begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"reach \d+(?:\.\d+)?% share of voice",
            "begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"achieve \d+(?:\.\d+)?% share of voice",
            "begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"target \d+(?:\.\d+)?% share of voice",
            "begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"(?:increase|boost) by \d+(?:\.\d+)?%",
            "improve the relevant benchmark metric directionally",
        ),
        (r"conversion rate", "query intent visibility"),
        (r"session duration", "prompt-level visibility"),
        (r"engagement rate", "target-brand association"),
        (r"traffic increase", "query intent visibility improvement"),
        (r"\brevenue\b", "business outcome"),
        (r"\bsales\b", "business outcomes"),
        (r"\bguarantee(?:d|s)?\b", "support"),
    ]

    for pattern, replacement in general_replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    grammar_replacements = [
        (
            r"\b(?:Increase|Improve) Begin generating prompt-level visibility in relevant prompt categories\.?",
            "Begin generating prompt-level visibility in relevant prompt categories.",
        ),
        (
            r"\bAchieve initial visibility in at least \d+\s*-\s*\d+ relevant prompt categories\.?",
            "Begin generating prompt-level visibility in relevant prompt categories.",
        ),
        (
            r"\binitial visibility in at least \d+\s*-\s*\d+ relevant prompt categories\b",
            "Begin generating prompt-level visibility in relevant prompt categories",
        ),
        (
            r"Achieve a begin generating measurable share of voice in a future full benchmark(?: in targeted comparisons| in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Achieve begin generating measurable share of voice in a future full benchmark(?: in targeted comparisons| in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"achieving a begin generating measurable share of voice in a future full benchmark(?: in targeted comparisons| in targeted categories)?",
            "beginning to generate measurable share of voice in a future full benchmark",
        ),
        (
            r"target a detectable begin generating measurable share of voice in a future full benchmark(?: in targeted comparisons| in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Target a detectable begin generating measurable share of voice in a future full benchmark(?: in targeted comparisons| in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"target begin generating measurable share of voice(?: in a future full benchmark)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Expected AI visibility effect:\s*Aim for a measurable share of voice in a future full benchmark(?: in targeted categories)?\.?",
            "Expected AI visibility effect: Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Expected AI visibility effect:\s*Aim for a begin generating measurable share of voice in a full benchmark(?: in targeted categories)?\.?",
            "Expected AI visibility effect: Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Expected AI visibility effect:\s*Aim for a begin generating measurable share of voice in a future full benchmark(?: in targeted categories)?\.?",
            "Expected AI visibility effect: Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Aim for a begin generating measurable share of voice in a full benchmark(?: in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Aim for a begin generating measurable share of voice in a future full benchmark(?: in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"Aim for a measurable share of voice in a future full benchmark(?: in targeted categories)?\.?",
            "Begin generating measurable share of voice in a future full benchmark.",
        ),
        (
            r"\ba begin generating measurable share of voice in a future full benchmark\b",
            "begin generating measurable share of voice in a future full benchmark",
        ),
        (
            r"\baiming for begin generating detectable mentions in a future full benchmark\b",
            "Begin generating detectable mentions in a future full benchmark",
        ),
        (
            r"goal of achieving begin generating detectable mentions",
            "goal of beginning to generate detectable mentions",
        ),
        (
            r"achieving begin generating detectable mentions",
            "beginning to generate detectable mentions",
        ),
        (r"[ \t]{2,}", " "),
    ]

    return _apply_replacements(sanitized, grammar_replacements).strip()


def sanitize_source_label_artifacts(text: str) -> str:
    replacements = [
        (
            r"Top Competitor-Owned Associations\s*\(Source:\s*AI-discovered market signal\)s\)",
            "Top Competitor-Owned Associations",
        ),
        (r"\(Source:\s*AI-discovered market signal\)s\)", ""),
        (r"\(Source:\s*Tracked competitor\)s\)", ""),
        (r"\(Source:\s*Mixed tracked competitor / AI-discovered market signal\)s\)", ""),
        (r"\s+\)", ")"),
        (r"\(\s*\)", ""),
    ]
    return _apply_replacements(text, replacements).strip()


def _strip_bullet_prefix(line):
    return re.sub(r"^\s*(?:[-*]\s+|\d+[.)]\s*)", "", str(line or "")).strip()


def _extract_bullet_entity(line):
    stripped = _strip_bullet_prefix(line)

    bold_match = re.match(r"\*\*(?P<name>[^*]+)\*\*", stripped)
    if bold_match:
        return bold_match.group("name").strip()

    plain_match = re.match(
        r"(?P<name>[^:\-|\u2013\u2014]+?)\s*(?:[:\-|\u2013\u2014]|$)",
        stripped,
    )
    if plain_match:
        return plain_match.group("name").strip()

    return stripped


def _contains_invalid_brand_item(value):
    normalized = str(value or "")
    return any(
        re.search(pattern, normalized, flags=re.IGNORECASE)
        for pattern in INVALID_AI_DISCOVERED_BRAND_BULLET_PATTERNS
    )


def _is_wrapper_entity(value: str) -> bool:
    return bool(WRAPPER_ENTITY_RE.search(str(value or "")))


def _entity_has_action_language(value: str) -> bool:
    entity = str(value or "").strip()
    return bool(
        ACTION_ENTITY_START_RE.search(entity)
        or GENERIC_ACTION_ENTITY_NOUN_RE.search(entity)
        or WRAPPER_ENTITY_RE.search(entity)
        or _contains_invalid_brand_item(entity)
    )


def _line_indicates_action_task(value: str) -> bool:
    line = str(value or "")
    return bool(ACTION_TASK_LINE_RE.search(line) or _contains_invalid_brand_item(line))


def _is_brand_like_entity(value: str) -> bool:
    entity = str(value or "").strip(" -*:().")
    if not entity or len(entity) < 2:
        return False
    if _entity_has_action_language(entity):
        return False

    words = [word for word in re.split(r"\s+", entity) if word]
    if not words or len(words) > 6:
        return False

    if BRAND_LEGAL_SUFFIX_RE.search(entity) or BRAND_SYMBOL_RE.search(entity):
        return bool(re.search(r"[A-Za-z0-9]", entity))

    connector_words = {"the", "a", "an", "and", "or", "of", "de", "der", "la", "le", "van", "von"}
    meaningful_words = [
        word.strip("'’")
        for word in words
        if normalize_text(word.strip("'’")) not in connector_words
    ]
    if not meaningful_words:
        return False

    brandish_words = [
        word
        for word in meaningful_words
        if re.search(r"[A-Z]", word) or word[:1].isupper()
    ]

    if len(words) > 1:
        return len(brandish_words) >= max(1, (len(meaningful_words) + 1) // 2)

    single = meaningful_words[0]
    if len(single) <= 2:
        return False
    return bool(
        re.search(r"[A-Z]", single)
        and not normalize_text(single) in connector_words
    )


def _extract_embedded_brand_bullets(
    line: str,
    context: OutputQualityContext | None = None,
) -> list[str]:
    context = context or OutputQualityContext()
    text = str(line or "")
    if not re.search(
        r"\b(additional brands|other brands|brands like|consider adding brands like|"
        r"consider adding brands|such as|including)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return []

    wrapper_entity = normalize_text(_extract_bullet_entity(text))
    extracted = []
    seen = set()
    for name in re.findall(r"\*\*([^*]+)\*\*", text):
        candidate = str(name).strip()
        normalized = normalize_text(candidate)
        if not normalized or normalized == wrapper_entity or normalized in seen:
            continue
        if _is_tracked_brand(candidate, context.tracked_competitors):
            continue
        if not _is_brand_like_entity(candidate):
            continue
        bullet = f"- **{candidate}**"
        extracted.append(bullet)
        seen.add(normalized)
    return extracted


def is_likely_brand_bullet(line: str) -> bool:
    stripped = str(line or "").strip()

    if not re.match(r"^\s*(?:[-*]\s+|\d+[.)]\s*)", stripped):
        return False

    entity = _extract_bullet_entity(stripped)
    if not entity:
        return False

    if _line_indicates_action_task(stripped):
        return False

    return _is_brand_like_entity(entity)


def _is_section_boundary(stripped_line):
    if not stripped_line:
        return False

    if MARKDOWN_HORIZONTAL_RULE_RE.match(stripped_line):
        return True

    if stripped_line.startswith("|"):
        return True

    if (
        AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped_line)
        or MARKET_TRENDS_HEADING_RE.match(stripped_line)
        or TRACKED_COMPETITORS_HEADING_RE.match(stripped_line)
    ):
        return True

    if re.match(r"^\s*(?:[-*]|\d+[.)])", stripped_line):
        return False

    return bool(SECTION_HEADING_RE.match(stripped_line))


def _extract_brand_names_from_cell(value):
    text = str(value or "").strip()

    if not text or normalize_text(text) in {"none", "none listed", "n/a", "not listed"}:
        return []

    text = re.sub(r"\(Source:[^)]+\)", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b(?:tracked competitors?|ai-discovered market signals?|mixed tracked competitors? / ai-discovered market signals?)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    names = []
    for part in re.split(r",|\band\b|/|;", text):
        candidate = part.strip(" -*:().")
        if not candidate or len(candidate.split()) > 6:
            continue
        if re.search(r"[A-Z]", candidate):
            names.append(candidate)

    return names


def _extract_example_brands_from_text(value, tracked_competitors=None):
    text = str(value or "")
    names = []
    seen = set()

    def add(name):
        normalized = normalize_text(name)
        if normalized and normalized not in seen:
            seen.add(normalized)
            names.append(str(name).strip())

    for competitor in tracked_competitors or []:
        if re.search(re.escape(str(competitor)), text, flags=re.IGNORECASE):
            add(competitor)

    cue_match = re.search(
        r"\b(?:with|like|such as|including|from)\b(?P<phrase>.*?)(?:[.;()]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if cue_match:
        for candidate in _extract_brand_names_from_cell(cue_match.group("phrase")):
            add(candidate)

    if not names:
        for candidate in _extract_brand_names_from_cell(text):
            add(candidate)

    return names


def classify_source_type_from_example_brands(
    example_brands: str | list[str] | None,
    tracked_competitors: list[str] | None = None,
) -> str:
    if isinstance(example_brands, str):
        brands = _extract_brand_names_from_cell(example_brands)
    else:
        brands = [str(item).strip() for item in (example_brands or []) if str(item).strip()]

    if not brands:
        return "Diagnostic inference"

    tracked = [brand for brand in brands if _is_tracked_brand(brand, tracked_competitors)]
    non_tracked = [brand for brand in brands if not _is_tracked_brand(brand, tracked_competitors)]

    if tracked and non_tracked:
        return "Mixed tracked competitors / AI-discovered market signals"
    if tracked:
        return "Tracked competitors"
    return "AI-discovered market signals"


def _markdown_table_cells(line):
    if not str(line).strip().startswith("|"):
        return None
    return [part.strip() for part in str(line).split("|")[1:-1]]


def _markdown_separator_for(columns):
    return "| " + " | ".join("---" for _ in columns) + " |"


def sanitize_competitor_advantage_table(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    context = context or OutputQualityContext()
    columns = ["Advantage Signal", "Evidence Source", "Example Brands", "Source Type"]
    lines = str(text or "").splitlines()
    sanitized = []
    index = 0

    while index < len(lines):
        line = lines[index]
        cells = _markdown_table_cells(line)
        normalized_cells = [normalize_text(cell) for cell in cells or []]

        is_advantage_table = (
            cells
            and "advantage signal" in normalized_cells
            and (
                "source" in normalized_cells
                or "source type" in normalized_cells
                or "evidence source" in normalized_cells
            )
        )

        if not is_advantage_table:
            sanitized.append(line)
            index += 1
            continue

        sanitized.append("| " + " | ".join(columns) + " |")
        sanitized.append(_markdown_separator_for(columns))
        index += 1

        if index < len(lines) and set(str(lines[index]).replace("|", "").strip()) <= {"-", ":", " "}:
            index += 1

        header_map = {normalize_text(cell): pos for pos, cell in enumerate(cells)}

        while index < len(lines):
            row_cells = _markdown_table_cells(lines[index])
            if row_cells is None:
                break

            if set(str(lines[index]).replace("|", "").strip()) <= {"-", ":", " "}:
                index += 1
                continue

            def get_cell(*names):
                for name in names:
                    pos = header_map.get(normalize_text(name))
                    if pos is not None and pos < len(row_cells):
                        return sanitize_source_label_artifacts(row_cells[pos])
                return ""

            advantage = get_cell("Advantage Signal") or (row_cells[0] if row_cells else "")
            evidence = get_cell("Evidence Source") or "Diagnostic inference"
            examples = get_cell("Example Brands")
            source_value = get_cell("Source Type", "Source")

            if not examples:
                examples = ", ".join(
                    _extract_example_brands_from_text(
                        advantage,
                        context.tracked_competitors,
                    )
                )

            source_type = classify_source_type_from_example_brands(
                examples,
                context.tracked_competitors,
            )

            if source_type == "Diagnostic inference" and "user-provided" in normalize_text(source_value):
                source_type = "User-provided"
                evidence = "User-provided context"

            sanitized.append(
                "| "
                + " | ".join(
                    [
                        sanitize_source_label_artifacts(advantage),
                        sanitize_source_label_artifacts(evidence),
                        sanitize_source_label_artifacts(examples) or "None listed",
                        source_type,
                    ]
                )
                + " |"
            )

            index += 1

        continue

    return "\n".join(sanitized)


def sanitize_ai_discovered_brands_section(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    context = context or OutputQualityContext()
    lines = str(text or "").splitlines()
    result = []
    in_section = False
    section_lines = []

    def flush_section():
        nonlocal section_lines, in_section

        if not in_section:
            return

        valid = []
        for item in section_lines:
            if not item.strip():
                continue

            if not is_likely_brand_bullet(item):
                valid.extend(_extract_embedded_brand_bullets(item, context))
                continue

            entity = _extract_bullet_entity(item)
            if _is_tracked_brand(entity, context.tracked_competitors):
                continue

            valid.append(item)

        if valid:
            result.extend(valid)
        else:
            result.append("No additional non-tracked brands were identified.")

        section_lines = []
        in_section = False

    for line in lines:
        stripped = line.strip()

        if AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped):
            flush_section()
            result.append("AI-Discovered Brands Not Included in Scoring")
            in_section = True
            continue

        if in_section and (
            MARKET_TRENDS_HEADING_RE.match(stripped)
            or (not AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped) and _is_section_boundary(stripped))
        ):
            flush_section()
            result.append(line)
            continue

        if in_section:
            section_lines.append(line)
            continue

        result.append(line)

    flush_section()
    return dedupe_empty_section_placeholders("\n".join(result))


def sanitize_market_trends_section(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    lines = str(text or "").splitlines()
    result = []
    in_section = False
    buffer = []

    def flush():
        nonlocal buffer, in_section

        if not in_section:
            return

        valid = [line for line in buffer if line.strip() and not is_likely_brand_bullet(line)]

        if valid:
            result.extend(valid)
        else:
            result.append("No additional non-tracked market signals were identified.")

        buffer = []
        in_section = False

    for line in lines:
        stripped = line.strip()

        if MARKET_TRENDS_HEADING_RE.match(stripped):
            flush()
            result.append("Market Trends / Demand Signals")
            in_section = True
            continue

        if in_section and (
            AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped)
            or (not MARKET_TRENDS_HEADING_RE.match(stripped) and _is_section_boundary(stripped))
        ):
            flush()
            result.append(line)
            continue

        if in_section:
            buffer.append(line)
            continue

        result.append(line)

    flush()
    return dedupe_empty_section_placeholders("\n".join(result))


def sanitize_market_signal_sections(
    text: str,
    context: OutputQualityContext | None = None,
) -> str:
    context = context or OutputQualityContext()
    sanitized = sanitize_ai_discovered_brands_section(text, context)
    sanitized = sanitize_market_trends_section(sanitized, context)
    return dedupe_empty_section_placeholders(sanitized)


def sanitize_geo_roadmap_text(
    text: str,
    context: OutputQualityContext,
) -> str:
    sanitized = sanitize_source_label_artifacts(text)
    sanitized = sanitize_claim_safety_text(sanitized, context)
    sanitized = sanitize_business_kpi_text(sanitized, context)
    return dedupe_empty_section_placeholders(sanitized).strip()


def sanitize_brand_intelligence_text(
    text: str,
    context: OutputQualityContext,
) -> str:
    sanitized = sanitize_source_label_artifacts(text)
    sanitized = sanitize_claim_safety_text(sanitized, context)
    sanitized = sanitize_competitor_advantage_table(sanitized, context)
    sanitized = sanitize_market_signal_sections(sanitized, context)
    sanitized = sanitize_business_kpi_text(sanitized, context)
    sanitized = re.sub(r"[ \t]+\n", "\n", sanitized)
    sanitized = re.sub(r"\n{4,}", "\n\n\n", sanitized)
    return dedupe_empty_section_placeholders(sanitized).strip()


def sanitize_strategy_text(
    text: str,
    context: OutputQualityContext,
) -> str:
    sanitized = sanitize_claim_safety_text(text, context)
    sanitized = sanitize_business_kpi_text(sanitized, context)
    sanitized = sanitize_source_label_artifacts(sanitized)
    sanitized = re.sub(r"[ \t]+\n", "\n", sanitized)
    return sanitized.strip()


def sanitize_narrative_appendix_text(
    text: str,
    context: OutputQualityContext,
) -> str:
    return sanitize_strategy_text(text, context)


def sanitize_report_text(
    text: str,
    context: OutputQualityContext,
) -> str:
    sanitized = sanitize_claim_safety_text(text, context)
    sanitized = sanitize_business_kpi_text(sanitized, context)
    sanitized = sanitize_competitor_advantage_table(sanitized, context)
    sanitized = sanitize_market_signal_sections(sanitized, context)
    sanitized = sanitize_source_label_artifacts(sanitized)
    sanitized = sanitize_geo_roadmap_text(sanitized, context)
    sanitized = re.sub(r"[ \t]+\n", "\n", sanitized)
    sanitized = re.sub(r"\n{4,}", "\n\n\n", sanitized)
    return dedupe_empty_section_placeholders(sanitized).strip()


def sanitize_snapshot_payload(
    snapshot: dict,
    context: OutputQualityContext,
) -> dict:
    sanitized = copy.deepcopy(snapshot)
    brand_intelligence = sanitized.get("brand_intelligence")

    if isinstance(brand_intelligence, dict):
        for key in (
            "recommendation_drivers",
            "target_brand_understanding",
            "positioning_gap_analysis",
        ):
            if brand_intelligence.get(key):
                brand_intelligence[key] = sanitize_brand_intelligence_text(
                    brand_intelligence[key],
                    context,
                )

    notes = sanitized.get("notes")
    if isinstance(notes, dict):
        for key, value in list(notes.items()):
            if isinstance(value, str):
                notes[key] = sanitize_source_label_artifacts(value)

    return sanitized


def _text_from_payload(value):
    if isinstance(value, dict):
        return "\n".join(_text_from_payload(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(_text_from_payload(item) for item in value)
    return str(value or "")


def _extract_ai_discovered_section_lines(text):
    lines = str(text or "").splitlines()
    in_section = False
    section_lines = []

    for line in lines:
        stripped = line.strip()

        if AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped):
            in_section = True
            continue

        if in_section and (
            MARKET_TRENDS_HEADING_RE.match(stripped)
            or (not AI_DISCOVERED_BRANDS_HEADING_RE.match(stripped) and _is_section_boundary(stripped))
        ):
            in_section = False

        if in_section:
            section_lines.append(line)

    return section_lines


def _find_competitor_advantage_source_issues(text, context, content_type):
    issues = []
    lines = str(text or "").splitlines()
    index = 0

    while index < len(lines):
        cells = _markdown_table_cells(lines[index])
        normalized_cells = [normalize_text(cell) for cell in cells or []]

        is_advantage_table = (
            cells
            and "advantage signal" in normalized_cells
            and "example brands" in normalized_cells
            and "source type" in normalized_cells
        )

        if not is_advantage_table:
            index += 1
            continue

        header_map = {normalize_text(cell): pos for pos, cell in enumerate(cells)}
        example_index = header_map.get("example brands")
        source_index = header_map.get("source type")

        index += 1

        if index < len(lines) and set(str(lines[index]).replace("|", "").strip()) <= {"-", ":", " "}:
            index += 1

        while index < len(lines):
            row_cells = _markdown_table_cells(lines[index])
            if row_cells is None:
                break

            if set(str(lines[index]).replace("|", "").strip()) <= {"-", ":", " "}:
                index += 1
                continue

            if (
                example_index is not None
                and source_index is not None
                and example_index < len(row_cells)
                and source_index < len(row_cells)
            ):
                examples = row_cells[example_index]
                actual = row_cells[source_index].strip()
                expected = classify_source_type_from_example_brands(
                    examples,
                    context.tracked_competitors,
                )

                if normalize_text(actual) != normalize_text(expected):
                    issues.append(
                        OutputQualityIssue(
                            code="source_type_mismatch",
                            message="Competitor Advantage Signals Source Type does not match Example Brands.",
                            section=content_type,
                            phrase=lines[index].strip(),
                        )
                    )

            index += 1

    return issues


def validate_output_quality(
    text_or_payload,
    context: OutputQualityContext,
    content_type: str = "text",
    strict: bool = True,
) -> list[OutputQualityIssue]:
    text = _text_from_payload(text_or_payload)
    issues = []

    if is_raw_error_output(text):
        issues.append(
            OutputQualityIssue(
                code="raw_error_output",
                message="Raw LLM/client error output remains in generated content.",
                section=content_type,
                phrase="ERROR:",
            )
        )

    if is_health_adjacent_category(context.category):
        lowered = normalize_text(text)
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if normalize_text(phrase) in lowered:
                issues.append(
                    OutputQualityIssue(
                        code="forbidden_claim_phrase",
                        message=f"Forbidden health-adjacent claim phrase remains: {phrase}",
                        section=content_type,
                        phrase=phrase,
                    )
                )

    for pattern in FORBIDDEN_BUSINESS_KPI_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            issues.append(
                OutputQualityIssue(
                    code="forbidden_business_kpi",
                    message=f"Unsupported business KPI phrase remains: {pattern}",
                    section=content_type,
                    phrase=pattern,
                )
            )

    malformed_target_patterns = [
        r"target a detectable begin generating measurable share of voice",
        r"target begin generating measurable share of voice",
        r"aim for a begin generating",
        r"increase begin generating prompt-level visibility",
        r"achieve a begin generating",
        r"achieve begin generating",
        r"achieving a begin generating",
        r"achieving begin generating",
        r"visibility score above \d+",
        r"average visibility score above \d+",
        r"increase average visibility score to above \d+",
        r"increase mentions from \d+(?:\.\d+)? to \d+\s*-\s*\d+",
        r"move from \d+(?:\.\d+)? visibility to \d+(?:\.\d+)? or more",
        r"establish presence in \d+\s*-\s*\d+ relevant prompt categories",
        r"achieve visibility in at least \d+\s*-\s*\d+ relevant prompt categories",
        r"gain visibility in \d+\s*-\s*\d+ prompt categories",
        r"generate \d+\s*-\s*\d+ mentions",
        r"establish a recognizable presence in local searches and begin to capture share of voice",
        r"should each aim to increase from \d+(?:\.\d+)? to at least \d+\s*-\s*\d+",
        r"goal of achieving at least \d+(?:\.\d+)?% share of voice",
        r"goal of achieving \d+(?:\.\d+)?% share of voice",
        r"reach \d+(?:\.\d+)?% share of voice",
        r"achieve \d+(?:\.\d+)?% share of voice",
        r"target \d+(?:\.\d+)?% share of voice",
        r"target a benchmark of \d+(?:\.\d+)?% share of voice(?: in [^.]+)?",
        r"capture \d+(?:\.\d+)?% share of voice",
        r"at least \d+(?:\.\d+)?% share of voice",
        r"aim to reach at least \d+\s*(?:-\s*\d+)?",
        r"average visibility score \(target \d+(?:\.\d+)?\)",
        r"share of voice \(aim for \d+(?:\.\d+)?%\)",
        r"total mentions \(aim to reach at least \d+\s*(?:-\s*\d+)?\)",
        r"target \d+(?:\.\d+)?\)",
        r"aim for \d+(?:\.\d+)?%\)",
        r"aim for at least \d+\s*(?:-\s*\d+)? mentions",
        r"at least \d+\s*(?:-\s*\d+)? detectable mentions",
        r"at least \d+\s*(?:-\s*\d+)? mentions",
        r"visible in at least \d+\s*(?:-\s*\d+)? prompt categories",
        r"move toward being visible in \d+\s*-\s*\d+ relevant prompt categories",
        r"achieve visibility in \d+\s*-\s*\d+ relevant prompt categories",
        r"achieve initial visibility in at least \d+\s*-\s*\d+ relevant prompt categories",
        r"initial visibility in at least \d+\s*-\s*\d+ relevant prompt categories",
        r"a begin generating measurable share of voice",
        r"visibility in \d+\s*-\s*\d+ relevant prompt categories",
        r"gain initial mentions",
        r"aiming for begin generating",
        r"achieve initial mentions",
        r"above \d+(?:\.\d+)?",
        r"at least \d+(?:\.\d+)?%",
    ]

    for pattern in malformed_target_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            issues.append(
                OutputQualityIssue(
                    code="malformed_conservative_target",
                    message="Malformed conservative target wording remains.",
                    section=content_type,
                    phrase=pattern,
                )
            )

    if is_quick_test_mode(context.run_mode):
        for unit in _iter_text_quality_units(text):
            if _is_quick_test_numeric_target_statement(unit):
                issues.append(
                    OutputQualityIssue(
                        code="quick_test_numeric_target",
                        message="Quick Test output contains concrete numeric target language.",
                        section=content_type,
                        phrase=unit.strip(),
                    )
                )

    artifact_phrases = [
        "where substantiated and compliant showing",
        "where substantiated and compliant product claims",
        "where substantiated and compliant Data",
        "claims support documentation, where substantiated and compliant Data",
        "Research studies or claims support documentation, where substantiated and compliant",
        "claims support documentation, where substantiated and compliant supporting product claims",
        "claims support documentation, where substantiated and compliant or research",
        "Publishing results from claims support documentation, where substantiated and compliant",
        "(Source: AI-discovered market signal)s)",
        "(Source: Tracked competitor)s)",
        "substantiated product evidence",
        "business outcomes Performance Metrics",
        "business outcome Performance Metrics",
        "Evidence Support-focused",
        "claims support-focused",
    ]

    for phrase in artifact_phrases:
        if phrase.lower() in text.lower():
            issues.append(
                OutputQualityIssue(
                    code="sanitizer_artifact",
                    message=f"Sanitizer artifact remains: {phrase}",
                    section=content_type,
                    phrase=phrase,
                )
            )

    if is_health_adjacent_category(context.category):
        latest_geo_title_patterns = [
            r"Protects Your Skin",
            r"The Science Behind [^|\n]+ for Skin Health",
        ]

        for pattern in latest_geo_title_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                issues.append(
                    OutputQualityIssue(
                        code="forbidden_geo_claim_title",
                        message="High-risk GEO roadmap title remains.",
                        section=content_type,
                        phrase=pattern,
                    )
                )

    issues.extend(
        _find_competitor_advantage_source_issues(
            text,
            context,
            content_type,
        )
    )

    for line in _extract_ai_discovered_section_lines(text):
        stripped = line.strip()
        entity = _extract_bullet_entity(line)

        if not stripped:
            continue

        if "No additional non-tracked brands" in stripped:
            continue

        if (
            _contains_invalid_brand_item(entity)
            or _contains_invalid_brand_item(stripped)
            or not is_likely_brand_bullet(line)
        ):
            issues.append(
                OutputQualityIssue(
                    code="invalid_ai_discovered_brand_item",
                    message="AI-Discovered Brands section contains a non-brand item.",
                    section="AI-Discovered Brands",
                    phrase=stripped,
                )
            )

        if entity and _is_tracked_brand(entity, context.tracked_competitors):
            issues.append(
                OutputQualityIssue(
                    code="tracked_competitor_in_ai_discovered",
                    message="Tracked competitor appears under AI-Discovered Brands.",
                    section="AI-Discovered Brands",
                    phrase=entity,
                )
            )

    return issues


def format_quality_issues(issues: list[OutputQualityIssue]) -> str:
    if not issues:
        return "No output quality issues detected."

    return "\n".join(
        f"- [{issue.severity}] {issue.code}: {issue.message}"
        + (f" ({issue.phrase})" if issue.phrase else "")
        for issue in issues
    )
