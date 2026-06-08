@echo off
chcp 65001 >nul
echo ======================================================================
echo 关闭所有浏览器进程
echo ======================================================================
echo.

echo 正在关闭 Edge 浏览器...
taskkill /F /IM msedge.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Edge 浏览器已关闭
) else (
    echo ℹ 没有发现 Edge 浏览器进程
)

echo.
echo 正在关闭 Chrome 浏览器...
taskkill /F /IM chrome.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Chrome 浏览器已关闭
) else (
    echo ℹ 没有发现 Chrome 浏览器进程
)

echo.
echo ======================================================================
echo 完成！所有浏览器进程已关闭
echo ======================================================================
echo.

pause
