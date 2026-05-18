from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas.run_request import RunRequest
from schemas.run_response import RunResponse
from services.run_service import (
    create_run,
    get_available_agents,
    get_available_models,
    get_available_plugins,
    get_report,
    get_run,
    get_workflow_templates,
    instantiate_workflow_template,
    list_reports,
    list_run_history,
)
from utils.simple_code_agent import execute_code_agent


app = FastAPI(
    title="Python Agent Engine API",
    description="FastAPI wrapper for the v2.0 Python Agent Engine preview.",
    version="v2-api-preview",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()

    return model.dict()


def _build_run_response(result: dict, include_state: bool) -> dict:
    response = {
        "run_id": result.get("run_id", ""),
        "run_summary": result.get("run_summary", {}),
        "ui_view_model": result.get("ui_view_model", {}),
    }

    if include_state:
        response["state"] = result.get("state", {})

    return response


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "python-agent-engine",
        "version": "v2-api-preview",
    }


@app.get("/models")
def list_models():
    return get_available_models()


@app.get("/plugins")
def list_plugins():
    return get_available_plugins()


@app.get("/agents")
def list_agents():
    return get_available_agents()


@app.get("/api/workflows/templates")
def list_workflow_templates():
    return get_workflow_templates()


@app.post("/api/workflows/instantiate")
def instantiate_workflow(request: dict):
    try:
        return instantiate_workflow_template(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/code-agent/execute")
def execute_code_agent_operation(request: dict):
    return execute_code_agent(request or {})


@app.post("/runs", response_model=RunResponse, response_model_exclude_none=True)
def create_workflow_run(request: RunRequest):
    try:
        result = create_run(_model_to_dict(request))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return _build_run_response(result, include_state=True)


@app.get("/runs", response_model=list[dict])
def list_workflow_runs():
    return list_run_history()


@app.get("/runs/{run_id}", response_model=RunResponse)
def get_workflow_run(run_id: str):
    result = get_run(run_id)

    if not result.get("found", False):
        raise HTTPException(status_code=404, detail=f"run not found: {run_id}")

    return _build_run_response(result, include_state=True)


@app.get("/reports")
def list_markdown_reports():
    return list_reports()


@app.get("/reports/{report_name}")
def get_markdown_report(report_name: str):
    try:
        return get_report(report_name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
