param(
    [ValidateSet("java", "python")]
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

    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $ProjectRoot "output"
$PidFile = Join-Path $OutputDir "local_v2_pids.json"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { "python" }
$Launched = @()

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Test-TcpPort {
    param([int]$Port)

    $listener = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $Port } |
        Select-Object -First 1

    return $null -ne $listener
}

function Wait-TcpPort {
    param(
        [int]$Port,
        [string]$Name,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-TcpPort -Port $Port) {
            Write-Host "[ok] $Name is listening on port $Port"
            return
        }
        Start-Sleep -Seconds 1
    }

    throw "$Name did not listen on port $Port within $TimeoutSeconds seconds"
}

function Wait-Http {
    param(
        [string]$Url,
        [string]$Name,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-RestMethod -Uri $Url -TimeoutSec 5 | Out-Null
            Write-Host "[ok] $Name health check passed: $Url"
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    throw "$Name health check failed: $Url"
}

function Start-LoggedProcess {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WorkingDirectory
    )

    $safeName = $Name.Replace(" ", "_").ToLowerInvariant()
    $stdout = Join-Path $OutputDir "local_$safeName.out.log"
    $stderr = Join-Path $OutputDir "local_$safeName.err.log"
    $process = Start-Process `
        -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru `
        -WindowStyle Hidden

    $script:Launched += [ordered]@{
        name = $Name
        pid = $process.Id
        stdout = $stdout
        stderr = $stderr
    }

    Write-Host "[start] $Name pid=$($process.Id)"
    return $process
}

function Invoke-MySql {
    param(
        [int]$Port,
        [string]$User,
        [string]$Password,
        [string]$Sql
    )

    $args = @(
        "--connect-timeout=5",
        "--host=127.0.0.1",
        "--port=$Port",
        "--user=$User"
    )

    if ([string]::IsNullOrEmpty($Password)) {
        $args += "--skip-password"
    } else {
        $args += "--password=$Password"
    }

    $args += @("-e", $Sql)
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        & mysql @args *>$null
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    return $exitCode -eq 0
}

function Start-TempMySql {
    if (-not (Get-Command mysqld -ErrorAction SilentlyContinue)) {
        throw "mysqld not found. Install MySQL locally, start Docker, or run with -MySqlMode existing."
    }

    if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
        throw "mysql client not found. Install MySQL client or run with -MySqlMode existing."
    }

    $dataDir = Join-Path $OutputDir "mysql-local-data"
    $logDir = Join-Path $OutputDir "mysql-local-logs"
    New-Item -ItemType Directory -Force -Path $dataDir, $logDir | Out-Null

    if (-not (Test-Path (Join-Path $dataDir "auto.cnf"))) {
        $initLog = Join-Path $logDir "initialize.log"
        Write-Host "[mysql] initializing temporary data directory: $dataDir"
        & mysqld --initialize-insecure --datadir="$dataDir" --console *>$initLog
    }

    if (-not (Test-TcpPort -Port $TempMySqlPort)) {
        Start-LoggedProcess `
            -Name "mysql-temp" `
            -FilePath "mysqld" `
            -ArgumentList @(
                "--datadir=$dataDir",
                "--port=$TempMySqlPort",
                "--bind-address=127.0.0.1",
                "--skip-log-bin",
                "--mysqlx=0"
            ) `
            -WorkingDirectory $ProjectRoot | Out-Null
    }

    Wait-TcpPort -Port $TempMySqlPort -Name "temporary MySQL" -TimeoutSeconds 60

    if (-not (Invoke-MySql -Port $TempMySqlPort -User $MySqlUser -Password $MySqlPassword -Sql "SELECT 1;")) {
        $escapedPassword = $MySqlPassword.Replace("'", "''")
        Invoke-MySql `
            -Port $TempMySqlPort `
            -User $MySqlUser `
            -Password "" `
            -Sql "ALTER USER 'root'@'localhost' IDENTIFIED BY '$escapedPassword'; FLUSH PRIVILEGES;" | Out-Null
    }

    if (-not (Invoke-MySql -Port $TempMySqlPort -User $MySqlUser -Password $MySqlPassword -Sql "CREATE DATABASE IF NOT EXISTS aichat_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")) {
        throw "failed to prepare temporary MySQL database on port $TempMySqlPort"
    }

    return "jdbc:mysql://127.0.0.1:$TempMySqlPort/aichat_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true"
}

Write-Host "== AIchatProject v2 local startup =="
Write-Host "Project root: $ProjectRoot"
Write-Host "API mode: $ApiMode"
Write-Host "Python executable: $PythonExe"

if (-not (Test-TcpPort -Port $PythonPort)) {
    Start-LoggedProcess `
        -Name "python-api" `
        -FilePath $PythonExe `
        -ArgumentList @("-m", "uvicorn", "api_server:app", "--host", "127.0.0.1", "--port", "$PythonPort") `
        -WorkingDirectory $ProjectRoot | Out-Null
}
Wait-Http -Url "http://127.0.0.1:$PythonPort/health" -Name "Python API" -TimeoutSeconds 60

if ($ApiMode -eq "java") {
    if ($MySqlMode -eq "temp") {
        $datasourceUrl = Start-TempMySql
    } else {
        $datasourceUrl = "jdbc:mysql://127.0.0.1:$MySqlPort/aichat_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true"
    }

    $env:SPRING_PROFILES_ACTIVE = "local"
    $env:SPRING_DATASOURCE_URL = $datasourceUrl
    $env:SPRING_DATASOURCE_USERNAME = $MySqlUser
    $env:SPRING_DATASOURCE_PASSWORD = $MySqlPassword
    $env:AGENT_ENGINE_BASE_URL = "http://127.0.0.1:$PythonPort"

    if (-not (Test-TcpPort -Port $JavaPort)) {
        Start-LoggedProcess `
            -Name "backend-java" `
            -FilePath "mvn.cmd" `
            -ArgumentList @("spring-boot:run", "-Dspring-boot.run.profiles=local") `
            -WorkingDirectory (Join-Path $ProjectRoot "backend-java") | Out-Null
    }
    Wait-Http -Url "http://127.0.0.1:$JavaPort/api/health" -Name "Java Gateway" -TimeoutSeconds 90
}

$env:VITE_API_MODE = $ApiMode
$env:VITE_PYTHON_API_BASE_URL = "http://127.0.0.1:$PythonPort"
$env:VITE_JAVA_API_BASE_URL = "http://127.0.0.1:$JavaPort/api"

if (-not (Test-TcpPort -Port $VuePort)) {
    Start-LoggedProcess `
        -Name "frontend-vue" `
        -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "$VuePort") `
        -WorkingDirectory (Join-Path $ProjectRoot "frontend-vue") | Out-Null
}
Wait-TcpPort -Port $VuePort -Name "Vue dev server" -TimeoutSeconds 60

$Launched | ConvertTo-Json -Depth 5 | Set-Content -Path $PidFile -Encoding UTF8

Write-Host ""
Write-Host "== URLs =="
Write-Host "FastAPI Docs: http://127.0.0.1:$PythonPort/docs"
Write-Host "Java Health:  http://127.0.0.1:$JavaPort/api/health"
Write-Host "Vue RunConsole: http://127.0.0.1:$VuePort/runs/new"
Write-Host "PID file: $PidFile"

if (-not $SkipSmoke) {
    Write-Host ""
    Write-Host "== CodeAgent smoke =="
    & (Join-Path $PSScriptRoot "smoke_codeagent.ps1") `
        -ApiMode $ApiMode `
        -JavaApiBaseUrl "http://127.0.0.1:$JavaPort/api" `
        -PythonApiBaseUrl "http://127.0.0.1:$PythonPort"
}
