import json
import fnmatch
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


def _display_path(path: Path) -> str:
    if _is_within(path, PROJECT_ROOT):
        return _relative_path(path)

    return path.as_posix()


def _configured_paths(key: str, fallback: list[str]) -> list[Path]:
    values = _get_config().get(key, fallback)
    if not isinstance(values, list):
        values = fallback

    return [_resolve_config_path(value) for value in values]


def _configured_int(key: str, fallback: int) -> int:
    try:
        return int(_get_config().get(key, fallback) or fallback)
    except (TypeError, ValueError):
        return fallback


def _configured_bool(key: str, fallback: bool) -> bool:
    value = _get_config().get(key, fallback)
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}

    return fallback


def _configured_list(key: str, fallback: list[str]) -> list[str]:
    values = _get_config().get(key, fallback)
    if not isinstance(values, list):
        return fallback

    return [str(value) for value in values]


def _check_enabled():
    if not bool(_get_config().get("enabled", True)):
        raise ValueError("CodeAgent 当前已在 config/settings.yaml 中禁用")


def _check_path_policy(target_path: Path, relative_path: str):
    _check_enabled()
    allowed_paths = _configured_paths("allowed_paths", ["."]) + _configured_paths("allowed_workspace_roots", [])
    blocked_paths = _configured_paths("blocked_paths", [".git", ".venv", "node_modules", ".env"])

    for blocked_path in blocked_paths:
        if _is_within(target_path, blocked_path):
            raise ValueError(f"CodeAgent 路径被禁止访问：{relative_path}")

    if not any(_is_within(target_path, allowed_path) for allowed_path in allowed_paths):
        allowed_text = ", ".join(_display_path(path) for path in allowed_paths)
        raise ValueError(f"CodeAgent 路径不在白名单内：{relative_path}；允许范围：{allowed_text}")


def _normalize_project_path(file_path: str) -> tuple[Path, str]:
    if not file_path or not str(file_path).strip():
        raise ValueError("filePath 不能为空")

    raw_path = Path(str(file_path).replace("\\", "/"))

    if raw_path.is_absolute():
        target_path = raw_path.resolve()
    else:
        target_path = (PROJECT_ROOT / raw_path).resolve()

    allowed_paths = _configured_paths("allowed_paths", ["."]) + _configured_paths("allowed_workspace_roots", [])

    if not any(_is_within(target_path, allowed_path) for allowed_path in allowed_paths):
        raise ValueError("只能操作项目目录内或 allowed_workspace_roots 白名单内的文件")

    display_path = _display_path(target_path)
    _check_path_policy(target_path, display_path)
    return target_path, display_path


def _split_patterns(value, fallback: list[str]) -> list[str]:
    if isinstance(value, str):
        patterns = [item.strip() for item in value.replace(";", ",").split(",")]
    elif isinstance(value, list):
        patterns = [str(item).strip() for item in value]
    else:
        patterns = fallback

    return [pattern for pattern in patterns if pattern]


def _matches_any(path_text: str, patterns: list[str]) -> bool:
    normalized = path_text.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(Path(normalized).name, pattern) for pattern in patterns)


def _is_text_file(path: Path) -> bool:
    extensions = {extension.lower() for extension in _configured_list("text_file_extensions", [".py", ".md", ".txt", ".json", ".yaml", ".yml"])}
    return path.suffix.lower() in extensions


def _line_diff(before: str, after: str) -> str:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    prefix = 0

    while prefix < len(before_lines) and prefix < len(after_lines) and before_lines[prefix] == after_lines[prefix]:
        prefix += 1

    before_suffix = len(before_lines) - 1
    after_suffix = len(after_lines) - 1

    while before_suffix >= prefix and after_suffix >= prefix and before_lines[before_suffix] == after_lines[after_suffix]:
        before_suffix -= 1
        after_suffix -= 1

    rows = [f" {line}" for line in before_lines[:prefix]]
    rows.extend(f"-{line}" for line in before_lines[prefix : before_suffix + 1])
    rows.extend(f"+{line}" for line in after_lines[prefix : after_suffix + 1])
    rows.extend(f" {line}" for line in before_lines[before_suffix + 1 :])
    return "\n".join(rows)


def _folder_file_candidates(base_path: Path, include_patterns: list[str], exclude_patterns: list[str], recursive: bool) -> tuple[list[Path], list[dict]]:
    pattern = "**/*" if recursive else "*"
    blocked_patterns = _configured_list("blocked_patterns", [".env", ".git/**", "node_modules/**", "dist/**", "target/**"])
    max_files = _configured_int("max_files_per_folder", 80)
    max_file_size = _configured_int("max_file_size_bytes", 200000)
    files: list[Path] = []
    blocked: list[dict] = []

    for path in sorted(base_path.glob(pattern)):
        if not path.is_file():
            continue

        relative_to_base = path.relative_to(base_path).as_posix()
        display_path = _display_path(path)

        try:
            _check_path_policy(path.resolve(), display_path)
        except ValueError as error:
            blocked.append({"filePath": display_path, "reason": str(error)})
            continue

        if _matches_any(display_path, blocked_patterns) or _matches_any(relative_to_base, blocked_patterns):
            blocked.append({"filePath": display_path, "reason": "命中 blocked_patterns"})
            continue

        if exclude_patterns and (_matches_any(display_path, exclude_patterns) or _matches_any(relative_to_base, exclude_patterns)):
            blocked.append({"filePath": display_path, "reason": "命中 exclude_patterns"})
            continue

        if include_patterns and not (_matches_any(display_path, include_patterns) or _matches_any(relative_to_base, include_patterns)):
            continue

        if not _is_text_file(path):
            blocked.append({"filePath": display_path, "reason": "非文本扩展名，已跳过"})
            continue

        if path.stat().st_size > max_file_size:
            blocked.append({"filePath": display_path, "reason": f"文件超过 max_file_size_bytes={max_file_size}"})
            continue

        files.append(path)

        if len(files) >= max_files:
            blocked.append({"filePath": display_path, "reason": f"达到 max_files_per_folder={max_files} 限制，后续文件已跳过"})
            break

    return files, blocked


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


def scan_folder(directory_path: str, include_patterns=None, exclude_patterns=None, recursive: bool = True) -> dict:
    target_path, relative_path = _normalize_project_path(directory_path or ".")
    target_path.mkdir(parents=True, exist_ok=True)

    if not target_path.is_dir():
        raise ValueError(f"目标不是目录：{relative_path}")

    includes = _split_patterns(include_patterns, ["**/*"])
    excludes = _split_patterns(exclude_patterns, [])
    files, blocked = _folder_file_candidates(target_path, includes, excludes, recursive)
    file_items = [
        {
            "filePath": _display_path(path),
            "relativePath": path.relative_to(target_path).as_posix(),
            "sizeBytes": path.stat().st_size,
            "extension": path.suffix.lower(),
        }
        for path in files
    ]

    return {
        "success": True,
        "filePath": relative_path,
        "message": "已扫描文件夹",
        "files": [item["filePath"] for item in file_items],
        "fileTree": file_items,
        "blockedFiles": blocked,
        "summary": {
            "baseDir": relative_path,
            "scannedFiles": len(file_items),
            "blockedFiles": len(blocked),
            "totalSizeBytes": sum(item["sizeBytes"] for item in file_items),
        },
    }


def read_folder(directory_path: str, include_patterns=None, exclude_patterns=None, recursive: bool = True, encoding: str = "utf-8") -> dict:
    target_path, relative_path = _normalize_project_path(directory_path or ".")
    target_path.mkdir(parents=True, exist_ok=True)

    if not target_path.is_dir():
        raise ValueError(f"目标不是目录：{relative_path}")

    includes = _split_patterns(include_patterns, ["**/*"])
    excludes = _split_patterns(exclude_patterns, [])
    files, blocked = _folder_file_candidates(target_path, includes, excludes, recursive)
    max_total_read_chars = _configured_int("max_total_read_chars", 500000)
    read_items = []
    total_chars = 0
    truncated = False

    for path in files:
        try:
            content = path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            blocked.append({"filePath": _display_path(path), "reason": "文件编码不是可读取文本，已跳过"})
            continue

        remaining = max_total_read_chars - total_chars if max_total_read_chars > 0 else len(content)

        if max_total_read_chars > 0 and remaining <= 0:
            truncated = True
            blocked.append({"filePath": _display_path(path), "reason": "达到 max_total_read_chars 限制，已跳过"})
            continue

        if max_total_read_chars > 0 and len(content) > remaining:
            content = content[:remaining]
            truncated = True

        total_chars += len(content)
        read_items.append(
            {
                "filePath": _display_path(path),
                "relativePath": path.relative_to(target_path).as_posix(),
                "content": content,
                "truncated": truncated,
            }
        )

    return {
        "success": True,
        "filePath": relative_path,
        "message": "已读取文件夹文本内容" if not truncated else "已读取文件夹文本内容，部分结果已截断",
        "folderFiles": read_items,
        "blockedFiles": blocked,
        "truncated": truncated,
        "summary": {
            "baseDir": relative_path,
            "readFiles": len(read_items),
            "blockedFiles": len(blocked),
            "totalReadChars": total_chars,
        },
    }


def _normalize_folder_changes(operation_request: dict, base_path: Path) -> list[dict]:
    changes = operation_request.get("changes")

    if isinstance(changes, list) and changes:
        return [change for change in changes if isinstance(change, dict)]

    output_file = str(operation_request.get("outputFile") or operation_request.get("output_file") or "code_agent_result.md")
    content = str(operation_request.get("content") or "")
    return [
        {
            "filePath": output_file,
            "content": content,
            "action": "create",
            "reason": "由 CodeAgent 文件夹模式生成的输出文件",
        }
    ]


def plan_folder_changes(operation_request: dict) -> dict:
    directory_path = str(operation_request.get("filePath") or operation_request.get("baseDir") or "").strip()
    target_path, relative_path = _normalize_project_path(directory_path or ".")
    target_path.mkdir(parents=True, exist_ok=True)

    if not target_path.is_dir():
        raise ValueError(f"目标不是目录：{relative_path}")

    planned_changes = []
    blocked = []

    for change in _normalize_folder_changes(operation_request, target_path):
        raw_file_path = str(change.get("filePath") or "").strip()

        if not raw_file_path:
            blocked.append({"filePath": "", "reason": "变更缺少 filePath"})
            continue

        change_path = Path(raw_file_path.replace("\\", "/"))
        target_file = change_path.resolve() if change_path.is_absolute() else (target_path / change_path).resolve()
        target_display = _display_path(target_file)

        if not _is_within(target_file, target_path):
            blocked.append({"filePath": target_display, "reason": "变更目标不能逃逸文件夹工作区"})
            continue

        try:
            _check_path_policy(target_file, target_display)
        except ValueError as error:
            blocked.append({"filePath": target_display, "reason": str(error)})
            continue

        blocked_patterns = _configured_list("blocked_patterns", [".env", ".git/**", "node_modules/**", "dist/**", "target/**"])
        relative_to_base = target_file.relative_to(target_path).as_posix()

        if _matches_any(target_display, blocked_patterns) or _matches_any(relative_to_base, blocked_patterns):
            blocked.append({"filePath": target_display, "reason": "命中 blocked_patterns"})
            continue

        before = target_file.read_text(encoding=str(operation_request.get("encoding") or "utf-8")) if target_file.exists() and target_file.is_file() else ""
        after = str(change.get("content") if change.get("content") is not None else change.get("after") or "")
        action = "update" if target_file.exists() else str(change.get("action") or "create")
        diff = _line_diff(before, after)

        planned_changes.append(
            {
                "filePath": target_display,
                "relativePath": relative_to_base,
                "action": action,
                "before": before,
                "after": after,
                "diff": diff,
                "reason": str(change.get("reason") or "CodeAgent 文件夹模式计划变更"),
            }
        )

    return {
        "success": True,
        "filePath": relative_path,
        "message": "已生成文件夹变更计划",
        "baseDir": relative_path,
        "changes": planned_changes,
        "blockedFiles": blocked,
        "dryRun": True,
        "summary": {
            "baseDir": relative_path,
            "plannedChanges": len(planned_changes),
            "blockedFiles": len(blocked),
            "actualWrites": 0,
        },
    }


def backup_folder_changes(operation_request: dict) -> dict:
    plan = plan_folder_changes(operation_request)
    backup_root = (PROJECT_ROOT / "output" / "code_agent_backups" / datetime.now().strftime("%Y%m%d_%H%M%S")).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)
    backups = []

    for change in plan.get("changes", []):
        target_path, target_display = _normalize_project_path(change["filePath"])

        if not target_path.exists() or not target_path.is_file():
            continue

        backup_path = backup_root / target_display.replace(":", "").replace("\\", "/")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(target_path.read_text(encoding=str(operation_request.get("encoding") or "utf-8")), encoding=str(operation_request.get("encoding") or "utf-8"))
        backups.append({"filePath": target_display, "backupPath": _display_path(backup_path)})

    return {
        "success": True,
        "filePath": plan.get("filePath", ""),
        "message": "已备份文件夹变更涉及文件",
        "backups": backups,
        "summary": {
            "backupCount": len(backups),
            "backupRoot": _display_path(backup_root),
        },
    }


def apply_folder_changes(operation_request: dict) -> dict:
    dry_run = bool(operation_request.get("dryRun", operation_request.get("dry_run", _configured_bool("dry_run_default", True))))
    backup_before_write = bool(
        operation_request.get(
            "backupBeforeWrite",
            operation_request.get("backup_before_write", _configured_bool("backup_before_write", True)),
        )
    )
    plan = plan_folder_changes(operation_request)
    backups = []
    actual_writes = 0

    if not dry_run and backup_before_write:
        backups = backup_folder_changes(operation_request).get("backups", [])

    if not dry_run:
        encoding = str(operation_request.get("encoding") or "utf-8")

        for change in plan.get("changes", []):
            if change.get("action") == "skip":
                continue

            target_path, _ = _normalize_project_path(change["filePath"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(str(change.get("after") or ""), encoding=encoding)
            actual_writes += 1

    return {
        **plan,
        "success": True,
        "message": "已预览文件夹变更计划" if dry_run else "已应用文件夹变更计划",
        "dryRun": dry_run,
        "backups": backups,
        "summary": {
            **plan.get("summary", {}),
            "actualWrites": actual_writes,
            "backupCount": len(backups),
        },
    }


def export_folder_result(operation_request: dict) -> dict:
    next_request = {
        **operation_request,
        "changes": [
            {
                "filePath": operation_request.get("outputFile") or "code_agent_result.md",
                "content": operation_request.get("content") or operation_request.get("result") or "",
                "action": "create",
                "reason": "导出 CodeAgent 输出结果",
            }
        ],
    }
    return apply_folder_changes(next_request)


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
        elif operation == "scan_folder":
            result = scan_folder(
                file_path,
                include_patterns=operation_request.get("includePatterns") or operation_request.get("include_patterns"),
                exclude_patterns=operation_request.get("excludePatterns") or operation_request.get("exclude_patterns"),
                recursive=bool(operation_request.get("recursive", True)),
            )
            events.append(
                _operation_finished(
                    operation,
                    result,
                    {
                        "file_count": len(result.get("files", [])),
                        "blocked_count": len(result.get("blockedFiles", [])),
                    },
                )
            )
        elif operation == "read_folder":
            result = read_folder(
                file_path,
                include_patterns=operation_request.get("includePatterns") or operation_request.get("include_patterns"),
                exclude_patterns=operation_request.get("excludePatterns") or operation_request.get("exclude_patterns"),
                recursive=bool(operation_request.get("recursive", True)),
                encoding=encoding,
            )
            events.append(
                _operation_finished(
                    operation,
                    result,
                    {
                        "read_count": len(result.get("folderFiles", [])),
                        "blocked_count": len(result.get("blockedFiles", [])),
                    },
                )
            )
        elif operation == "plan_folder_changes":
            result = plan_folder_changes(operation_request)
            events.append(
                _operation_finished(
                    operation,
                    result,
                    {
                        "planned_changes": len(result.get("changes", [])),
                        "blocked_count": len(result.get("blockedFiles", [])),
                    },
                )
            )
        elif operation == "apply_folder_changes":
            result = apply_folder_changes(operation_request)
            events.append(
                _operation_finished(
                    operation,
                    result,
                    {
                        "actual_writes": result.get("summary", {}).get("actualWrites", 0),
                        "dry_run": result.get("dryRun", True),
                    },
                )
            )
        elif operation == "backup_folder_changes":
            result = backup_folder_changes(operation_request)
            events.append(_operation_finished(operation, result, {"backup_count": len(result.get("backups", []))}))
        elif operation == "export_folder_result":
            result = export_folder_result(operation_request)
            events.append(
                _operation_finished(
                    operation,
                    result,
                    {
                        "actual_writes": result.get("summary", {}).get("actualWrites", 0),
                        "dry_run": result.get("dryRun", True),
                    },
                )
            )
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
                "planned_changes": len(result.get("changes", [])),
                "actual_writes": result.get("summary", {}).get("actualWrites", 0) if isinstance(result.get("summary"), dict) else 0,
                "blocked_count": len(result.get("blockedFiles", [])),
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
