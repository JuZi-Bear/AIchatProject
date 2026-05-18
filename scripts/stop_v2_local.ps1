param(
    [switch]$ForcePorts
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $ProjectRoot "output"
$PidFile = Join-Path $OutputDir "local_v2_pids.json"
$KnownPorts = @(8001, 8088, 5174, 3307)

Write-Host "== AIchatProject v2 local stop =="

$hadPidFile = Test-Path $PidFile

if ($hadPidFile) {
    $rawItems = Get-Content -Path $PidFile -Raw | ConvertFrom-Json
    if ($rawItems -is [array]) {
        $items = $rawItems
    } else {
        $items = @($rawItems)
    }

    foreach ($item in $items) {
        if (-not $item.pid) {
            continue
        }

        $process = Get-Process -Id ([int]$item.pid) -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            Write-Host "[stop] $($item.name) pid=$($process.Id)"
        }
    }

    Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "[info] no PID file found: $PidFile"
}

if ($ForcePorts -or $hadPidFile) {
    $listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -in $KnownPorts }

    foreach ($listener in $listeners) {
        Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
        Write-Host "[port-stop] port=$($listener.LocalPort) pid=$($listener.OwningProcess)"
    }
}

$remaining = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in $KnownPorts } |
    Select-Object LocalPort, OwningProcess |
    Sort-Object LocalPort

if ($remaining) {
    Write-Host "[info] remaining listeners:"
    $remaining | Format-Table | Out-String | Write-Host
} else {
    Write-Host "[ok] no v2 local listeners remain on known ports"
}
