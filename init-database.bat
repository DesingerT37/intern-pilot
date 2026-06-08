@echo off
chcp 65001 >nul
echo ========================================
echo InternPilot 数据库初始化
echo ========================================
echo.

echo 请选择数据库类型:
echo 1. SQLite (推荐用于开发/MVP)
echo 2. PostgreSQL (推荐用于生产)
echo.
set /p choice="请输入选择 (1 或 2): "

if "%choice%"=="1" goto sqlite
if "%choice%"=="2" goto postgresql
echo ❌ 无效选择
pause
exit /b 1

:sqlite
echo.
echo ========================================
echo 初始化 SQLite 数据库
echo ========================================
echo.

cd intern-pilot-api

echo [1/2] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到 Python
    pause
    exit /b 1
)

echo ✅ Python 环境正常
echo.

echo [2/2] 初始化数据库...
python database\init_sqlite.py

if errorlevel 1 (
    echo.
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ SQLite 数据库初始化完成！
echo ========================================
echo.
echo 数据库文件: internpilot.db
echo.
echo 下一步:
echo 1. 编辑 .env 文件，设置 DATABASE_TYPE=sqlite
echo 2. 运行 start-backend.bat 启动后端服务
echo.
pause
exit /b 0

:postgresql
echo.
echo ========================================
echo 初始化 PostgreSQL 数据库
echo ========================================
echo.

echo 请确保已完成以下步骤:
echo 1. 安装 PostgreSQL
echo 2. 创建数据库: CREATE DATABASE internpilot;
echo 3. 配置 .env 文件中的数据库连接信息
echo.
set /p confirm="是否已完成上述步骤？(yes/no): "

if not "%confirm%"=="yes" (
    echo.
    echo 请先完成准备工作，然后重新运行此脚本
    echo.
    echo 参考文档: intern-pilot-api\database\README.md
    pause
    exit /b 1
)

echo.
echo [1/2] 检查 psql 命令...
psql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到 psql 命令
    echo 请确保 PostgreSQL 已正确安装并添加到 PATH
    pause
    exit /b 1
)

echo ✅ PostgreSQL 环境正常
echo.

echo [2/2] 执行 SQL 脚本...
echo 请输入 PostgreSQL 连接信息:
set /p pg_user="用户名 (默认: postgres): "
if "%pg_user%"=="" set pg_user=postgres

set /p pg_db="数据库名 (默认: internpilot): "
if "%pg_db%"=="" set pg_db=internpilot

cd intern-pilot-api
psql -U %pg_user% -d %pg_db% -f database\init_postgresql.sql

if errorlevel 1 (
    echo.
    echo ❌ 数据库初始化失败
    echo 请检查数据库连接信息是否正确
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ PostgreSQL 数据库初始化完成！
echo ========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件，设置 DATABASE_TYPE=postgresql
echo 2. 配置 PostgreSQL 连接信息
echo 3. 运行 start-backend.bat 启动后端服务
echo.
pause
exit /b 0
