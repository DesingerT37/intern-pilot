@echo off
chcp 65001 >nul
echo ========================================
echo InternPilot 前端依赖安装
echo ========================================
echo.

cd intern-pilot-web

echo [1/2] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到 Node.js
    echo 请先安装 Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js 版本:
node --version
echo.

echo [2/2] 安装依赖包...
call npm install

if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 前端依赖安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 运行 start-frontend.bat 启动前端开发服务器
echo 2. 访问 http://localhost:5173
echo.
pause
