param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$pythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$script = @'
from dynamic_workflow.runtime import execute_dynamic_workflow

template = {
    "workflowTemplateKey": "runtime_context_smoke",
    "name": "Runtime Context Smoke",
    "description": "Verify field-level runtime context transfer without model calls.",
    "nodes": [
        {
            "nodeId": "alpha",
            "agentKey": "custom_agent",
            "nodeType": "custom_agent",
            "name": "Alpha",
            "stage": "custom",
            "enabled": True,
            "input_fields": ["requirement"],
            "output_fields": ["alpha_result"],
        },
        {
            "nodeId": "beta",
            "agentKey": "custom_agent",
            "nodeType": "custom_agent",
            "name": "Beta",
            "stage": "custom",
            "enabled": True,
            "input_fields": ["beta_input"],
            "output_fields": ["beta_result"],
        },
    ],
    "connections": [
        {
            "fromNodeId": "alpha",
            "toNodeId": "beta",
            "fromOutputField": "alpha_result",
            "toInputField": "beta_input",
            "edgeType": "control",
            "dataType": "custom",
            "label": "alpha_result -> beta_input",
        }
    ],
}

result = execute_dynamic_workflow({
    "template": template,
    "input_data": {
        "requirement": "Runtime context smoke",
    },
})

runtime_context = result["ui_view_model"]["runtime_summary"]["runtime_context"]
transfers = runtime_context.get("transfers", [])
state = result.get("state", {})
node_inputs = runtime_context.get("node_inputs", {})
node_outputs = runtime_context.get("node_outputs", {})
alpha_output = node_outputs.get("alpha", {}).get("alpha_result", {})
beta_input = node_inputs.get("beta", {}).get("beta_input", {})
beta_output = node_outputs.get("beta", {}).get("beta_result", {})

ok = (
    result.get("status") == "SUCCESS"
    and len(transfers) == 1
    and transfers[0].get("fromOutputField") == "alpha_result"
    and transfers[0].get("toInputField") == "beta_input"
    and beta_input.get("preview") == alpha_output.get("preview")
    and "Alpha simulated output" in beta_output.get("preview", "")
)

import json
print(json.dumps({
    "success": ok,
    "status": result.get("status"),
    "betaInput": beta_input.get("preview"),
    "alphaResult": alpha_output.get("preview"),
    "betaResult": beta_output.get("preview"),
    "transferCount": len(transfers),
    "runtimeContext": runtime_context,
    "reportPath": result.get("run_summary", {}).get("report_path"),
}, ensure_ascii=False, indent=2))

if not ok:
    raise SystemExit(1)
'@

$output = $script | & $pythonExe -
$text = ($output | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($text)) {
    throw "Dynamic runtime context smoke returned empty output"
}

$text
