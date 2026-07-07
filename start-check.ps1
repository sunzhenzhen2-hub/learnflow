# LearnFlow 启动脚本 - 自动检查后端可用性

param(
    [string]$BackendPort = "8001",
    [string]$FrontendPort = "5173"
)

Write-Host "=== LearnFlow 启动检查 ===" -ForegroundColor Cyan

# 1. 检查后端
Write-Host "`n[1/2] 检查后端 (端口 $BackendPort)..." -NoNewline
$backendRunning = $false
try {
    $resp = Invoke-WebRequest "http://localhost:$BackendPort/api/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($resp.StatusCode -eq 200) {
        Write-Host " OK" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host " 未运行" -ForegroundColor Red
}

# 2. 检查/启动前端
Write-Host "`n[2/2] 启动前端 (端口 $FrontendPort)..." -NoNewline
$existing = Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host " 已在运行 (PID $($existing[0].OwningProcess))" -ForegroundColor Yellow
} else {
    if ($backendRunning) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "`n前端: http://localhost:$FrontendPort"
        Write-Host "后端: http://localhost:$BackendPort"
        Write-Host "`n全部就绪！" -ForegroundColor Green
    } else {
        Write-Host "`n后端未就绪，请先启动后端: cd backend; python -m uvicorn app.main:app --reload --port $BackendPort" -ForegroundColor Red
    }
}
