-- 数据库迁移脚本：删除 crawl_tasks 表中未使用的字段
-- 执行前请备份数据库！

-- 1. 删除 experience 字段（如果存在）
ALTER TABLE crawl_tasks DROP COLUMN IF EXISTS experience;

-- 2. 删除 education 字段（如果存在）
ALTER TABLE crawl_tasks DROP COLUMN IF EXISTS education;

-- 3. 删除 error_message 字段（如果存在）
ALTER TABLE crawl_tasks DROP COLUMN IF EXISTS error_message;

-- 4. 验证修改
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'crawl_tasks'
ORDER BY ordinal_position;

-- 预期结果应该包含以下字段：
-- id, task_id, user_id, keyword, city, max_pages, status, progress, 
-- total_jobs, crawled_jobs, started_at, completed_at, created_at
