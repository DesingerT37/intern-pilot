-- 数据库迁移脚本：修改 boss_jobs 表结构
-- 执行前请备份数据库！

-- 1. 移除 job_id 的唯一约束
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_job_id_key;

-- 2. 移除 user_id 列（如果存在）
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS user_id;

-- 3. 如果列名是 crawl_task_id，重命名为 task_id
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'boss_jobs' AND column_name = 'crawl_task_id'
    ) THEN
        ALTER TABLE boss_jobs RENAME COLUMN crawl_task_id TO task_id;
    END IF;
END $$;

-- 4. 修改 task_id 为 NOT NULL
ALTER TABLE boss_jobs ALTER COLUMN task_id SET NOT NULL;

-- 5. 删除旧的外键约束
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_crawl_task_id_fkey;
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_task_id_fkey;

-- 6. 添加新的外键约束（CASCADE 删除）
ALTER TABLE boss_jobs 
ADD CONSTRAINT boss_jobs_task_id_fkey 
FOREIGN KEY (task_id) 
REFERENCES crawl_tasks(task_id) 
ON DELETE CASCADE;

-- 7. 验证修改
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'boss_jobs'
ORDER BY ordinal_position;

-- 8. 检查约束
SELECT 
    conname AS constraint_name,
    contype AS constraint_type
FROM pg_constraint 
WHERE conrelid = 'boss_jobs'::regclass;
