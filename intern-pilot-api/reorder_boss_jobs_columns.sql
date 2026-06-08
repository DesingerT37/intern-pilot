-- 重新排列 boss_jobs 表的列顺序
-- 将 task_id 移到 job_id 后面
-- 执行前请备份数据库！

BEGIN;

-- 1. 删除所有约束和索引
ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_task_id_fkey;
DROP INDEX IF EXISTS ix_boss_jobs_task_id;
DROP INDEX IF EXISTS ix_boss_jobs_job_id;
DROP INDEX IF EXISTS ix_boss_jobs_created_at;

-- 2. 创建新表（按理想顺序排列列）
CREATE TABLE boss_jobs_new (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    task_id UUID NOT NULL,
    job_name VARCHAR(200) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    salary VARCHAR(100),
    location VARCHAR(200),
    experience VARCHAR(100),
    education VARCHAR(100),
    job_description TEXT,
    welfare_tags JSONB,
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 如果有数据，复制数据（当前表是空的，这步可以跳过）
-- INSERT INTO boss_jobs_new SELECT id, job_id, task_id, job_name, company_name, salary, location, experience, education, job_description, welfare_tags, crawled_at, created_at FROM boss_jobs;

-- 4. 删除旧表
DROP TABLE boss_jobs;

-- 5. 重命名新表
ALTER TABLE boss_jobs_new RENAME TO boss_jobs;

-- 6. 重新创建索引
CREATE INDEX ix_boss_jobs_job_id ON boss_jobs(job_id);
CREATE INDEX ix_boss_jobs_task_id ON boss_jobs(task_id);
CREATE INDEX ix_boss_jobs_created_at ON boss_jobs(created_at);

-- 7. 添加外键约束
ALTER TABLE boss_jobs 
ADD CONSTRAINT boss_jobs_task_id_fkey 
FOREIGN KEY (task_id) 
REFERENCES crawl_tasks(task_id) 
ON DELETE CASCADE;

COMMIT;

-- 8. 验证列顺序
SELECT 
    ordinal_position,
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'boss_jobs'
ORDER BY ordinal_position;

-- 预期结果（列顺序）：
-- 1  | id              | integer                  | NO
-- 2  | job_id          | character varying        | NO
-- 3  | task_id         | uuid                     | NO
-- 4  | job_name        | character varying        | NO
-- 5  | company_name    | character varying        | NO
-- 6  | salary          | character varying        | YES
-- 7  | location        | character varying        | YES
-- 8  | experience      | character varying        | YES
-- 9  | education       | character varying        | YES
-- 10 | job_description | text                     | YES
-- 11 | welfare_tags    | jsonb                    | YES
-- 12 | crawled_at      | timestamp with time zone | YES
-- 13 | created_at      | timestamp with time zone | YES
