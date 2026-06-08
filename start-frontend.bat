@echo off
chcp 65001 >nul
echo ========================================
echo InternPilot 前端开发服务器
echo ========================================
echo.

cd intern-pilot-web

echo [1/2] 检查依赖...
if not exist "node_modules" (
    echo ❌ 未检测到 node_modules 目录
    echo 请先运行 install-frontend.bat 安装依赖
    pause
    exit /b 1
)

echo ✅ 依赖检查通过
echo.

echo [2/2] 启动 Vite 开发服务器...
echo.
echo 📱 前端地址: http://localhost:5173
echo 🔗 后端地址: http://localhost:8000
echo.
echo 提示: 请确保后端服务已启动 (运行 start-backend.bat)
echo.
echo ----------------------------------------
echo.

npm run dev
