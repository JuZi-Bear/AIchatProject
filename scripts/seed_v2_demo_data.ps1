param(
    [string]$JavaApiBaseUrl = "http://127.0.0.1:8088/api",
    [string]$VueBaseUrl = "http://127.0.0.1:5174",
    [string]$TemplateKey = "demo_workflow_template_showcase",
    [switch]$SkipAgentRun,
    [switch]$SkipCodeAgent,
    [switch]$SkipWorkflowTemplate
)

$ErrorActionPreference = "Stop"

$baseUrl = $JavaApiBaseUrl.TrimEnd("/")
$vueUrl = $VueBaseUrl.TrimEnd("/")
$timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()

function Invoke-JsonPost {
    param(
        [string]$Url,
        [object]$Payload,
        [int]$TimeoutSec = 240
    )

    $json = $Payload | ConvertTo-Json -Depth 40
    return Invoke-RestMethod -Method Post -Uri $Url -Body $json -ContentType "application/json" -TimeoutSec $TimeoutSec
}

function Assert-ApiResponse {
    param(
        [object]$Response,
        [string]$StepName
    )

    if (-not $Response.success) {
        throw "$StepName failed: $($Response.message)"
    }
}

function Get-PlatformRunId {
    param([object]$Response)

    if ($Response.platformRunId) {
        return [string]$Response.platformRunId
    }

    if ($Response.platform_run_id) {
        return [string]$Response.platform_run_id
    }

    if ($Response.data -and $Response.data.platformRunId) {
        return [string]$Response.data.platformRunId
    }

    if ($Response.data -and $Response.data.platform_run_id) {
        return [string]$Response.data.platform_run_id
    }

    return ""
}

Invoke-RestMethod -Method Get -Uri "$baseUrl/health" -TimeoutSec 15 | Out-Null
Invoke-RestMethod -Method Get -Uri "$baseUrl/agent/health" -TimeoutSec 15 | Out-Null

$summary = [ordered]@{
    success = $true
    generatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    javaApiBaseUrl = $baseUrl
    vueBaseUrl = $vueUrl
    agentRun = $null
    codeAgentRun = $null
    workflowTemplateRun = $null
    links = [ordered]@{
        dashboard = "$vueUrl/"
        history = "$vueUrl/history"
    }
}

if (-not $SkipAgentRun) {
    $agentPayload = [ordered]@{
        requirement = "Demo task: create a minimal Python script that prints Hello World and exits without user input."
        model_provider = "deepseek"
        enabled_plugins = @("Doc Agent", "Security Agent")
        max_retry_count = 2
        require_human_approval = $false
        demo_mode = $true
        offline_mode = $true
    }

    $agentResponse = Invoke-JsonPost -Url "$baseUrl/runs" -Payload $agentPayload -TimeoutSec 300
    $agentPlatformRunId = Get-PlatformRunId -Response $agentResponse
    $agentSuccess = [bool]($agentResponse.run_summary.success)

    $summary.agentRun = [ordered]@{
        platformRunId = $agentPlatformRunId
        runId = $agentResponse.run_id
        success = $agentSuccess
        qualityScore = $agentResponse.run_summary.quality_score
        runnerMode = $agentResponse.run_summary.runner_mode
        historyUrl = if ($agentPlatformRunId) { "$vueUrl/history?run_id=$agentPlatformRunId" } else { "$vueUrl/history" }
        replayUrl = if ($agentPlatformRunId) { "$vueUrl/replay/$agentPlatformRunId" } else { "" }
    }
}

if (-not $SkipCodeAgent) {
    $codeAgentPlatformRunId = "code_agent_demo_$timestamp"
    $codeAgentPath = "output/demo_code_agent_$timestamp.txt"
    $codeAgentPayload = [ordered]@{
        platformRunId = $codeAgentPlatformRunId
        operation = "write_file"
        filePath = $codeAgentPath
        content = "CodeAgent demo file generated at $timestamp.`nThis file is safe demo output for Dashboard / History / Replay."
    }
    $codeAgentResponse = Invoke-JsonPost -Url "$baseUrl/code-agent/execute" -Payload $codeAgentPayload -TimeoutSec 60
    Assert-ApiResponse -Response $codeAgentResponse -StepName "create CodeAgent demo run"

    $summary.codeAgentRun = [ordered]@{
        platformRunId = $codeAgentPlatformRunId
        success = [bool]$codeAgentResponse.data.success
        filePath = $codeAgentResponse.data.filePath
        auditLogPath = $codeAgentResponse.data.auditLogPath
        historyUrl = "$vueUrl/history?run_id=$codeAgentPlatformRunId"
        replayUrl = "$vueUrl/replay/$codeAgentPlatformRunId"
    }
}

if (-not $SkipWorkflowTemplate) {
    $templatePayload = [ordered]@{
        workflowTemplateKey = $TemplateKey
        name = "比赛演示 Workflow 模板"
        description = "用于一键生成 Dashboard / History / Replay 演示数据的 MySQL Workflow 模板。"
        nodes = @(
            [ordered]@{
                nodeId = "product_demo_1"
                agentKey = "product"
                name = "Product Agent"
                position = [ordered]@{ x = 80; y = 80 }
                input_fields = @("requirement")
                output_fields = @("product_result")
                stage = "analysis"
                enabled = $true
                description = "拆解演示需求"
            },
            [ordered]@{
                nodeId = "coder_demo_2"
                agentKey = "coder"
                name = "Coder Agent"
                position = [ordered]@{ x = 340; y = 80 }
                input_fields = @("product_result")
                output_fields = @("code")
                stage = "generation"
                enabled = $true
                description = "生成演示代码"
            },
            [ordered]@{
                nodeId = "code_agent_demo_3"
                agentKey = "code_agent"
                name = "CodeAgent"
                position = [ordered]@{ x = 600; y = 80 }
                input_fields = @("code")
                output_fields = @("code_agent_result")
                stage = "file_operation"
                enabled = $true
                description = "写入或读取项目文件"
            },
            [ordered]@{
                nodeId = "quality_demo_4"
                agentKey = "quality"
                name = "Quality Evaluator"
                position = [ordered]@{ x = 860; y = 80 }
                input_fields = @("test_result")
                output_fields = @("quality_score")
                stage = "quality"
                enabled = $true
                description = "质量评分"
            },
            [ordered]@{
                nodeId = "report_demo_5"
                agentKey = "report"
                name = "Report Generator"
                position = [ordered]@{ x = 1120; y = 80 }
                input_fields = @("quality_score")
                output_fields = @("report")
                stage = "report"
                enabled = $true
                description = "报告生成"
            }
        )
        connections = @(
            [ordered]@{ fromNodeId = "product_demo_1"; toNodeId = "coder_demo_2" },
            [ordered]@{ fromNodeId = "coder_demo_2"; toNodeId = "code_agent_demo_3" },
            [ordered]@{ fromNodeId = "code_agent_demo_3"; toNodeId = "quality_demo_4" },
            [ordered]@{ fromNodeId = "quality_demo_4"; toNodeId = "report_demo_5" }
        )
        version = "1.0"
    }

    $templateSaveResponse = Invoke-JsonPost -Url "$baseUrl/platform/workflows/templates" -Payload $templatePayload -TimeoutSec 60
    Assert-ApiResponse -Response $templateSaveResponse -StepName "save demo workflow template"

    $instantiateResponse = Invoke-JsonPost `
        -Url "$baseUrl/platform/workflows/templates/$TemplateKey/instantiate" `
        -Payload @{
            input_data = @{
                requirement = "比赛演示：从 MySQL Workflow 模板生成可回放任务视图"
            }
        } `
        -TimeoutSec 60
    Assert-ApiResponse -Response $instantiateResponse -StepName "instantiate demo workflow template"

    $templatePlatformRunId = Get-PlatformRunId -Response $instantiateResponse
    $replayResponse = Invoke-RestMethod -Method Get -Uri "$baseUrl/platform/runs/$templatePlatformRunId/replay" -TimeoutSec 30
    Assert-ApiResponse -Response $replayResponse -StepName "verify demo workflow replay"

    $summary.workflowTemplateRun = [ordered]@{
        templateKey = $TemplateKey
        templateVersion = $templateSaveResponse.data.version
        platformRunId = $templatePlatformRunId
        replayEventCount = @($replayResponse.data.events).Count
        historyUrl = "$vueUrl/history?run_id=$templatePlatformRunId"
        replayUrl = "$vueUrl/replay/$templatePlatformRunId"
    }
}

$platformRuns = Invoke-RestMethod -Method Get -Uri "$baseUrl/platform/runs" -TimeoutSec 30
Assert-ApiResponse -Response $platformRuns -StepName "list platform runs"
$summary.platformRunCount = @($platformRuns.data).Count

$summary | ConvertTo-Json -Depth 30
