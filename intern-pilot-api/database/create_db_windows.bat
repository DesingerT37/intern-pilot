@echo off
chcp 65001 >nul
echo ========================================
echo PostgreSQL 数据库创建（Windows）
echo ========================================
echo.

echo 此脚本将创建 internpilot 数据库
echo.

set /p pg_user="请输入 PostgreSQL 用户名 (默认: postgres): "
if "%pg_user%"=="" set pg_user=postgres

echo.
echo 正在创建数据库...
echo.

psql -U %pg_user% -c "CREATE DATABASE internpilot WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TEMPLATE = template0;"

if errorlevel 1 (
    echo.
    echo ❌ 数据库创建失败
    echo.
    echo 可能的原因:
    echo 1. 数据库已存在
    echo 2. 用户名或密码错误
    echo 3. PostgreSQL 服务未启动
    echo.
    echo 如果数据库已存在，可以直接执行下一步
    pause
    exit /b 1
)

echo.
echo ✅ 数据库创建成功！
echo.
echo 下一步: 初始化表结构
echo 运行: psql -U %pg_user% -d internpilot -f init_postgresql.sql
echo.
pause
