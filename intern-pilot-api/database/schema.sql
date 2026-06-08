-- InternPilot 数据库表结构
-- 支持 SQLite 和 PostgreSQL

-- ============================================
-- 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    resume_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    user_id INTEGER,  -- NULL 表示未登录用户
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,  -- pdf, docx, md
    file_path VARCHAR(500),  -- 文件存储路径
    
    -- 基本信息
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    target_position VARCHAR(100),
    
    -- 原始文本
    raw_text TEXT,
    markdown_text TEXT,
    
    -- 结构化数据（JSON）
    education_json TEXT,  -- JSON array
    skills_json TEXT,  -- JSON array
    projects_json TEXT,  -- JSON array
    work_experience_json TEXT,  -- JSON array
    certifications_json TEXT,  -- JSON array
    awards_json TEXT,  -- JSON array
    
    -- 元数据
    parsed BOOLEAN DEFAULT FALSE,
    parse_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_resumes_resume_id ON resumes(resume_id);
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_created_at ON resumes(created_at);

-- ============================================
-- 岗位需求表 (Job Description)
-- ============================================
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    jd_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    user_id INTEGER,  -- NULL 表示未登录用户
    
    -- 基本信息
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    salary_range VARCHAR(100),
    
    -- 原始文本
    raw_text TEXT NOT NULL,
    
    -- 结构化数据（JSON）
    required_skills_json TEXT,  -- JSON array
    preferred_skills_json TEXT,  -- JSON array
    responsibilities_json TEXT,  -- JSON array
    requirements_json TEXT,  -- JSON array
    benefits_json TEXT,  -- JSON array
    keywords_json TEXT,  -- JSON array
    
    -- 元数据
    parsed BOOLEAN DEFAULT FALSE,
    parse_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_jd_jd_id ON job_descriptions(jd_id);
CREATE INDEX idx_jd_user_id ON job_descriptions(user_id);
CREATE INDEX idx_jd_company ON job_descriptions(company);
CREATE INDEX idx_jd_position ON job_descriptions(position);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at);

-- ============================================
-- 匹配分析表
-- ============================================
CREATE TABLE IF NOT EXISTS match_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    match_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    resume_id VARCHAR(36) NOT NULL,
    jd_id VARCHAR(36) NOT NULL,
    user_id INTEGER,
    
    -- 匹配结果
    match_score REAL NOT NULL,  -- 0-100
    
    -- 分析结果（JSON）
    matched_skills_json TEXT,  -- JSON array
    missing_skills_json TEXT,  -- JSON array
    strengths_json TEXT,  -- JSON array
    weaknesses_json TEXT,  -- JSON array
    suggestions_json TEXT,  -- JSON array
    
    -- 增强建议（JSON）
    enhancements_json TEXT,  -- JSON array of objects
    
    -- 完整报告
    report_markdown TEXT,
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
    FOREIGN KEY (jd_id) REFERENCES job_descriptions(jd_id) ON DELETE CASCADE
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    job_id VARCHAR(100) UNIQUE NOT NULL,  -- BOSS 职位 ID
    user_id INTEGER,
    
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
    welfare_tags TEXT,  -- JSON array
    
    -- 职位链接
    job_url VARCHAR(500),
    
    -- 爬取信息
    crawl_task_id VARCHAR(36),  -- 关联爬取任务
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_boss_jobs_job_id ON boss_jobs(job_id);
CREATE INDEX idx_boss_jobs_user_id ON boss_jobs(user_id);
CREATE INDEX idx_boss_jobs_company ON boss_jobs(company_name);
CREATE INDEX idx_boss_jobs_position ON boss_jobs(job_name);
CREATE INDEX idx_boss_jobs_crawled_at ON boss_jobs(crawled_at);

-- ============================================
-- 爬虫任务表
-- ============================================
CREATE TABLE IF NOT EXISTS crawl_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    task_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    user_id INTEGER,
    
    -- 任务配置
    keyword VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    experience VARCHAR(50),
    education VARCHAR(50),
    max_pages INTEGER DEFAULT 5,
    
    -- 任务状态
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,  -- 0-100
    total_jobs INTEGER DEFAULT 0,
    crawled_jobs INTEGER DEFAULT 0,
    
    -- 错误信息
    error_message TEXT,
    
    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_crawl_tasks_task_id ON crawl_tasks(task_id);
CREATE INDEX idx_crawl_tasks_user_id ON crawl_tasks(user_id);
CREATE INDEX idx_crawl_tasks_status ON crawl_tasks(status);
CREATE INDEX idx_crawl_tasks_created_at ON crawl_tasks(created_at);

-- ============================================
-- 批量分析表
-- ============================================
CREATE TABLE IF NOT EXISTS batch_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    batch_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    resume_id VARCHAR(36) NOT NULL,
    crawl_task_id VARCHAR(36) NOT NULL,
    user_id INTEGER,
    
    -- 分析统计
    total_jobs INTEGER DEFAULT 0,
    analyzed_jobs INTEGER DEFAULT 0,
    avg_match_score REAL,
    max_match_score REAL,
    min_match_score REAL,
    
    -- 聚合结果（JSON）
    top_matched_jobs_json TEXT,  -- JSON array
    common_missing_skills_json TEXT,  -- JSON array
    common_suggestions_json TEXT,  -- JSON array
    
    -- 状态
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,
    
    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
    FOREIGN KEY (crawl_task_id) REFERENCES crawl_tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX idx_batch_analyses_batch_id ON batch_analyses(batch_id);
CREATE INDEX idx_batch_analyses_resume_id ON batch_analyses(resume_id);
CREATE INDEX idx_batch_analyses_user_id ON batch_analyses(user_id);
CREATE INDEX idx_batch_analyses_created_at ON batch_analyses(created_at);

-- ============================================
-- 系统日志表
-- ============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,  -- upload_resume, parse_jd, analyze_match, etc.
    resource_type VARCHAR(50),  -- resume, jd, match, etc.
    resource_id VARCHAR(36),
    status VARCHAR(50) NOT NULL,  -- success, error
    error_message TEXT,
    execution_time REAL,  -- 执行时间（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_logs_action ON system_logs(action);
CREATE INDEX idx_logs_status ON system_logs(status);
CREATE INDEX idx_logs_created_at ON system_logs(created_at);

-- ============================================
-- 用户使用统计表
-- ============================================
CREATE TABLE IF NOT EXISTS user_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL
    user_id INTEGER UNIQUE NOT NULL,
    
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_stats_user_id ON user_statistics(user_id);
