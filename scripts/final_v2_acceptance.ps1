param(
    [ValidateSet("java")]
    [string]$ApiMode = "java",

    [ValidateSet("temp", "existing")]
    [string]$MySqlMode = "temp",

    [int]$PythonPort = 8001,
    [int]$JavaPort = 8088,
    [int]$VuePort = 5174,
    [int]$TempMySqlPort = 3307,
    [int]$MySqlPort = 3306,

    [string]$MySqlUser = "root",
    [string]$MySqlPassword = "root",

    [switch]$SkipStartup,
    [switch]$SkipDemoSeed,
    [switch]$FastDemoSeed
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$JavaApiBaseUrl = "http://127.0.0.1:$JavaPort/api"
$PythonApiBaseUrl = "http://127.0.0.1:$PythonPort"
$VueBaseUrl = "http://127.0.0.1:$VuePort"
$Checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param(
        [string]$Name,
        [bool]$Success,
        [string]$Detail = ""
    )

    $script:Checks.Add([ordered]@{
        name = $Name
        success = $Success
        detail = $Detail
    }) | Out-Null
}

function Invoke-HealthCheck {
    param(
        [string]$Name,
        [string]$Url
    )

    try {
        Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 20 | Out-Null
        Add-Check -Name $Name -Success $true -Detail $Url
    } catch {
        Add-Check -Name $Name -Success $false -Detail $_.Exception.Message
        throw
    }
}

function Invoke-PageCheck {
    param(
        [string]$Name,
        [string]$Url
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20
        $ok = $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
        Add-Check -Name $Name -Success $ok -Detail "$Url status=$($response.StatusCode)"
        if (-not $ok) {
            throw "$Name returned status $($response.StatusCode)"
        }
    } catch {
        Add-Check -Name $Name -Success $false -Detail $_.Exception.Message
        throw
    }
}

function Invoke-JsonScript {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock
    )

    $raw = & $ScriptBlock
    $text = ($raw | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "$Name returned empty output"
    }

    return $text | ConvertFrom-Json
}

Write-Host "== AIchatProject v2 final acceptance =="
Write-Host "Project root: $ProjectRoot"
Write-Host "Java API: $JavaApiBaseUrl"
Write-Host "Python API: $PythonApiBaseUrl"
Write-Host "Vue: $VueBaseUrl"

if (-not $SkipStartup) {
    Write-Host ""
    Write-Host "== Start local v2 stack =="
    & (Join-Path $PSScriptRoot "start_v2_local.ps1") `
        -ApiMode $ApiMode `
        -MySqlMode $MySqlMode `
        -PythonPort $PythonPort `
        -JavaPort $JavaPort `
        -VuePort $VuePort `
        -TempMySqlPort $TempMySqlPort `
        -MySqlPort $MySqlPort `
        -MySqlUser $MySqlUser `
        -MySqlPassword $MySqlPassword `
        -SkipSmoke
    Add-Check -Name "local stack startup" -Success $true -Detail "start_v2_local.ps1 completed"
}

Write-Host ""
Write-Host "== API health checks =="
Invoke-HealthCheck -Name "Python API /health" -Url "$PythonApiBaseUrl/health"
Invoke-HealthCheck -Name "Java Gateway /api/health" -Url "$JavaApiBaseUrl/health"
Invoke-HealthCheck -Name "Java -> Python /api/agent/health" -Url "$JavaApiBaseUrl/agent/health"
Invoke-HealthCheck -Name "Java platform runs" -Url "$JavaApiBaseUrl/platform/runs"
Invoke-HealthCheck -Name "Java recent events" -Url "$JavaApiBaseUrl/platform/events/recent"
Invoke-HealthCheck -Name "Java workflow templates" -Url "$JavaApiBaseUrl/platform/workflows/templates"

Write-Host ""
Write-Host "== Smoke tests =="
& (Join-Path $PSScriptRoot "smoke_codeagent.ps1") `
    -ApiMode java `
    -JavaApiBaseUrl $JavaApiBaseUrl `
    -PythonApiBaseUrl $PythonApiBaseUrl `
    -CheckBlockedPath
Add-Check -Name "CodeAgent smoke with blocked path" -Success $true -Detail "SSE, events, replay, audit checked"

& (Join-Path $PSScriptRoot "smoke_workflow_template.ps1") -JavaApiBaseUrl $JavaApiBaseUrl
Add-Check -Name "Workflow template smoke" -Success $true -Detail "save, version bump, instantiate, replay, delete checked"

& (Join-Path $PSScriptRoot "smoke_workflow_runtime_lite.ps1") -JavaApiBaseUrl $JavaApiBaseUrl
Add-Check -Name "Workflow Runtime Lite smoke" -Success $true -Detail "execute, approval, replay and report checked"

& (Join-Path $PSScriptRoot "smoke_skill_export.ps1") -JavaApiBaseUrl $JavaApiBaseUrl -RunExportedScript
Add-Check -Name "Workflow Skill Export smoke" -Success $true -Detail "exported files, frontmatter and run_workflow.py checked"

& (Join-Path $PSScriptRoot "smoke_dynamic_runtime_context.ps1")
Add-Check -Name "Dynamic runtime context smoke" -Success $true -Detail "field-level connection values transferred"

$seedSummary = $null
if (-not $SkipDemoSeed) {
    Write-Host ""
    Write-Host "== Seed demo data =="
    $seedScript = {
        $seedParams = @{
            JavaApiBaseUrl = $JavaApiBaseUrl
            VueBaseUrl = $VueBaseUrl
        }

        if ($FastDemoSeed) {
            $seedParams.SkipAgentRun = $true
        }

        & (Join-Path $PSScriptRoot "seed_v2_demo_data.ps1") @seedParams
    }
    $seedSummary = Invoke-JsonScript -Name "seed_v2_demo_data.ps1" -ScriptBlock $seedScript
    Add-Check -Name "Seed v2 demo data" -Success ([bool]$seedSummary.success) -Detail "platformRunCount=$($seedSummary.platformRunCount)"
}

Write-Host ""
Write-Host "== Vue route checks =="
$routes = @(
    [ordered]@{ name = "Dashboard"; path = "/" },
    [ordered]@{ name = "RunConsole"; path = "/runs/new" },
    [ordered]@{ name = "History"; path = "/history" },
    [ordered]@{ name = "Reports"; path = "/reports" },
    [ordered]@{ name = "Models"; path = "/models" },
    [ordered]@{ name = "Plugins"; path = "/plugins" },
    [ordered]@{ name = "Agents"; path = "/agents" },
    [ordered]@{ name = "Workflow Templates"; path = "/workflows/templates" },
    [ordered]@{ name = "Workflow Editor"; path = "/workflows/editor" }
)

foreach ($route in $routes) {
    Invoke-PageCheck -Name "Vue $($route.name)" -Url "$VueBaseUrl$($route.path)"
}

if ($seedSummary -and $seedSummary.workflowTemplateRun -and $seedSummary.workflowTemplateRun.platformRunId) {
    Invoke-PageCheck `
        -Name "Vue Replay seeded workflow" `
        -Url "$VueBaseUrl/replay/$($seedSummary.workflowTemplateRun.platformRunId)"
}

$success = -not ($Checks | Where-Object { -not $_.success } | Select-Object -First 1)
$summary = [ordered]@{
    success = $success
    generatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    javaApiBaseUrl = $JavaApiBaseUrl
    pythonApiBaseUrl = $PythonApiBaseUrl
    vueBaseUrl = $VueBaseUrl
    checks = $Checks
    demoSeed = $seedSummary
    recommendedPages = [ordered]@{
        dashboard = "$VueBaseUrl/"
        runConsole = "$VueBaseUrl/runs/new"
        history = "$VueBaseUrl/history"
        workflowEditor = "$VueBaseUrl/workflows/editor"
    }
}

Write-Host ""
Write-Host "== Acceptance summary =="
$summary | ConvertTo-Json -Depth 40

if (-not $success) {
    throw "v2 final acceptance failed"
}
