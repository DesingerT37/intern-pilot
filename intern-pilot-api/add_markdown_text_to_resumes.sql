-- 添加 markdown_text 字段到 resumes 表
-- 用于存储简历的 Markdown 格式内容，供简历优化 Agent 使用
-- Requirements: 2.1 (Markdown 编辑和预览), 12.1 (数据持久化和完整性)

-- 添加 markdown_text 字段（TEXT 类型）
ALTER TABLE resumes 
ADD COLUMN IF NOT EXISTS markdown_text TEXT;

-- 添加字段注释
COMMENT ON COLUMN resumes.markdown_text IS '简历的 Markdown 格式内容，用于简历优化 Agent 的编辑和预览功能';

-- 验证字段已添加
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'resumes' 
  AND column_name = 'markdown_text';
