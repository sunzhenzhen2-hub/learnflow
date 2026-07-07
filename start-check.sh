#!/bin/bash
# LearnFlow 状态检查 (Mac / Linux)
# 用法: ./start-check.sh

BACKEND_PORT=${BACKEND_PORT:-8001}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

echo "=== LearnFlow 状态检查 ==="

# 检查后端
if curl -sf "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
    echo "[后端] OK (端口 $BACKEND_PORT)"
else
    echo "[后端] 未运行 (端口 $BACKEND_PORT)"
fi

# 检查前端
if lsof -i ":$FRONTEND_PORT" > /dev/null 2>&1; then
    echo "[前端] OK (端口 $FRONTEND_PORT)"
else
    echo "[前端] 未运行 (端口 $FRONTEND_PORT)"
fi

# 端口占用情况
echo ""
echo "端口占用:"
lsof -i ":$BACKEND_PORT" 2>/dev/null | grep LISTEN | awk '{print "  后端 " $9}'
lsof -i ":$FRONTEND_PORT" 2>/dev/null | grep LISTEN | awk '{print "  前端 " $9}'
