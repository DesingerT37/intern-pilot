@echo off
echo ========================================
echo 安装爬虫依赖
echo ========================================
echo.

echo 正在安装 DrissionPage...
pip install DrissionPage

echo.
echo 正在安装 beautifulsoup4...
pip install beautifulsoup4

echo.
echo 正在安装 openpyxl (可选，用于 Excel 导出)...
pip install openpyxl

echo.
echo 正在安装 pandas (可选，用于 Excel 导出)...
pip install pandas

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 验证安装:
python -c "import DrissionPage; print('DrissionPage:', DrissionPage.__version__)"
python -c "import bs4; print('beautifulsoup4: OK')"

echo.
echo 按任意键退出...
pause >nul
