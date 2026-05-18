param(
    [ValidateSet("java", "python")]
    [string]$ApiMode = "java",

    [string]$JavaApiBaseUrl = "http://127.0.0.1:8088/api",
    [string]$PythonApiBaseUrl = "http://127.0.0.1:8001",
    [string]$FilePath = "output/code_agent_smoke.txt",
    [switch]$CheckBlockedPath
)

$ErrorActionPreference = "Stop"

$env:CODE_AGENT_SMOKE_MODE = $ApiMode
$env:CODE_AGENT_JAVA_API = $JavaApiBaseUrl.TrimEnd("/")
$env:CODE_AGENT_PYTHON_API = $PythonApiBaseUrl.TrimEnd("/")
$env:CODE_AGENT_FILE_PATH = $FilePath
$env:CODE_AGENT_CHECK_BLOCKED = if ($CheckBlockedPath) { "1" } else { "0" }

$python = @'
import json
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

mode = os.environ["CODE_AGENT_SMOKE_MODE"]
java_api = os.environ["CODE_AGENT_JAVA_API"]
python_api = os.environ["CODE_AGENT_PYTHON_API"]
file_path = os.environ["CODE_AGENT_FILE_PATH"]
check_blocked = os.environ.get("CODE_AGENT_CHECK_BLOCKED") == "1"
platform_run_id = f"code_agent_smoke_{int(time.time())}"
content = "# CodeAgent smoke test\n\ndef smoke_func():\n    return 'ok'\n"


def post_json(url, payload):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def run_java_smoke():
    events = []
    errors = []

    def read_sse():
        url = f"{java_api}/platform/runs/{platform_run_id}/events/stream"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                current_event = "message"
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    if line.startswith("event:"):
                        current_event = line.split(":", 1)[1].strip()
                    elif line.startswith("data:"):
                        data = line.split(":", 1)[1].strip()
                        try:
                            payload = json.loads(data)
                        except json.JSONDecodeError:
                            payload = {"raw": data}
                        events.append({"event": current_event, "data": payload})
                        if current_event == "final":
                            break
        except Exception as exc:
            errors.append(str(exc))

    thread = threading.Thread(target=read_sse, daemon=True)
    thread.start()
    time.sleep(1)

    response = post_json(
        f"{java_api}/code-agent/execute",
        {
            "platformRunId": platform_run_id,
            "operation": "write_file",
            "filePath": file_path,
            "content": content,
        },
    )
    thread.join(timeout=10)

    history = get_json(f"{java_api}/platform/runs/{platform_run_id}/events")
    replay = get_json(f"{java_api}/platform/runs/{platform_run_id}/replay")
    event_types = [item.get("eventType") for item in history.get("data", [])]
    sse_types = [
        item.get("data", {}).get("eventType")
        for item in events
        if isinstance(item.get("data"), dict)
    ]

    success = (
        response.get("success")
        and response.get("data", {}).get("success")
        and Path(file_path).exists()
        and "AGENT_STARTED" in event_types
        and "AGENT_FINISHED" in event_types
        and "RUN_SUCCESS" in event_types
        and "AGENT_STARTED" in sse_types
        and replay.get("success")
        and len(replay.get("data", {}).get("events", [])) >= 3
    )

    blocked_summary = None
    if check_blocked:
        blocked_id = f"code_agent_blocked_{int(time.time())}"
        blocked_response = post_json(
            f"{java_api}/code-agent/execute",
            {
                "platformRunId": blocked_id,
                "operation": "read_file",
                "filePath": ".env",
            },
        )
        blocked_replay = get_json(f"{java_api}/platform/runs/{blocked_id}/replay")
        blocked_types = [item.get("eventType") for item in blocked_replay.get("data", {}).get("events", [])]
        blocked_summary = {
            "platformRunId": blocked_id,
            "success": blocked_response.get("data", {}).get("success"),
            "eventTypes": blocked_types,
            "status": blocked_replay.get("data", {}).get("status"),
        }
        success = success and blocked_summary["success"] is False and "AGENT_FAILED" in blocked_types

    return {
        "mode": "java",
        "platformRunId": platform_run_id,
        "success": success,
        "fileExists": Path(file_path).exists(),
        "auditExists": Path("output/code_agent_audit.jsonl").exists(),
        "sseEventTypes": sse_types,
        "historyEventTypes": event_types,
        "replayEventCount": len(replay.get("data", {}).get("events", [])),
        "sseErrors": errors,
        "blocked": blocked_summary,
    }


def run_python_smoke():
    response = post_json(
        f"{python_api}/api/code-agent/execute",
        {
            "operation": "write_file",
            "filePath": file_path,
            "content": content,
        },
    )
    event_types = [event.get("event_type") for event in response.get("events", [])]
    success = (
        response.get("success")
        and Path(file_path).exists()
        and "AGENT_STARTED" in event_types
        and "AGENT_FINISHED" in event_types
        and Path("output/code_agent_audit.jsonl").exists()
    )
    return {
        "mode": "python",
        "success": success,
        "fileExists": Path(file_path).exists(),
        "auditExists": Path("output/code_agent_audit.jsonl").exists(),
        "eventTypes": event_types,
    }


summary = run_java_smoke() if mode == "java" else run_python_smoke()
print(json.dumps(summary, ensure_ascii=False, indent=2))

if not summary["success"]:
    sys.exit(1)
'@

$python | python -
if ($LASTEXITCODE -ne 0) {
    throw "CodeAgent smoke test failed"
}
