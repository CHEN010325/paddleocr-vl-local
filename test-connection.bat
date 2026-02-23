@echo off
REM PandOCR 连接测试脚本 (Windows)

echo 🔍 测试 PandOCR 服务连接...
echo.

REM 测试前端服务
echo 1️⃣  测试前端服务 (localhost:8000)...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/ | findstr "200" >nul
if not errorlevel 1 (
    echo    ✅ 前端服务正常
) else (
    echo    ❌ 前端服务异常
)

REM 测试 PaddleOCR API
echo 2️⃣  测试 PaddleOCR API (localhost:8081)...
curl -s -o nul -w "%%{http_code}" http://localhost:8081/health | findstr "200" >nul
if not errorlevel 1 (
    echo    ✅ PaddleOCR API 正常
) else (
    echo    ❌ PaddleOCR API 异常（可能正在启动中...）
)

REM 测试网络连接
echo 3️⃣  测试 Docker 内部网络...
docker compose exec -T pandocr-web curl -s -o /dev/null -w "%%{http_code}" http://paddleocr-vl-api:8080/health 2>nul | findstr "200" >nul
if not errorlevel 1 (
    echo    ✅ 内部网络正常
) else (
    echo    ⚠️  内部网络可能未就绪
)

REM 测试 GPU 可用性
echo 4️⃣  测试 GPU 可用性...
docker compose exec -T paddleocr-vlm-server nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo    ✅ GPU 可用
) else (
    echo    ❌ GPU 不可用
)

echo.
echo 📊 服务状态总览:
docker compose ps

echo.
echo 💡 提示:
echo    - 如果服务异常，查看日志: docker compose logs -f
echo    - 如果正在启动中，等待 3-5 分钟后重试
echo.
pause

