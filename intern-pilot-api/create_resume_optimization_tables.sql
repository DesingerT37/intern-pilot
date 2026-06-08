-- ============================================
-- Resume Optimization Agent - Database Migration
-- ============================================
-- This script creates the necessary tables for the Resume Optimization Agent feature
-- Run this script against your PostgreSQL database

-- ============================================
-- Task 1.3: Add markdown_text field to resumes table
-- ============================================

-- Add markdown_text column to resumes table (idempotent)
ALTER TABLE resumes 
ADD COLUMN IF NOT EXISTS markdown_text TEXT;

-- Add comment to the field
COMMENT ON COLUMN resumes.markdown_text IS '简历的 Markdown 格式内容';


-- ============================================
-- Task 1.1: Create resume_versions table
-- ============================================

-- Create resume_versions table
CREATE TABLE IF NOT EXISTS resume_versions (
    id SERIAL PRIMARY KEY,
    version_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- Version content
    content TEXT NOT NULL,
    description TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_resume_versions_resume 
        FOREIGN KEY (resume_id) 
        REFERENCES resumes(resume_id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_resume_versions_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- Create indexes for resume_versions
CREATE INDEX IF NOT EXISTS idx_resume_versions_resume_id ON resume_versions(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_versions_user_id ON resume_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_versions_created_at ON resume_versions(created_at);

-- Add table and column comments
COMMENT ON TABLE resume_versions IS '简历版本历史表';
COMMENT ON COLUMN resume_versions.id IS '主键ID';
COMMENT ON COLUMN resume_versions.version_id IS '版本唯一标识（UUID）';
COMMENT ON COLUMN resume_versions.resume_id IS '关联的简历ID';
COMMENT ON COLUMN resume_versions.user_id IS '用户ID';
COMMENT ON COLUMN resume_versions.content IS '该版本的 Markdown 内容';
COMMENT ON COLUMN resume_versions.description IS '版本说明（用户备注）';
COMMENT ON COLUMN resume_versions.created_at IS '版本创建时间';


-- ============================================
-- Task 1.2: Create resume_chat_history table
-- ============================================

-- Create resume_chat_history table
CREATE TABLE IF NOT EXISTS resume_chat_history (
    id SERIAL PRIMARY KEY,
    chat_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- Message content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    
    -- AI response additional information
    modified_section TEXT,
    section_type VARCHAR(50),
    explanation TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_resume_chat_history_resume 
        FOREIGN KEY (resume_id) 
        REFERENCES resumes(resume_id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_resume_chat_history_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- Create indexes for resume_chat_history
CREATE INDEX IF NOT EXISTS idx_chat_history_resume_id ON resume_chat_history(resume_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON resume_chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON resume_chat_history(created_at);

-- Add table and column comments
COMMENT ON TABLE resume_chat_history IS '简历优化对话历史表';
COMMENT ON COLUMN resume_chat_history.id IS '主键ID';
COMMENT ON COLUMN resume_chat_history.chat_id IS '对话消息唯一标识（UUID）';
COMMENT ON COLUMN resume_chat_history.resume_id IS '关联的简历ID';
COMMENT ON COLUMN resume_chat_history.user_id IS '用户ID';
COMMENT ON COLUMN resume_chat_history.role IS '消息角色：user（用户）或 assistant（AI）';
COMMENT ON COLUMN resume_chat_history.content IS '消息内容';
COMMENT ON COLUMN resume_chat_history.modified_section IS 'AI 返回的修改后的 Markdown 段落';
COMMENT ON COLUMN resume_chat_history.section_type IS '修改的段落类型（education/work_experience/projects/skills）';
COMMENT ON COLUMN resume_chat_history.explanation IS 'AI 对修改的说明';
COMMENT ON COLUMN resume_chat_history.created_at IS '消息创建时间';


-- ============================================
-- Verification Queries
-- ============================================

-- Verify tables were created successfully
SELECT 
    table_name, 
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('resume_versions', 'resume_chat_history')
ORDER BY table_name;

-- Verify indexes were created
SELECT 
    tablename, 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND tablename IN ('resume_versions', 'resume_chat_history')
ORDER BY tablename, indexname;

-- Verify markdown_text column was added to resumes
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'resumes' 
    AND column_name = 'markdown_text';
