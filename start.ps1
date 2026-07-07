# LearnFlow 一键启动 (Windows)
param(
    [string]$BackendPort = "8001",
    [string]$FrontendPort = "5173"
)

$ErrorActionPreference = "Continue"
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path

function Test-Port {
    param($port)
    try {
        $null = (Invoke-WebRequest "http://localhost:$port/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue)
        return $true
    } catch { return $false }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LearnFlow 启动" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

# 1. 启动后端
Write-Host ""
Write-Host "[1/2] 后端 (端口 $BackendPort)..." -NoNewline
if (Test-Port $BackendPort) {
    Write-Host " 已在运行" -ForegroundColor Yellow
} else {
    Write-Host " 启动中..." -NoNewline
    $backendPath = Join-Path $BASE "backend"
    Start-Process powershell -ArgumentList "-NoExit", "cd '$backendPath'; python -m uvicorn app.main:app --reload --port $BackendPort --host 0.0.0.0" -WindowStyle Minimized
    
    # 等待就绪
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep 2
        if (Test-Port $BackendPort) {
            Write-Host " 就绪" -ForegroundColor Green
            break
        }
        if ($i -eq 14) {
            Write-Host " 超时" -ForegroundColor Red
        }
    }
}

# 2. 启动前端
Write-Host "[2/2] 前端 (端口 $FrontendPort)..." -NoNewline
$existing = Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host " 已在运行" -ForegroundColor Yellow
} else {
    Write-Host " 启动中..." -NoNewline
    $frontendPath = Join-Path $BASE "frontend"
    Start-Process powershell -ArgumentList "-NoExit", "cd '$frontendPath'; npx vite --host --port $FrontendPort" -WindowStyle Minimized
    Start-Sleep 5
    $check = Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host " 就绪" -ForegroundColor Green
    } else {
        Write-Host " 启动失败，请手动检查" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "  后端: http://localhost:$BackendPort" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
