param(
    [string]$JavaApiBaseUrl = "http://127.0.0.1:8088/api",
    [string]$TemplateKey = "",
    [switch]$RunExportedScript,
    [switch]$KeepTemplate
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$baseUrl = $JavaApiBaseUrl.TrimEnd("/")
if ([string]::IsNullOrWhiteSpace($TemplateKey)) {
    $TemplateKey = "skill_export_smoke_{0}" -f ([DateTimeOffset]::Now.ToUnixTimeSeconds())
}

function Invoke-JsonPost {
    param(
        [string]$Url,
        [object]$Payload = @{}
    )

    $json = $Payload | ConvertTo-Json -Depth 50
    return Invoke-RestMethod -Method Post -Uri $Url -Body $json -ContentType "application/json" -TimeoutSec 60
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

function Resolve-SkillPath {
    param([string]$SkillPath)

    $candidates = New-Object System.Collections.Generic.List[string]

    if ([System.IO.Path]::IsPathRooted($SkillPath)) {
        $candidates.Add($SkillPath) | Out-Null
    } else {
        $candidates.Add((Join-Path $ProjectRoot $SkillPath)) | Out-Null
        $candidates.Add((Join-Path (Join-Path $ProjectRoot "backend-java") $SkillPath)) | Out-Null
    }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "Cannot resolve exported skill path '$SkillPath'. Checked: $($candidates -join ', ')"
}

function Assert-FileExists {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path $Path -PathType Leaf)) {
        throw "$Label missing: $Path"
    }
}

function Assert-TextContains {
    param(
        [string]$Text,
        [string]$Pattern,
        [string]$Label
    )

    if ($Text -notmatch [regex]::Escape($Pattern)) {
        throw "$Label does not contain '$Pattern'"
    }
}

$payload = [ordered]@{
    workflowTemplateKey = $TemplateKey
    name = "Skill Export Smoke Workflow"
    description = "Created by scripts/smoke_skill_export.ps1 to verify Workflow Template to Codex Skill export."
    nodes = @(
        [ordered]@{
            nodeId = "custom_1"
            agentKey = "custom_agent"
            nodeType = "custom_agent"
            name = "Skill Export Demo Node"
            position = [ordered]@{ x = 120; y = 120 }
            input_fields = @("requirement")
            output_fields = @("custom_result")
            stage = "custom"
            enabled = $true
            description = "Simulated node used to keep the exported script smoke fast and model-free."
        }
    )
    connections = @()
    version = "1.0"
}

$saveResponse = Invoke-JsonPost -Url "$baseUrl/platform/workflows/templates" -Payload $payload
Assert-ApiResponse -Response $saveResponse -StepName "save skill export workflow template"

$exportResponse = Invoke-JsonPost -Url "$baseUrl/platform/workflows/templates/$TemplateKey/export-skill"
Assert-ApiResponse -Response $exportResponse -StepName "export workflow skill"

$exportData = $exportResponse.data
$skillDir = Resolve-SkillPath -SkillPath $exportData.skillPath
$skillMarkdownPath = Join-Path $skillDir "SKILL.md"
$templateJsonPath = Join-Path (Join-Path $skillDir "references") "workflow-template.json"
$runScriptPath = Join-Path (Join-Path $skillDir "scripts") "run_workflow.py"

Assert-FileExists -Path $skillMarkdownPath -Label "SKILL.md"
Assert-FileExists -Path $templateJsonPath -Label "workflow-template.json"
Assert-FileExists -Path $runScriptPath -Label "run_workflow.py"

$skillMarkdown = Get-Content $skillMarkdownPath -Raw
$templateJson = Get-Content $templateJsonPath -Raw | ConvertFrom-Json
$runScript = Get-Content $runScriptPath -Raw

$frontmatterMatch = [regex]::Match($skillMarkdown, "(?s)^---\s*\r?\n(?<frontmatter>.*?)\r?\n---")
if (-not $frontmatterMatch.Success) {
    throw "SKILL.md frontmatter missing"
}

$frontmatterLines = @(
    $frontmatterMatch.Groups["frontmatter"].Value -split "\r?\n" |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)
$frontmatterKeys = @($frontmatterLines | ForEach-Object { ($_ -split ":", 2)[0].Trim() })
$unexpectedKeys = @($frontmatterKeys | Where-Object { $_ -notin @("name", "description") })

if (($frontmatterKeys -notcontains "name") -or ($frontmatterKeys -notcontains "description") -or $unexpectedKeys.Count -gt 0) {
    throw "SKILL.md frontmatter must contain only name and description. Actual keys: $($frontmatterKeys -join ', ')"
}

Assert-TextContains -Text $runScript -Pattern "/execute-langgraph" -Label "run_workflow.py"
Assert-TextContains -Text $runScript -Pattern "http://127.0.0.1:8088/api" -Label "run_workflow.py"

if ($runScript -match 'api_server|8001|/runs(\b|/)') {
    throw "run_workflow.py appears to bypass Java Gateway or call Python Agent directly"
}

$expectedFiles = @("SKILL.md", "references/workflow-template.json", "scripts/run_workflow.py")
$actualFiles = @($exportData.files)
$missingFiles = @($expectedFiles | Where-Object { $_ -notin $actualFiles })
if ($missingFiles.Count -gt 0) {
    throw "Export response is missing file entries: $($missingFiles -join ', ')"
}

$scriptRunSummary = $null
if ($RunExportedScript) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
    }

    if (-not $pythonCommand) {
        throw "Cannot run exported skill script because no python command was found"
    }

    $rawScriptOutput = & $pythonCommand.Source $runScriptPath `
        --api-base $baseUrl `
        --requirement "Skill export smoke: run exported Dynamic LangGraph script"
    $scriptText = ($rawScriptOutput | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($scriptText)) {
        throw "Exported run_workflow.py returned empty output"
    }

    $scriptRunSummary = $scriptText | ConvertFrom-Json
    if (-not $scriptRunSummary.success) {
        throw "Exported run_workflow.py returned unsuccessful ApiResponse"
    }
}

$deleted = $false
if (-not $KeepTemplate) {
    $deleteResponse = Invoke-RestMethod -Method Delete -Uri "$baseUrl/platform/workflows/templates/$TemplateKey" -TimeoutSec 30
    Assert-ApiResponse -Response $deleteResponse -StepName "delete skill export workflow template"
    $deleted = $true
}

$success = $exportData.templateKey -eq $TemplateKey `
    -and -not [string]::IsNullOrWhiteSpace($exportData.skillName) `
    -and -not [string]::IsNullOrWhiteSpace($exportData.skillPath) `
    -and $false -eq [bool]$exportData.installed `
    -and $templateJson.workflowTemplateKey -eq $TemplateKey `
    -and ($frontmatterKeys -contains "name") `
    -and ($frontmatterKeys -contains "description") `
    -and $unexpectedKeys.Count -eq 0 `
    -and (Test-Path $skillMarkdownPath) `
    -and (Test-Path $templateJsonPath) `
    -and (Test-Path $runScriptPath)

if ($RunExportedScript) {
    $success = $success -and [bool]$scriptRunSummary.success
}

$summary = [ordered]@{
    success = $success
    templateKey = $TemplateKey
    skillName = $exportData.skillName
    skillPath = $exportData.skillPath
    resolvedSkillPath = $skillDir
    files = $actualFiles
    frontmatterKeys = $frontmatterKeys
    runScriptChecked = $true
    exportedScriptExecuted = [bool]$RunExportedScript
    exportedScriptStatus = if ($scriptRunSummary) { $scriptRunSummary.data.status } else { "" }
    installed = [bool]$exportData.installed
    warnings = @($exportData.warnings)
    templateDeleted = $deleted
}

$summary | ConvertTo-Json -Depth 30

if (-not $success) {
    throw "Workflow Skill Export smoke test failed"
}
