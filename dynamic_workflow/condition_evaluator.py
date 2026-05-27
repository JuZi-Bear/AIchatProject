from __future__ import annotations

import re
from typing import Any


ALLOWED_STATE_FIELDS = {
    "success",
    "test_success",
    "approved",
    "retry_count",
    "max_retry_count",
    "quality_score",
    "coverage_percent",
    "error_log",
    "sentry_result",
    "code",
    "stdout",
    "status",
}

CONDITION_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(==|!=|>=|<=|>|<)\s*(true|false|null|none|-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\")\s*$",
    re.IGNORECASE,
)


def normalize_condition(condition: str | None) -> str:
    return (condition or "").strip()


def validate_condition(condition: str | None) -> tuple[bool, str]:
    normalized = normalize_condition(condition)

    if not normalized or normalized.lower() in {"always", "else", "default"}:
        return True, ""

    match = CONDITION_RE.match(normalized)

    if not match:
        return False, "条件表达式只支持白名单字段与常量比较，例如 success == true"

    field_name = match.group(1)

    if field_name not in ALLOWED_STATE_FIELDS:
        return False, f"条件字段不在白名单内: {field_name}"

    return True, ""


def _literal_value(raw: str) -> Any:
    normalized = raw.strip()
    lower = normalized.lower()

    if lower == "true":
        return True

    if lower == "false":
        return False

    if lower in {"null", "none"}:
        return None

    if (normalized.startswith("'") and normalized.endswith("'")) or (
        normalized.startswith('"') and normalized.endswith('"')
    ):
        return normalized[1:-1]

    if "." in normalized:
        try:
            return float(normalized)
        except ValueError:
            return normalized

    try:
        return int(normalized)
    except ValueError:
        return normalized


def _compare(left: Any, operator: str, right: Any) -> bool:
    if operator == "==":
        return left == right

    if operator == "!=":
        return left != right

    try:
        left_number = float(left)
        right_number = float(right)
    except (TypeError, ValueError):
        return False

    if operator == ">":
        return left_number > right_number
    if operator == "<":
        return left_number < right_number
    if operator == ">=":
        return left_number >= right_number
    if operator == "<=":
        return left_number <= right_number

    return False


def evaluate_condition(condition: str | None, state: dict[str, Any]) -> bool:
    normalized = normalize_condition(condition)

    if not normalized or normalized.lower() in {"always", "default"}:
        return True

    if normalized.lower() == "else":
        return False

    valid, _ = validate_condition(normalized)
    if not valid:
        return False

    match = CONDITION_RE.match(normalized)
    if not match:
        return False

    field_name, operator, literal = match.groups()
    return _compare(state.get(field_name), operator, _literal_value(literal))
