from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from .api_cost_estimator import estimate_actual_usage_cost


_CURRENT_USAGE_TRACKER: ContextVar["UsageTracker | None"] = ContextVar(
    "geo_audit_current_usage_tracker",
    default=None,
)


def _get_attr_or_key(value, name, default=None):
    if value is None:
        return default

    if isinstance(value, dict):
        return value.get(name, default)

    return getattr(value, name, default)


def _safe_int(value):
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_openai_usage(response, fallback_model_name=None):
    model_name = (
        _get_attr_or_key(response, "model")
        or fallback_model_name
    )
    usage = _get_attr_or_key(response, "usage")

    if usage is None:
        return {
            "model_name": model_name,
            "usage_available": False,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    input_tokens = _safe_int(
        _get_attr_or_key(usage, "prompt_tokens")
        or _get_attr_or_key(usage, "input_tokens")
    ) or 0
    output_tokens = _safe_int(
        _get_attr_or_key(usage, "completion_tokens")
        or _get_attr_or_key(usage, "output_tokens")
    ) or 0
    total_tokens = _safe_int(_get_attr_or_key(usage, "total_tokens"))

    if total_tokens is None:
        total_tokens = input_tokens + output_tokens

    return {
        "model_name": model_name,
        "usage_available": True,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


@dataclass
class UsageTracker:
    model_name: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0
    calls_with_usage: int = 0
    calls_without_usage: int = 0

    def record_response(self, response, fallback_model_name=None):
        usage = extract_openai_usage(response, fallback_model_name)
        model_name = usage.get("model_name")

        if self.model_name is None and model_name:
            self.model_name = model_name

        self.call_count += 1

        if usage["usage_available"]:
            self.calls_with_usage += 1
            self.input_tokens += usage["input_tokens"]
            self.output_tokens += usage["output_tokens"]
            self.total_tokens += usage["total_tokens"]
        else:
            self.calls_without_usage += 1

    def to_summary(self):
        cost = estimate_actual_usage_cost(
            self.input_tokens,
            self.output_tokens,
            self.model_name,
        )
        usage_available = self.calls_with_usage > 0

        return {
            "model_name": self.model_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "call_count": self.call_count,
            "calls_with_usage": self.calls_with_usage,
            "calls_without_usage": self.calls_without_usage,
            "usage_available": usage_available,
            "pricing_available": cost["pricing_available"],
            "estimated_actual_cost_usd": (
                cost["estimated_actual_cost_usd"]
                if usage_available
                else None
            ),
            "pricing_label": cost["pricing_label"],
        }


def set_current_usage_tracker(tracker):
    return _CURRENT_USAGE_TRACKER.set(tracker)


def get_current_usage_tracker():
    return _CURRENT_USAGE_TRACKER.get()


def clear_current_usage_tracker():
    _CURRENT_USAGE_TRACKER.set(None)


@contextmanager
def track_api_usage(tracker=None):
    active_tracker = tracker or UsageTracker()
    token = set_current_usage_tracker(active_tracker)

    try:
        yield active_tracker
    finally:
        _CURRENT_USAGE_TRACKER.reset(token)


def record_openai_usage(response, fallback_model_name=None):
    tracker = get_current_usage_tracker()
    if tracker is None:
        return None

    tracker.record_response(response, fallback_model_name)
    return tracker
