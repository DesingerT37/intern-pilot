@echo off
chcp 65001 >nul
echo ======================================================================
echo 检查浏览器进程
echo ======================================================================
echo.

echo 正在查找 Edge 和 Chrome 进程...
echo.

tasklist | findstr /i "msedge chrome" >nul
if %errorlevel% equ 0 (
    echo 找到以下浏览器进程：
    echo.
    tasklist | findstr /i "msedge chrome"
    echo.
    echo ======================================================================
    echo 提示：如果需要关闭这些进程，请运行 kill_browser.bat
    echo ======================================================================
) else (
    echo ✓ 没有发现浏览器进程在运行
    echo.
)

echo.
pause
