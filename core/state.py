from typing import TypedDict


class AgentState(TypedDict, total=False):
    requirement: str
    product_result: str
    code: str
    tester_result: str
    test_code: str
    test_stdout: str
    test_stderr: str
    test_success: bool
    coverage_stdout: str
    coverage_percent: int
    stdout: str
    error_log: str
    retry_count: int
    max_retry_count: int
    success: bool
    sentry_result: str
    approved: bool
    approval_message: str
    require_human_approval: bool
    model_provider: str
    model_name: str
    model_base_url: str
    enabled_plugins: list
    doc_result: str
    security_result: str
    refactor_result: str
    ui_result: str
    plugin_results: list
    quality_score: int
    quality_summary: str
    run_id: str
    report_path: str

