-- ============================================
-- PostgreSQL 创建数据库脚本
-- 适用于 Windows/Linux/macOS
-- ============================================

-- 方式一: Windows 系统（推荐）
-- 使用 C locale 避免编码问题
CREATE DATABASE internpilot
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 方式二: Linux/macOS 系统
-- 如果上面的命令失败，使用这个
-- CREATE DATABASE internpilot
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.UTF-8'
--     LC_CTYPE = 'en_US.UTF-8'
--     TEMPLATE = template0
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- 方式三: 最简化版本（通用）
-- 如果上面都失败，使用这个
-- CREATE DATABASE internpilot
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     TEMPLATE = template0;

-- ============================================
-- 使用说明
-- ============================================
-- 1. 以 postgres 用户登录
--    psql -U postgres
--
-- 2. 执行此脚本
--    \i database/create_database.sql
--
-- 3. 连接到新数据库
--    \c internpilot
--
-- 4. 执行表结构初始化
--    \i database/init_postgresql.sql
-- ============================================
