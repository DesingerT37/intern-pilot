-- ============================================
-- 重新设计 job_descriptions 表
-- 职责：存储用户输入的 JD 文本，解析出结构化信息用于简历匹配分析
-- ============================================

-- 1. 删除旧表（包括相关的外键约束）
DROP TABLE IF EXISTS match_analyses CASCADE;
DROP TABLE IF EXISTS job_descriptions CASCADE;

-- 2. 创建新的 job_descriptions 表
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    jd_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 原始 JD 文本（用户输入的完整职位描述）
    raw_text TEXT NOT NULL,
    
    -- AI 解析出的结构化信息（JSONB 格式，用于简历匹配）
    required_skills JSONB,           -- 必需技能列表 ["Python", "Django", "PostgreSQL"]
    preferred_skills JSONB,          -- 优先技能列表 ["Docker", "K8s"]
    responsibilities JSONB,          -- 工作职责列表 ["开发后端 API", "数据库设计"]
    requirements JSONB,              -- 任职要求列表 ["本科及以上", "3年以上经验"]
    keywords JSONB,                  -- 关键词列表（用于搜索和匹配）["后端", "Python", "全栈"]
    
    -- 解析状态
    parsed BOOLEAN DEFAULT FALSE,    -- 是否已完成 AI 解析
    parse_error TEXT,                -- 解析失败时的错误信息
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
CREATE INDEX idx_jd_jd_id ON job_descriptions(jd_id);
CREATE INDEX idx_jd_user_id ON job_descriptions(user_id);
CREATE INDEX idx_jd_parsed ON job_descriptions(parsed);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at);

-- 4. 创建 GIN 索引用于 JSONB 字段的快速搜索
CREATE INDEX idx_jd_required_skills ON job_descriptions USING gin(required_skills);
CREATE INDEX idx_jd_keywords ON job_descriptions USING gin(keywords);

-- 5. 重新创建 match_analyses 表（依赖 job_descriptions）
CREATE TABLE match_analyses (
    id SERIAL PRIMARY KEY,
    match_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    resume_id UUID REFERENCES resumes(resume_id) ON DELETE CASCADE NOT NULL,
    jd_id UUID REFERENCES job_descriptions(jd_id) ON DELETE CASCADE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 匹配分析结果
    overall_score DECIMAL(5,2),                    -- 总体匹配度 (0-100)
    skill_match_score DECIMAL(5,2),                -- 技能匹配度
    experience_match_score DECIMAL(5,2),           -- 经验匹配度
    education_match_score DECIMAL(5,2),            -- 学历匹配度
    
    matched_skills JSONB,                          -- 匹配的技能列表
    missing_skills JSONB,                          -- 缺失的技能列表
    suggestions JSONB,                             -- 优化建议列表
    
    -- AI 生成的详细分析报告
    analysis_report TEXT,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建 match_analyses 索引
CREATE INDEX idx_match_match_id ON match_analyses(match_id);
CREATE INDEX idx_match_resume_id ON match_analyses(resume_id);
CREATE INDEX idx_match_jd_id ON match_analyses(jd_id);
CREATE INDEX idx_match_user_id ON match_analyses(user_id);
CREATE INDEX idx_match_overall_score ON match_analyses(overall_score);
CREATE INDEX idx_match_created_at ON match_analyses(created_at);

-- 7. 添加表注释
COMMENT ON TABLE job_descriptions IS '职位描述表：存储用户输入的 JD 文本并解析出结构化信息用于简历匹配';
COMMENT ON COLUMN job_descriptions.raw_text IS '用户输入的完整 JD 文本';
COMMENT ON COLUMN job_descriptions.required_skills IS 'AI 解析出的必需技能列表（JSONB）';
COMMENT ON COLUMN job_descriptions.preferred_skills IS 'AI 解析出的优先技能列表（JSONB）';
COMMENT ON COLUMN job_descriptions.responsibilities IS 'AI 解析出的工作职责列表（JSONB）';
COMMENT ON COLUMN job_descriptions.requirements IS 'AI 解析出的任职要求列表（JSONB）';
COMMENT ON COLUMN job_descriptions.keywords IS 'AI 提取的关键词列表（JSONB），用于搜索和匹配';
COMMENT ON COLUMN job_descriptions.parsed IS '是否已完成 AI 解析';
COMMENT ON COLUMN job_descriptions.parse_error IS '解析失败时的错误信息';

COMMENT ON TABLE match_analyses IS '简历-JD 匹配分析表：存储简历与职位描述的匹配分析结果';
COMMENT ON COLUMN match_analyses.overall_score IS '总体匹配度评分 (0-100)';
COMMENT ON COLUMN match_analyses.matched_skills IS '简历中匹配的技能列表（JSONB）';
COMMENT ON COLUMN match_analyses.missing_skills IS '简历中缺失的技能列表（JSONB）';
COMMENT ON COLUMN match_analyses.suggestions IS 'AI 生成的优化建议列表（JSONB）';
COMMENT ON COLUMN match_analyses.analysis_report IS 'AI 生成的详细分析报告（Markdown 格式）';
