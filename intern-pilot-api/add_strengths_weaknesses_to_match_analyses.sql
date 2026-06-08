-- 添加 strengths 和 weaknesses 字段到 match_analyses 表
-- 用于存储候选人的优势和劣势分析

-- 添加 strengths 字段（JSONB 类型，存储优势列表）
ALTER TABLE match_analyses 
ADD COLUMN IF NOT EXISTS strengths JSONB DEFAULT '[]'::jsonb;

-- 添加 weaknesses 字段（JSONB 类型，存储劣势列表）
ALTER TABLE match_analyses 
ADD COLUMN IF NOT EXISTS weaknesses JSONB DEFAULT '[]'::jsonb;

-- 添加注释
COMMENT ON COLUMN match_analyses.strengths IS '候选人优势列表';
COMMENT ON COLUMN match_analyses.weaknesses IS '候选人劣势列表';

-- 验证字段已添加
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'match_analyses' 
  AND column_name IN ('strengths', 'weaknesses');
