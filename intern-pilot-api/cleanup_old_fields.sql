-- 清理旧字段脚本
-- 删除不再使用的字段

-- 1. 删除 boss_jobs 表中的旧字段 crawl_task_id（如果存在）
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS crawl_task_id;

-- 2. 验证 boss_jobs 表结构
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'boss_jobs'
ORDER BY ordinal_position;

-- 预期结果应该只包含：
-- id, job_id, task_id, job_name, company_name, salary, location, 
-- experience, education, job_description, welfare_tags, crawled_at, created_at
-- 
-- 不应该有：crawl_task_id, user_id, company_info, job_url
