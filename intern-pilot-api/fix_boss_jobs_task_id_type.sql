-- 修复 boss_jobs.task_id 字段类型
-- 执行前请备份数据库！
-- 注意：此脚本会清空 boss_jobs 表的所有数据！

-- 0. 先清空表（因为旧数据的 task_id 是错的）
TRUNCATE TABLE boss_jobs CASCADE;

-- 1. 删除外键约束（如果存在）
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_task_id_fkey;

-- 2. 删除旧的 task_id 列（如果是从 user_id 改名来的，类型不对）
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS task_id;

-- 3. 添加新的 task_id 列（UUID 类型）
ALTER TABLE boss_jobs 
ADD COLUMN task_id UUID NOT NULL;

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS ix_boss_jobs_task_id ON boss_jobs(task_id);

-- 5. 添加外键约束
ALTER TABLE boss_jobs 
ADD CONSTRAINT boss_jobs_task_id_fkey 
FOREIGN KEY (task_id) 
REFERENCES crawl_tasks(task_id) 
ON DELETE CASCADE;

-- 6. 验证字段类型
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'boss_jobs' AND column_name = 'task_id';

-- 7. 检查表是否为空
SELECT COUNT(*) as job_count FROM boss_jobs;

-- 预期结果：
-- column_name | data_type | is_nullable | column_default
-- task_id     | uuid      | NO          | NULL
-- job_count = 0（表已清空，需要重新爬取数据）
