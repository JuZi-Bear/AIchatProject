import json
from datetime import datetime
from pathlib import Path

from config.config_loader import get_setting
from utils.workflow_event_builder import create_workflow_event


PROJECT_ROOT = Path.cwd().resolve()


def _get_config() -> dict:
    config = get_setting("code_agent", {}) or {}
    if not isinstance(config, dict):
        return {}

    return config


def _resolve_config_path(path_value: str) -> Path:
    raw_path = Path(str(path_value).replace("\\", "/"))
    if raw_path.is_absolute():
        return raw_path.resolve()

    return (PROJECT_ROOT / raw_path).resolve()


def _is_within(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _configured_paths(key: str, fallback: list[str]) -> list[Path]:
    values = _get_config().get(key, fallback)
    if not isinstance(values, list):
        values = fallback

    return [_resolve_config_path(value) for value in values]


def _check_enabled():
    if not bool(_get_config().get("enabled", True)):
        raise ValueError("CodeAgent 当前已在 config/settings.yaml 中禁用")


def _check_path_policy(target_path: Path, relative_path: str):
    _check_enabled()
    allowed_paths = _configured_paths("allowed_paths", ["."])
    blocked_paths = _configured_paths("blocked_paths", [".git", ".venv", "node_modules", ".env"])

    for blocked_path in blocked_paths:
        if _is_within(target_path, blocked_path):
            raise ValueError(f"CodeAgent 路径被禁止访问：{relative_path}")

    if not any(_is_within(target_path, allowed_path) for allowed_path in allowed_paths):
        allowed_text = ", ".join(_relative_path(path) for path in allowed_paths if _is_within(path, PROJECT_ROOT))
        raise ValueError(f"CodeAgent 路径不在白名单内：{relative_path}；允许范围：{allowed_text}")


def _normalize_project_path(file_path: str) -> tuple[Path, str]:
    if not file_path or not str(file_path).strip():
        raise ValueError("filePath 不能为空")

    raw_path = Path(str(file_path).replace("\\", "/"))

    if raw_path.is_absolute():
        target_path = raw_path.resolve()
    else:
        target_path = (PROJECT_ROOT / raw_path).resolve()

    if PROJECT_ROOT not in target_path.parents and target_path != PROJECT_ROOT:
        raise ValueError("只能操作项目目录内的文件")

    relative_path = _relative_path(target_path)
    _check_path_policy(target_path, relative_path)
    return target_path, relative_path


def _write_audit_record(operation: str, file_path: str, status: str, success: bool, message: str, detail=None) -> str:
    audit_path = _resolve_config_path(_get_config().get("audit_log_path", "output/code_agent_audit.jsonl"))

    if not _is_within(audit_path, PROJECT_ROOT):
        return ""

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "agent": "code_agent",
        "operation": operation,
        "filePath": file_path,
        "status": status,
        "success": success,
        "message": message,
        "detail": detail or {},
    }

    try:
        with audit_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        return _relative_path(audit_path)
    except OSError:
        return ""


def _operation_started(operation: str, file_path: str):
    return create_workflow_event(
        "AGENT_STARTED",
        "CodeAgent 操作开始",
        agent="code_agent",
        status="RUNNING",
        message=f"开始执行 {operation}: {file_path}",
        detail={
            "operation": operation,
            "filePath": file_path,
        },
    )


def _operation_finished(operation: str, summary: dict, detail: dict | None = None):
    safe_summary = {
        key: value
        for key, value in summary.items()
        if key not in {"events", "content"}
    }
    payload = {
        "operation": operation,
        "summary": safe_summary,
    }

    if detail:
        payload.update(detail)

    return create_workflow_event(
        "AGENT_FINISHED",
        "CodeAgent 操作完成",
        agent="code_agent",
        status="SUCCESS",
        message=summary.get("message", "CodeAgent 操作完成"),
        detail=payload,
    )


def _operation_failed(operation: str, file_path: str, error: Exception):
    return create_workflow_event(
        "AGENT_FAILED",
        "CodeAgent 操作失败",
        agent="code_agent",
        status="FAILED",
        message=str(error),
        detail={
            "operation": operation,
            "filePath": file_path,
            "error": str(error),
        },
    )


def read_file(file_path: str, encoding: str = "utf-8") -> dict:
    target_path, relative_path = _normalize_project_path(file_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not target_path.exists():
        raise FileNotFoundError(f"文件不存在：{relative_path}")

    if not target_path.is_file():
        raise ValueError(f"目标不是文件：{relative_path}")

    content = target_path.read_text(encoding=encoding)
    max_read_chars = int(_get_config().get("max_read_chars", 200000) or 200000)
    truncated = False

    if max_read_chars > 0 and len(content) > max_read_chars:
        content = content[:max_read_chars]
        truncated = True

    return {
        "success": True,
        "filePath": relative_path,
        "message": "已读取文件内容" if not truncated else "已读取文件内容，结果已按 max_read_chars 截断",
        "content": content,
        "truncated": truncated,
    }


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> dict:
    target_path, relative_path = _normalize_project_path(file_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(str(content or ""), encoding=encoding)
    return {
        "success": True,
        "filePath": relative_path,
        "message": "已修改或生成文件内容",
    }


def list_files(directory_path: str, recursive: bool = False) -> dict:
    target_path, relative_path = _normalize_project_path(directory_path or ".")
    target_path.mkdir(parents=True, exist_ok=True)

    if not target_path.is_dir():
        raise ValueError(f"目标不是目录：{relative_path}")

    pattern = "**/*" if recursive else "*"
    files = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in sorted(target_path.glob(pattern))
        if path.is_file()
    ]

    return {
        "success": True,
        "filePath": relative_path,
        "message": "已列出项目文件",
        "files": files,
    }


def execute_code_agent_operation(operation_request: dict) -> dict:
    operation = str(operation_request.get("operation", "")).strip()
    file_path = str(
        operation_request.get("filePath")
        or operation_request.get("file_path")
        or operation_request.get("path")
        or ""
    ).strip()
    encoding = str(operation_request.get("encoding") or "utf-8")
    events = [_operation_started(operation, file_path)]
    audit_path = _write_audit_record(
        operation,
        file_path,
        "STARTED",
        True,
        "CodeAgent 操作开始",
    )

    try:
        if operation == "read_file":
            result = read_file(file_path, encoding=encoding)
            events.append(_operation_finished(operation, result, {"content_length": len(result.get("content", ""))}))
        elif operation == "write_file":
            result = write_file(file_path, str(operation_request.get("content") or ""), encoding=encoding)
            events.append(_operation_finished(operation, result))
        elif operation == "list_files":
            result = list_files(file_path, recursive=bool(operation_request.get("recursive", False)))
            events.append(_operation_finished(operation, result, {"file_count": len(result.get("files", []))}))
        else:
            raise ValueError(f"不支持的 CodeAgent 操作：{operation}")

        finish_audit_path = _write_audit_record(
            operation,
            result.get("filePath", file_path),
            "FINISHED",
            True,
            result.get("message", "CodeAgent 操作完成"),
            {
                "recursive": bool(operation_request.get("recursive", False)),
                "file_count": len(result.get("files", [])),
                "content_length": len(result.get("content", "")),
            },
        )
        result["operation"] = operation
        result["auditPath"] = finish_audit_path or audit_path
        result["events"] = events
        return result
    except Exception as error:
        fail_audit_path = _write_audit_record(
            operation,
            file_path,
            "FAILED",
            False,
            str(error),
        )
        events.append(_operation_failed(operation, file_path, error))
        return {
            "success": False,
            "filePath": file_path,
            "operation": operation,
            "message": str(error),
            "auditPath": fail_audit_path or audit_path,
            "events": events,
        }


def execute_code_agent(request: dict) -> dict:
    operations = request.get("operations")

    if not isinstance(operations, list) or not operations:
        operations = [request]

    results = [execute_code_agent_operation(operation or {}) for operation in operations]
    events = [event for result in results for event in result.get("events", [])]
    success = all(result.get("success", False) for result in results)

    return {
        "success": success,
        "agent": "code_agent",
        "operation": results[0].get("operation", "") if len(results) == 1 else "batch",
        "filePath": results[0].get("filePath", "") if len(results) == 1 else "",
        "message": "CodeAgent 操作完成" if success else "CodeAgent 操作存在失败项",
        "results": results,
        "events": events,
    }
