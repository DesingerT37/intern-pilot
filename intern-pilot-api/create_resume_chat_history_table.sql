-- ============================================
-- 创建 resume_chat_history 表
-- 用于存储简历优化 AI 对话历史
-- Requirements: 4.9, 12.3, 16.1
-- ============================================

-- 创建表
CREATE TABLE IF NOT EXISTS resume_chat_history (
    id SERIAL PRIMARY KEY,
    chat_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    resume_id UUID NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- 消息内容
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    
    -- AI 响应的额外信息
    modified_section TEXT,      -- AI 输出的修改段落（Markdown 格式）
    section_type VARCHAR(50),   -- 段落类型（education/work_experience/projects/skills）
    explanation TEXT,           -- 修改说明
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 外键约束
    CONSTRAINT fk_resume_chat_history_resume 
        FOREIGN KEY (resume_id) 
        REFERENCES resumes(resume_id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_resume_chat_history_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_chat_history_resume_id ON resume_chat_history(resume_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON resume_chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON resume_chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_history_chat_id ON resume_chat_history(chat_id);

-- 添加表和字段注释
COMMENT ON TABLE resume_chat_history IS '简历优化对话历史表，存储用户与 AI 的对话记录';
COMMENT ON COLUMN resume_chat_history.id IS '主键 ID';
COMMENT ON COLUMN resume_chat_history.chat_id IS '对话消息唯一标识';
COMMENT ON COLUMN resume_chat_history.resume_id IS '关联的简历 ID';
COMMENT ON COLUMN resume_chat_history.user_id IS '用户 ID';
COMMENT ON COLUMN resume_chat_history.role IS '消息角色：user（用户）或 assistant（AI）';
COMMENT ON COLUMN resume_chat_history.content IS '消息内容';
COMMENT ON COLUMN resume_chat_history.modified_section IS 'AI 返回的修改后的 Markdown 段落';
COMMENT ON COLUMN resume_chat_history.section_type IS '修改的段落类型（education/work_experience/projects/skills）';
COMMENT ON COLUMN resume_chat_history.explanation IS 'AI 对修改的说明';
COMMENT ON COLUMN resume_chat_history.created_at IS '消息创建时间';

-- 验证表已创建
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'resume_chat_history'
ORDER BY ordinal_position;

-- 验证索引已创建
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'resume_chat_history';

-- 验证外键约束已创建
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'resume_chat_history';
