# job_descriptions 表重新设计总结

## 问题诊断

原表设计存在以下问题：
1. **职责不清**：混淆了"职位数据库"和"JD 解析"两个不同的职责
2. **冗余字段**：包含 `company`、`position`、`location`、`salary_range` 等字段，但这些字段：
   - 对于 JD 解析和简历匹配分析并不必要
   - 有 NOT NULL 约束，但初始保存时无法提供值
   - 导致插入失败：`null value in column "company" violates not-null constraint`
3. **字段命名不一致**：使用 `_json` 后缀（如 `required_skills_json`），但实际是 JSONB 类型

## 新设计原则

### 表职责
`job_descriptions` 表的唯一职责：
- **存储用户输入的 JD 文本**
- **AI 解析出结构化信息**（技能、职责、要求等）
- **用于简历匹配分析**

### 核心字段
1. `raw_text`：用户输入的完整 JD 文本
2. `required_skills`：AI 解析出的必需技能列表（JSONB）
3. `preferred_skills`：AI 解析出的优先技能列表（JSONB）
4. `responsibilities`：AI 解析出的工作职责列表（JSONB）
5. `requirements`：AI 解析出的任职要求列表（JSONB）
6. `keywords`：AI 提取的关键词列表（JSONB），用于搜索和匹配
7. `parsed`：是否已完成 AI 解析
8. `parse_error`：解析失败时的错误信息

### 删除的字段
- ❌ `company`：不需要，这不是职位数据库
- ❌ `position`：不需要，这不是职位数据库
- ❌ `location`：不需要，这不是职位数据库
- ❌ `salary_range`：不需要，这不是职位数据库
- ❌ `benefits_json`：不需要，福利待遇对匹配分析意义不大

## 修改的文件

### 1. SQL 迁移脚本
- **文件**：`redesign_job_descriptions.sql`
- **操作**：
  - 删除旧的 `match_analyses` 和 `job_descriptions` 表
  - 创建新的 `job_descriptions` 表（只包含必要字段）
  - 重新创建 `match_analyses` 表（更新字段名）
  - 添加索引和注释

### 2. Python ORM 模型
- **文件**：`app/models/database.py`
- **修改**：
  - `JobDescriptionDB`：删除 `company`、`position` 等字段，使用 JSONB 字段
  - `MatchAnalysisDB`：更新字段名（`match_score` → `overall_score`，添加细分评分）
  - 添加 `Numeric` 导入

### 3. Pydantic Schemas
- **文件**：`app/models/schemas.py`
- **修改**：
  - `JobDescription`：删除 `company`、`position` 等字段
  - `MatchAnalysis`：更新字段名，添加细分评分

### 4. 数据库服务
- **文件**：`app/services/db_service.py`
- **修改**：
  - `update_jd_parsed`：直接赋值 JSONB 字段，不需要 `json.dumps()`

## 执行步骤

### 1. 备份数据（如果需要）
```sql
-- 备份现有数据
CREATE TABLE job_descriptions_backup AS SELECT * FROM job_descriptions;
CREATE TABLE match_analyses_backup AS SELECT * FROM match_analyses;
```

### 2. 执行迁移脚本
```bash
psql -U your_user -d your_database -f redesign_job_descriptions.sql
```

### 3. 重启后端服务
```bash
cd intern-pilot-api
python main.py
```

### 4. 测试
- 上传 JD 文本
- 触发 AI 解析
- 执行简历匹配分析
- 验证数据正确保存

## 注意事项

1. **数据丢失**：执行迁移脚本会删除现有的 `job_descriptions` 和 `match_analyses` 表数据
2. **外键约束**：`match_analyses` 表依赖 `job_descriptions` 表，必须先删除 `match_analyses`
3. **JSONB 字段**：PostgreSQL 的 JSONB 字段会自动返回 Python 对象（list/dict），不需要 `json.loads()`
4. **索引优化**：为 JSONB 字段创建了 GIN 索引，提升搜索性能

## 后续优化建议

1. **添加全文搜索**：为 `raw_text` 字段添加全文搜索索引
2. **缓存解析结果**：对于相同的 JD 文本，可以缓存解析结果
3. **批量解析**：支持批量上传和解析 JD
4. **解析质量评估**：添加字段记录解析质量评分
