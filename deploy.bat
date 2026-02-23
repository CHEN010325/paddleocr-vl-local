@echo off
REM PandOCR Docker 部署脚本 (Windows)

echo 🚀 部署 PandOCR 应用...

REM 检查环境变量文件
if not exist "env.txt" (
    echo ❌ env.txt 不存在，请先创建配置文件
    pause
    exit /b 1
)

REM 停止旧容器（如果存在）
docker ps -q -f name=pandocr-web >nul 2>&1
if not errorlevel 1 (
    echo 🛑 停止旧容器...
    docker compose down
)

REM 启动所有服务
echo ▶️  启动服务...
docker compose --env-file env.txt up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo.
echo 📊 服务状态:
docker compose ps

REM 健康检查
echo.
echo 🏥 健康检查:

REM 检查前端服务
curl -f http://localhost:8000/ >nul 2>&1
if not errorlevel 1 (
    echo ✅ 前端服务 ^(8000^) - 正常
) else (
    echo ❌ 前端服务 ^(8000^) - 异常
)

REM 检查 PaddleOCR API
curl -f http://localhost:8081/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ PaddleOCR API ^(8081^) - 正常
) else (
    echo ⏳ PaddleOCR API ^(8081^) - 启动中...
)

echo.
echo 🎉 部署完成！
echo.
echo 📍 访问地址:
echo   前端界面: http://localhost:8000
echo   API 地址: http://localhost:8081
echo.
echo 📋 常用命令:
echo   查看日志: docker compose logs -f
echo   查看前端日志: docker compose logs -f pandocr-web
echo   重启服务: docker compose restart
echo   停止服务: docker compose down
echo.
pause

