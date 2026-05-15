import json
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = PROJECT_ROOT / "runs"


def create_run_id():
    """Create a run id like run_20260427_153000."""
    while True:
        run_id = "run_" + datetime.now().strftime("%Y%m%d_%H%M%S")

        has_related_run = RUNS_DIR.exists() and any(RUNS_DIR.glob(f"{run_id}*.json"))

        if not get_run_state_path(run_id).exists() and not has_related_run:
            return run_id

        time.sleep(1)


def get_run_state_path(run_id):
    return RUNS_DIR / f"{run_id}.json"


def save_run_state(run_id, state):
    """Save one workflow state to runs/{run_id}.json."""
    RUNS_DIR.mkdir(exist_ok=True)
    state_path = get_run_state_path(run_id)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return state_path


def load_run_state(run_id):
    """Load one workflow state by run id."""
    state_path = get_run_state_path(run_id)

    if not state_path.exists():
        return None

    return json.loads(state_path.read_text(encoding="utf-8"))


def list_runs():
    """Return all run ids, newest first."""
    if not RUNS_DIR.exists():
        return []

    run_files = sorted(
        RUNS_DIR.glob("run_*.json"),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )
    return [file.stem for file in run_files]


def get_latest_run():
    """Return the newest run id, or None if there is no history."""
    runs = list_runs()

    if not runs:
        return None

    return runs[0]
