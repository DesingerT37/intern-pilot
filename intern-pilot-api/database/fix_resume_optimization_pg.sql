-- 修复简历优化相关表（PostgreSQL UUID 外键）
-- 在 intern-pilot-api 目录下用 psql 或客户端执行

ALTER TABLE resumes ADD COLUMN IF NOT EXISTS markdown_text TEXT;

CREATE TABLE IF NOT EXISTS resume_versions (
    id SERIAL PRIMARY KEY,
    version_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_resume_versions_resume_id ON resume_versions(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_versions_user_id ON resume_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_versions_created_at ON resume_versions(created_at);

CREATE TABLE IF NOT EXISTS resume_chat_history (
    id SERIAL PRIMARY KEY,
    chat_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    modified_section TEXT,
    section_type VARCHAR(50),
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_history_resume_id ON resume_chat_history(resume_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON resume_chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON resume_chat_history(created_at);
