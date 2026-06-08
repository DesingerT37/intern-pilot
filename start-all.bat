@echo off
chcp 65001 >nul
echo ========================================
echo InternPilot 一键启动
echo ========================================
echo.

echo 正在启动后端和前端服务...
echo.

echo [1/2] 启动后端服务 (端口 8000)...
start "InternPilot Backend" cmd /k "start-backend.bat"
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务 (端口 5173)...
start "InternPilot Frontend" cmd /k "start-frontend.bat"

echo.
echo ========================================
echo ✅ 服务启动中...
echo ========================================
echo.
echo 📱 前端地址: http://localhost:5173
echo 🔗 后端地址: http://localhost:8000
echo 📚 API 文档: http://localhost:8000/docs
echo.
echo 提示: 
echo - 两个服务会在新窗口中启动
echo - 等待几秒后访问前端地址
echo - 关闭窗口即可停止服务
echo.
pause
