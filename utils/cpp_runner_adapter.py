import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNNER_CPP_DIR = PROJECT_ROOT / "runner-cpp"
OUTPUT_DIR = PROJECT_ROOT / "output"

RUNNER_CANDIDATES = [
    RUNNER_CPP_DIR / "build" / "runner.exe",
    RUNNER_CPP_DIR / "build" / "Release" / "runner.exe",
    RUNNER_CPP_DIR / "build" / "Debug" / "runner.exe",
]


def find_cpp_runner():
    """Return the first compiled C++ runner executable if it exists."""
    for candidate in RUNNER_CANDIDATES:
        if candidate.exists():
            return candidate

    return None


def _fallback(reason):
    return {
        "success": False,
        "blocked": False,
        "fallback": True,
        "runner_mode": "python",
        "runner_warning": reason,
        "stdout": "",
        "stderr": "",
        "returncode": 1,
        "duration_ms": 0,
    }


def run_with_cpp_runner(code_file: str, timeout_seconds: int = 10, working_dir: str | None = None) -> dict:
    """Run generated code with the optional C++ runner.

    When the C++ runner is not built, this returns a fallback marker so the
    normal Python runner can continue to preserve v1 compatibility.
    """
    runner_path = find_cpp_runner()
    if not runner_path:
        return _fallback("C++ runner executable not found; fallback to Python runner")

    code_path = Path(code_file)
    if not code_path.is_absolute():
        code_path = PROJECT_ROOT / code_path

    work_path = Path(working_dir) if working_dir else code_path.parent
    if not work_path.is_absolute():
        work_path = PROJECT_ROOT / work_path

    OUTPUT_DIR.mkdir(exist_ok=True)
    task_path = OUTPUT_DIR / "cpp_runner_task.json"
    task_payload = {
        "code_file": code_path.as_posix(),
        "timeout_seconds": int(timeout_seconds or 10),
        "working_dir": work_path.as_posix(),
        "allow_network": False,
    }
    task_path.write_text(json.dumps(task_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        result = subprocess.run(
            [str(runner_path), str(task_path)],
            capture_output=True,
            text=True,
            timeout=max(int(timeout_seconds or 10) + 2, 3),
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as error:
        return {
            "success": False,
            "blocked": False,
            "fallback": False,
            "runner_mode": "cpp",
            "runner_warning": "C++ runner process timeout",
            "stdout": error.stdout or "",
            "stderr": error.stderr or "C++ runner process timeout",
            "returncode": 1,
            "duration_ms": 0,
        }

    raw_output = (result.stdout or "").strip()
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "success": False,
            "blocked": False,
            "fallback": False,
            "runner_mode": "cpp",
            "runner_warning": "C++ runner returned non-JSON output",
            "stdout": raw_output,
            "stderr": result.stderr or "",
            "returncode": result.returncode,
            "duration_ms": 0,
        }

    payload.setdefault("stdout", "")
    payload.setdefault("stderr", "")
    payload.setdefault("returncode", result.returncode)
    payload.setdefault("blocked", False)
    payload.setdefault("duration_ms", 0)
    payload["fallback"] = False
    payload["runner_mode"] = "cpp"
    payload["runner_warning"] = ""

    if payload.get("blocked"):
        payload["stderr"] = payload.get("stderr") or payload.get("reason", "")

    return payload


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(OUTPUT_DIR / "generated_code.py")
    print(json.dumps(run_with_cpp_runner(target), ensure_ascii=False, indent=2))
