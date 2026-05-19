param(
    [string]$JavaApiBaseUrl = "http://127.0.0.1:8088/api",
    [string]$TemplateKey = ""
)

$ErrorActionPreference = "Stop"

$baseUrl = $JavaApiBaseUrl.TrimEnd("/")
if ([string]::IsNullOrWhiteSpace($TemplateKey)) {
    $TemplateKey = "workflow_template_smoke_{0}" -f ([DateTimeOffset]::Now.ToUnixTimeSeconds())
}

function Invoke-JsonPost {
    param(
        [string]$Url,
        [object]$Payload
    )

    $json = $Payload | ConvertTo-Json -Depth 30
    return Invoke-RestMethod -Method Post -Uri $Url -Body $json -ContentType "application/json" -TimeoutSec 30
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

$payload = [ordered]@{
    workflowTemplateKey = $TemplateKey
    name = "Smoke Test Workflow Template"
    description = "Created by scripts/smoke_workflow_template.ps1 to verify Java + MySQL workflow template persistence."
    nodes = @(
        [ordered]@{
            nodeId = "product_1"
            agentKey = "product"
            name = "Product Agent"
            position = [ordered]@{ x = 80; y = 80 }
            input_fields = @("requirement")
            output_fields = @("product_result")
            stage = "analysis"
            enabled = $true
            description = "Smoke test requirement analysis node"
        },
        [ordered]@{
            nodeId = "code_agent_2"
            agentKey = "code_agent"
            name = "CodeAgent"
            position = [ordered]@{ x = 340; y = 80 }
            input_fields = @("product_result")
            output_fields = @("code_agent_result")
            stage = "file_operation"
            enabled = $true
            description = "Smoke test file operation node"
        }
    )
    connections = @(
        [ordered]@{
            fromNodeId = "product_1"
            toNodeId = "code_agent_2"
        }
    )
    version = "1.0"
}

$saveResponse = Invoke-JsonPost -Url "$baseUrl/platform/workflows/templates" -Payload $payload
Assert-ApiResponse -Response $saveResponse -StepName "save workflow template"

$listResponse = Invoke-RestMethod -Method Get -Uri "$baseUrl/platform/workflows/templates" -TimeoutSec 30
Assert-ApiResponse -Response $listResponse -StepName "list workflow templates"

$detailResponse = Invoke-RestMethod -Method Get -Uri "$baseUrl/platform/workflows/templates/$TemplateKey" -TimeoutSec 30
Assert-ApiResponse -Response $detailResponse -StepName "get workflow template detail"

$found = $listResponse.data |
    Where-Object {
        $_.workflowTemplateKey -eq $TemplateKey -or
        $_.templateKey -eq $TemplateKey -or
        $_.key -eq $TemplateKey
    } |
    Select-Object -First 1

$detail = $detailResponse.data
$nodeCount = @($detail.nodes).Count
$connectionCount = @($detail.connections).Count
$agentSequence = @($detail.agent_sequence)
$stageSequence = @($detail.stage_sequence)

$success = $null -ne $found `
    -and $detail.workflowTemplateKey -eq $TemplateKey `
    -and $nodeCount -eq 2 `
    -and $connectionCount -eq 1 `
    -and ($agentSequence -contains "product") `
    -and ($agentSequence -contains "code_agent") `
    -and ($stageSequence -contains "analysis") `
    -and ($stageSequence -contains "file_operation")

$summary = [ordered]@{
    success = $success
    templateKey = $TemplateKey
    savedName = $saveResponse.data.name
    listed = $null -ne $found
    nodeCount = $nodeCount
    connectionCount = $connectionCount
    agentSequence = $agentSequence
    stageSequence = $stageSequence
    source = $detail.source
}

$summary | ConvertTo-Json -Depth 20

if (-not $success) {
    throw "Workflow template smoke test failed"
}
