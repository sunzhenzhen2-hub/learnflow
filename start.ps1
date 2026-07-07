# LearnFlow 一键启动
param(
    [string]$BackendPort = "8001",
    [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Stop"
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Status {
    param($msg, $color = "White")
    Write-Host "[LearnFlow]" $msg -ForegroundColor $color
}

# 1. 启动后端
Write-Status "启动后端 (端口 $BackendPort)..." -Color Cyan
$backendRunning = $false
try {
    $check = Invoke-WebRequest "http://localhost:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($check.StatusCode -eq 200) {
        Write-Status "后端已在运行" -Color Yellow
        $backendRunning = $true
    }
} catch {
    $backendRunning = $false
}

if (-not $backendRunning) {
    $backendJob = Start-Job -ScriptBlock {
        param($bd, $bp, $fe)
        cd $bd
        $env:PYTHONPATH = $bd
        python -m uvicorn app.main:app --reload --port $bp --host 0.0.0.0
    } -ArgumentList "$BASE/backend", $BackendPort, $FrontendPort
    Write-Status "后端 PID: $($backendJob.Id)" -Color Yellow
    
    # 等待后端就绪
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep 2
        try {
            $check = Invoke-WebRequest "http://localhost:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($check.StatusCode -eq 200) {
                Write-Status "后端就绪" -Color Green
                break
            }
        } catch { }
        if ($i -eq 14) {
            Write-Status "后端启动超时，请检查错误" -Color Red
            exit 1
        }
    }
}

# 2. 启动前端
Write-Status "启动前端 (端口 $FrontendPort)..." -Color Cyan
$existing = Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Job -ScriptBlock {
        cd 'C:\Users\Administrator\.qoderworkcn\workspace\mr7kcg38ce4xu7wf\learnflow\frontend'
        npx vite --host --port 5173
    } | Out-Null
    Start-Sleep 5
} else {
    Write-Status "前端已在运行" -Color Yellow
}

# 3. 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "  后端: http://localhost:$BackendPort" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
