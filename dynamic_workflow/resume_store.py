from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RUN_STORE_DIR = Path("runs") / "dynamic_workflows"


def _path_for(run_id: str) -> Path:
    safe_run_id = "".join(char for char in str(run_id) if char.isalnum() or char in {"_", "-"})
    return RUN_STORE_DIR / f"{safe_run_id}.json"


def save_dynamic_run(run_id: str, payload: dict[str, Any]) -> str:
    RUN_STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = _path_for(run_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path.as_posix()


def load_dynamic_run(run_id: str) -> dict[str, Any]:
    path = _path_for(run_id)

    if not path.exists():
        raise FileNotFoundError(f"dynamic workflow run not found: {run_id}")

    return json.loads(path.read_text(encoding="utf-8"))
