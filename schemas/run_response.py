from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UIWorkflowStep(BaseModel):
    key: str = ""
    label: str = ""
    status: str = ""
    summary: str = ""
    order: int = 0


class RunSummaryResponse(BaseModel):
    success: bool = False
    retry_count: int = 0
    test_success: bool = False
    coverage_percent: int = 0
    quality_score: int = 0
    security_status: str = ""
    enabled_plugins: List[str] = Field(default_factory=list)
    model_provider: str = ""
    report_path: str = ""
    runner_mode: str = "python"
    runner_warning: str = ""
    event_count: int = 0
    last_event: Dict[str, Any] = Field(default_factory=dict)
    workflow_event_summary: Dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str = ""
    state: Optional[Dict[str, Any]] = None
    run_summary: RunSummaryResponse = Field(default_factory=RunSummaryResponse)
    ui_view_model: Dict[str, Any] = Field(default_factory=dict)
