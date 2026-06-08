@echo off
chcp 65001 >nul
echo ======================================================================
echo 检查常用调试端口占用情况
echo ======================================================================
echo.

echo 检查端口 9222...
netstat -ano | findstr :9222 >nul
if %errorlevel% equ 0 (
    echo ✗ 端口 9222 被占用：
    netstat -ano | findstr :9222
) else (
    echo ✓ 端口 9222 空闲
)

echo.
echo 检查端口 9600...
netstat -ano | findstr :9600 >nul
if %errorlevel% equ 0 (
    echo ✗ 端口 9600 被占用：
    netstat -ano | findstr :9600
) else (
    echo ✓ 端口 9600 空闲
)

echo.
echo 检查端口 9601...
netstat -ano | findstr :9601 >nul
if %errorlevel% equ 0 (
    echo ✗ 端口 9601 被占用：
    netstat -ano | findstr :9601
) else (
    echo ✓ 端口 9601 空闲
)

echo.
echo ======================================================================
echo 提示：如果端口被占用，可以运行 kill_browser.bat 关闭浏览器
echo ======================================================================
echo.

pause
