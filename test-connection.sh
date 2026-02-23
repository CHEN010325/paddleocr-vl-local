#!/bin/bash

# PandOCR 连接测试脚本

echo "🔍 测试 PandOCR 服务连接..."
echo ""

# 测试前端服务
echo "1️⃣  测试前端服务 (localhost:8000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; then
    echo "   ✅ 前端服务正常"
else
    echo "   ❌ 前端服务异常"
fi

# 测试 PaddleOCR API
echo "2️⃣  测试 PaddleOCR API (localhost:8081)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health | grep -q "200"; then
    echo "   ✅ PaddleOCR API 正常"
else
    echo "   ❌ PaddleOCR API 异常（可能正在启动中...）"
fi

# 测试网络连接
echo "3️⃣  测试 Docker 内部网络..."
if docker compose exec -T pandocr-web curl -s -o /dev/null -w "%{http_code}" http://paddleocr-vl-api:8080/health | grep -q "200"; then
    echo "   ✅ 内部网络正常"
else
    echo "   ⚠️  内部网络可能未就绪"
fi

# 测试 GPU 可用性
echo "4️⃣  测试 GPU 可用性..."
if docker compose exec -T paddleocr-vlm-server nvidia-smi &> /dev/null; then
    echo "   ✅ GPU 可用"
else
    echo "   ❌ GPU 不可用"
fi

echo ""
echo "📊 服务状态总览:"
docker compose ps

echo ""
echo "💡 提示:"
echo "   - 如果服务异常，查看日志: docker compose logs -f"
echo "   - 如果正在启动中，等待 3-5 分钟后重试"

