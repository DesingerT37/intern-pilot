-- 数据库迁移脚本：删除 boss_jobs 表中未使用的字段
-- 执行前请备份数据库！

-- 1. 删除 company_info 字段（如果存在）
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS company_info;

-- 2. 删除 job_url 字段（如果存在）
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS job_url;

-- 3. 验证修改
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'boss_jobs'
ORDER BY ordinal_position;

-- 预期结果应该包含以下字段：
-- id, job_id, job_name, company_name, salary, location, experience, education,
-- job_description, welfare_tags, task_id, crawled_at, created_at
