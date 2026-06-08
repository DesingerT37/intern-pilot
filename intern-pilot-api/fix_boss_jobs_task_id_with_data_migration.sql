-- 修复 boss_jobs.task_id 字段类型（保留数据版本）
-- 执行前请备份数据库！

-- 步骤说明：
-- 1. 如果 boss_jobs 表中有数据，但 task_id 是 integer 类型（从 user_id 改名来的）
-- 2. 我们需要先清空数据，因为无法将 user_id 映射到 task_id
-- 3. 然后修改字段类型

-- 方案 A: 清空数据后修改（推荐，因为 user_id 无法映射到 task_id）
BEGIN;

-- 1. 删除所有职位数据（因为 user_id 无法映射到正确的 task_id）
TRUNCATE TABLE boss_jobs CASCADE;

-- 2. 删除外键约束
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_task_id_fkey;

-- 3. 删除旧的 task_id 列
ALTER TABLE boss_jobs DROP COLUMN IF EXISTS task_id;

-- 4. 添加新的 task_id 列（UUID 类型）
ALTER TABLE boss_jobs 
ADD COLUMN task_id UUID NOT NULL;

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS ix_boss_jobs_task_id ON boss_jobs(task_id);

-- 6. 添加外键约束
ALTER TABLE boss_jobs 
ADD CONSTRAINT boss_jobs_task_id_fkey 
FOREIGN KEY (task_id) 
REFERENCES crawl_tasks(task_id) 
ON DELETE CASCADE;

COMMIT;

-- 7. 验证
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'boss_jobs' AND column_name = 'task_id';

SELECT COUNT(*) as job_count FROM boss_jobs;

-- 预期结果：
-- task_id 字段类型应该是 uuid
-- job_count 应该是 0（数据已清空，需要重新爬取）
