#!/bin/bash

# PandOCR Docker 部署脚本

set -e

echo "🚀 部署 PandOCR 应用..."

# 检查环境变量文件
if [ ! -f "env.txt" ]; then
    echo "❌ env.txt 不存在，请先创建配置文件"
    exit 1
fi

# 停止旧容器（如果存在）
if [ "$(docker ps -q -f name=pandocr-web)" ]; then
    echo "🛑 停止旧容器..."
    docker compose down
fi

# 启动所有服务
echo "▶️  启动服务..."
docker compose --env-file env.txt up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker compose ps

# 健康检查
echo ""
echo "🏥 健康检查:"

# 检查前端服务
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ 前端服务 (8000) - 正常"
else
    echo "❌ 前端服务 (8000) - 异常"
fi

# 检查 PaddleOCR API
if curl -f http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ PaddleOCR API (8081) - 正常"
else
    echo "⏳ PaddleOCR API (8081) - 启动中..."
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "📍 访问地址:"
echo "  前端界面: http://localhost:8000"
echo "  API 地址: http://localhost:8081"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker compose logs -f"
echo "  查看前端日志: docker compose logs -f pandocr-web"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose down"

