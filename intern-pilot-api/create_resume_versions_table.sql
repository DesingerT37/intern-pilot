-- ============================================
-- 创建 resume_versions 表（SQLite 版本）
-- 用于存储简历版本历史记录
-- ============================================
-- Requirements: 3.2, 3.3, 12.2
-- 
-- 功能说明：
-- - 记录简历在不同时间点的完整内容快照
-- - 支持版本回滚和历史查看
-- - 每次保存简历时自动创建版本记录
-- ============================================

-- 创建 resume_versions 表
CREATE TABLE IF NOT EXISTS resume_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT UNIQUE NOT NULL,  -- UUID 存储为 TEXT
    resume_id TEXT NOT NULL,          -- 对应 resumes.resume_id
    user_id INTEGER NOT NULL,         -- 对应 users.id
    
    -- 版本内容
    content TEXT NOT NULL,            -- Markdown 内容
    description TEXT,                 -- 版本说明（可选）
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 创建索引
-- ============================================
-- 按简历 ID 查询版本历史
CREATE INDEX IF NOT EXISTS idx_resume_versions_resume_id 
    ON resume_versions(resume_id);

-- 按用户 ID 查询版本历史
CREATE INDEX IF NOT EXISTS idx_resume_versions_user_id 
    ON resume_versions(user_id);

-- 按创建时间排序（用于获取最新版本）
CREATE INDEX IF NOT EXISTS idx_resume_versions_created_at 
    ON resume_versions(created_at DESC);

-- 复合索引：按简历 ID 和创建时间查询（优化常见查询）
CREATE INDEX IF NOT EXISTS idx_resume_versions_resume_created 
    ON resume_versions(resume_id, created_at DESC);

-- ============================================
-- 表和字段说明（SQLite 不支持 COMMENT，使用注释记录）
-- ============================================
-- 表说明：简历版本历史表，记录简历在不同时间点的完整内容快照
-- 
-- 字段说明：
-- - id: 主键，自增 ID
-- - version_id: 版本唯一标识符（UUID，存储为 TEXT）
-- - resume_id: 关联的简历 ID（外键，对应 resumes.resume_id）
-- - user_id: 创建该版本的用户 ID（外键，对应 users.id）
-- - content: 该版本的完整 Markdown 内容
-- - description: 版本说明（用户备注），可选
-- - created_at: 版本创建时间
-- ============================================
