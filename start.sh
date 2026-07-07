#!/bin/bash
# LearnFlow 一键启动 (Mac / Linux)
# 用法: ./start.sh

BACKEND_PORT=${BACKEND_PORT:-8001}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

echo "=== LearnFlow 启动检查 ==="

# 检查后端
if curl -sf "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
    echo "[后端] 已在运行 (端口 $BACKEND_PORT)"
else
    echo "[后端] 启动中 (端口 $BACKEND_PORT)..."
    cd "$(dirname "$0")/backend"
    export PYTHONPATH="$(dirname "$0")/backend"
    nohup python -m uvicorn app.main:app --reload --port $BACKEND_PORT --host 0.0.0.0 > /tmp/learnflow-backend.log 2>&1 &
    BACKEND_PID=$!

    # 等待后端就绪
    for i in {1..15}; do
        sleep 2
        if curl -sf "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
            echo "[后端] 就绪 (PID $BACKEND_PID)"
            break
        fi
        if [ $i -eq 15 ]; then
            echo "[后端] 启动超时，请检查 /tmp/learnflow-backend.log"
            exit 1
        fi
    done
fi

# 检查前端
if lsof -i ":$FRONTEND_PORT" > /dev/null 2>&1; then
    echo "[前端] 已在运行 (端口 $FRONTEND_PORT)"
else
    echo "[前端] 启动中 (端口 $FRONTEND_PORT)..."
    cd "$(dirname "$0")/frontend"
    nohup npx vite --host --port $FRONTEND_PORT > /tmp/learnflow-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "[前端] 就绪 (PID $FRONTEND_PID)"
fi

echo ""
echo "========================================"
echo "  前端: http://localhost:$FRONTEND_PORT"
echo "  后端: http://localhost:$BACKEND_PORT"
echo "========================================"
