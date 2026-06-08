-- PostgreSQL 数据库初始化脚本
-- 用于生产环境

-- ============================================
-- 创建数据库（如果不存在）
-- -- ============================================
-- CREATE DATABASE internpilot
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'zh_CN.UTF-8'
--     LC_CTYPE = 'zh_CN.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- 连接到数据库
-- \c internpilot

-- ============================================
-- 启用扩展
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID 生成
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- 文本相似度搜索

-- ============================================
-- 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ============================================
-- 简历表
-- ============================================
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    resume_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    
    -- 基本信息
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    target_position VARCHAR(100),
    
    -- 原始文本
    raw_text TEXT,
    markdown_text TEXT,
    
    -- 结构化数据（JSONB）
    education_json JSONB,
    skills_json JSONB,
    projects_json JSONB,
    work_experience_json JSONB,
    certifications_json JSONB,
    awards_json JSONB,
    
    -- 元数据
    parsed BOOLEAN DEFAULT FALSE,
    parse_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resumes_resume_id ON resumes(resume_id);
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_created_at ON resumes(created_at);
CREATE INDEX idx_resumes_name ON resumes USING gin(name gin_trgm_ops);  -- 全文搜索

-- ============================================
-- 岗位需求表
-- ============================================
CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    jd_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 基本信息
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    salary_range VARCHAR(100),
    
    -- 原始文本
    raw_text TEXT NOT NULL,
    
    -- 结构化数据（JSONB）
    required_skills_json JSONB,
    preferred_skills_json JSONB,
    responsibilities_json JSONB,
    requirements_json JSONB,
    benefits_json JSONB,
    keywords_json JSONB,
    
    -- 元数据
    parsed BOOLEAN DEFAULT FALSE,
    parse_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jd_jd_id ON job_descriptions(jd_id);
CREATE INDEX idx_jd_user_id ON job_descriptions(user_id);
CREATE INDEX idx_jd_company ON job_descriptions(company);
CREATE INDEX idx_jd_position ON job_descriptions(position);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at);
CREATE INDEX idx_jd_company_position ON job_descriptions USING gin((company || ' ' || position) gin_trgm_ops);

-- ============================================
-- 匹配分析表
-- ============================================
CREATE TABLE IF NOT EXISTS match_analyses (
    id SERIAL PRIMARY KEY,
    match_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    jd_id UUID NOT NULL REFERENCES job_descriptions(jd_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 匹配结果
    match_score REAL NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
    
    -- 分析结果（JSONB）
    matched_skills_json JSONB,
    missing_skills_json JSONB,
    strengths_json JSONB,
    weaknesses_json JSONB,
    suggestions_json JSONB,
    
    -- 增强建议（JSONB）
    enhancements_json JSONB,
    
    -- 完整报告
    report_markdown TEXT,
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_match_match_id ON match_analyses(match_id);
CREATE INDEX idx_match_resume_id ON match_analyses(resume_id);
CREATE INDEX idx_match_jd_id ON match_analyses(jd_id);
CREATE INDEX idx_match_user_id ON match_analyses(user_id);
CREATE INDEX idx_match_created_at ON match_analyses(created_at);
CREATE INDEX idx_match_score ON match_analyses(match_score);

-- ============================================
-- BOSS 爬虫职位表
-- ============================================
CREATE TABLE IF NOT EXISTS boss_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 基本信息
    job_name VARCHAR(200) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    salary VARCHAR(100),
    location VARCHAR(200),
    experience VARCHAR(100),
    education VARCHAR(100),
    
    -- 详细信息
    job_description TEXT,
    company_info TEXT,
    welfare_tags JSONB,
    
    -- 职位链接
    job_url VARCHAR(500),
    
    -- 爬取信息
    crawl_task_id UUID,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_boss_jobs_job_id ON boss_jobs(job_id);
CREATE INDEX idx_boss_jobs_user_id ON boss_jobs(user_id);
CREATE INDEX idx_boss_jobs_company ON boss_jobs(company_name);
CREATE INDEX idx_boss_jobs_position ON boss_jobs(job_name);
CREATE INDEX idx_boss_jobs_crawled_at ON boss_jobs(crawled_at);
CREATE INDEX idx_boss_jobs_search ON boss_jobs USING gin((company_name || ' ' || job_name) gin_trgm_ops);

-- ============================================
-- 爬虫任务表
-- ============================================
CREATE TABLE IF NOT EXISTS crawl_tasks (
    id SERIAL PRIMARY KEY,
    task_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 任务配置
    keyword VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    experience VARCHAR(50),
    education VARCHAR(50),
    max_pages INTEGER DEFAULT 5,
    
    -- 任务状态
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    total_jobs INTEGER DEFAULT 0,
    crawled_jobs INTEGER DEFAULT 0,
    
    -- 错误信息
    error_message TEXT,
    
    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crawl_tasks_task_id ON crawl_tasks(task_id);
CREATE INDEX idx_crawl_tasks_user_id ON crawl_tasks(user_id);
CREATE INDEX idx_crawl_tasks_status ON crawl_tasks(status);
CREATE INDEX idx_crawl_tasks_created_at ON crawl_tasks(created_at);

-- ============================================
-- 批量分析表
-- ============================================
CREATE TABLE IF NOT EXISTS batch_analyses (
    id SERIAL PRIMARY KEY,
    batch_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    crawl_task_id UUID NOT NULL REFERENCES crawl_tasks(task_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 分析统计
    total_jobs INTEGER DEFAULT 0,
    analyzed_jobs INTEGER DEFAULT 0,
    avg_match_score REAL,
    max_match_score REAL,
    min_match_score REAL,
    
    -- 聚合结果（JSONB）
    top_matched_jobs_json JSONB,
    common_missing_skills_json JSONB,
    common_suggestions_json JSONB,
    
    -- 状态
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_batch_analyses_batch_id ON batch_analyses(batch_id);
CREATE INDEX idx_batch_analyses_resume_id ON batch_analyses(resume_id);
CREATE INDEX idx_batch_analyses_user_id ON batch_analyses(user_id);
CREATE INDEX idx_batch_analyses_created_at ON batch_analyses(created_at);

-- ============================================
-- 系统日志表
-- ============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    status VARCHAR(50) NOT NULL CHECK (status IN ('success', 'error')),
    error_message TEXT,
    execution_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_logs_action ON system_logs(action);
CREATE INDEX idx_logs_status ON system_logs(status);
CREATE INDEX idx_logs_created_at ON system_logs(created_at);

-- ============================================
-- 用户使用统计表
-- ============================================
CREATE TABLE IF NOT EXISTS user_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 使用统计
    total_resumes INTEGER DEFAULT 0,
    total_jds INTEGER DEFAULT 0,
    total_matches INTEGER DEFAULT 0,
    total_crawl_tasks INTEGER DEFAULT 0,
    
    -- 最后活动
    last_login_at TIMESTAMP,
    last_activity_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stats_user_id ON user_statistics(user_id);

-- ============================================
-- 触发器：自动更新 updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jd_updated_at BEFORE UPDATE ON job_descriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stats_updated_at BEFORE UPDATE ON user_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 视图：用户活动统计
-- ============================================
CREATE OR REPLACE VIEW user_activity_stats AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(DISTINCT r.id) as resume_count,
    COUNT(DISTINCT j.id) as jd_count,
    COUNT(DISTINCT m.id) as match_count,
    MAX(m.created_at) as last_match_at,
    u.created_at as user_created_at
FROM users u
LEFT JOIN resumes r ON u.id = r.user_id
LEFT JOIN job_descriptions j ON u.id = j.user_id
LEFT JOIN match_analyses m ON u.id = m.user_id
GROUP BY u.id, u.username, u.email, u.created_at;

-- ============================================
-- 视图：匹配分析统计
-- ============================================
CREATE OR REPLACE VIEW match_statistics AS
SELECT 
    DATE(created_at) as match_date,
    COUNT(*) as total_matches,
    AVG(match_score) as avg_score,
    MAX(match_score) as max_score,
    MIN(match_score) as min_score,
    COUNT(CASE WHEN match_score >= 80 THEN 1 END) as high_matches,
    COUNT(CASE WHEN match_score >= 60 AND match_score < 80 THEN 1 END) as medium_matches,
    COUNT(CASE WHEN match_score < 60 THEN 1 END) as low_matches
FROM match_analyses
GROUP BY DATE(created_at)
ORDER BY match_date DESC;

-- ============================================
-- 完成提示
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ PostgreSQL 数据库初始化完成！';
    RAISE NOTICE '📊 已创建所有表、索引、触发器和视图';
END $$;
