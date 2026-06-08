# InternPilot 数据库文档

## 📋 目录
1. [数据库选择](#数据库选择)
2. [表结构说明](#表结构说明)
3. [SQLite 使用](#sqlite-使用)
4. [PostgreSQL 使用](#postgresql-使用)
5. [数据迁移](#数据迁移)

---

## 数据库选择

### SQLite（推荐用于开发/MVP）
**优点**:
- 无需安装数据库服务器
- 零配置，开箱即用
- 文件数据库，易于备份
- 适合单用户/小规模使用

**缺点**:
- 并发性能较弱
- 不适合生产环境
- 缺少高级特性

**适用场景**:
- 本地开发
- MVP 快速验证
- 个人使用
- 小规模部署

### PostgreSQL（推荐用于生产）
**优点**:
- 高性能，支持高并发
- 丰富的数据类型（JSONB）
- 全文搜索支持
- 事务完整性强

**缺点**:
- 需要安装配置
- 资源占用较大
- 学习成本较高

**适用场景**:
- 生产环境
- 多用户系统
- 大规模数据
- 需要高级特性

---

## 表结构说明

### 核心表

#### 1. users（用户表）
存储用户账号信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER/SERIAL | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| email | VARCHAR(100) | 邮箱（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| is_active | BOOLEAN | 是否激活 |

#### 2. resumes（简历表）
存储简历信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER/SERIAL | 主键 |
| resume_id | VARCHAR(36)/UUID | 简历 ID（唯一） |
| user_id | INTEGER | 用户 ID（外键） |
| filename | VARCHAR(255) | 文件名 |
| file_size | INTEGER | 文件大小 |
| file_type | VARCHAR(50) | 文件类型 |
| name | VARCHAR(100) | 姓名 |
| email | VARCHAR(100) | 邮箱 |
| phone | VARCHAR(50) | 电话 |
| target_position | VARCHAR(100) | 目标职位 |
| raw_text | TEXT | 原始文本 |
| markdown_text | TEXT | Markdown 文本 |
| education_json | TEXT/JSONB | 教育背景（JSON） |
| skills_json | TEXT/JSONB | 技能（JSON） |
| projects_json | TEXT/JSONB | 项目经历（JSON） |
| work_experience_json | TEXT/JSONB | 工作经历（JSON） |
| parsed | BOOLEAN | 是否已解析 |
| created_at | TIMESTAMP | 创建时间 |

#### 3. job_descriptions（岗位需求表）
存储 JD 信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER/SERIAL | 主键 |
| jd_id | VARCHAR(36)/UUID | JD ID（唯一） |
| user_id | INTEGER | 用户 ID（外键） |
| company | VARCHAR(200) | 公司名称 |
| position | VARCHAR(200) | 职位名称 |
| location | VARCHAR(200) | 工作地点 |
| salary_range | VARCHAR(100) | 薪资范围 |
| raw_text | TEXT | 原始文本 |
| required_skills_json | TEXT/JSONB | 必备技能（JSON） |
| preferred_skills_json | TEXT/JSONB | 加分项（JSON） |
| responsibilities_json | TEXT/JSONB | 工作职责（JSON） |
| requirements_json | TEXT/JSONB | 任职要求（JSON） |
| keywords_json | TEXT/JSONB | 关键词（JSON） |
| parsed | BOOLEAN | 是否已解析 |
| created_at | TIMESTAMP | 创建时间 |

#### 4. match_analyses（匹配分析表）
存储匹配分析结果

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER/SERIAL | 主键 |
| match_id | VARCHAR(36)/UUID | 匹配 ID（唯一） |
| resume_id | VARCHAR(36)/UUID | 简历 ID（外键） |
| jd_id | VARCHAR(36)/UUID | JD ID（外键） |
| user_id | INTEGER | 用户 ID（外键） |
| match_score | REAL | 匹配度评分（0-100） |
| matched_skills_json | TEXT/JSONB | 已命中技能（JSON） |
| missing_skills_json | TEXT/JSONB | 缺失技能（JSON） |
| strengths_json | TEXT/JSONB | 优势（JSON） |
| weaknesses_json | TEXT/JSONB | 劣势（JSON） |
| suggestions_json | TEXT/JSONB | 建议（JSON） |
| enhancements_json | TEXT/JSONB | 增强建议（JSON） |
| report_markdown | TEXT | 完整报告（Markdown） |
| created_at | TIMESTAMP | 创建时间 |

### 扩展表

#### 5. boss_jobs（BOSS 职位表）
存储爬取的职位信息

#### 6. crawl_tasks（爬虫任务表）
存储爬虫任务信息

#### 7. batch_analyses（批量分析表）
存储批量分析结果

#### 8. system_logs（系统日志表）
存储系统操作日志

#### 9. user_statistics（用户统计表）
存储用户使用统计

---

## SQLite 使用

### 1. 初始化数据库

```bash
# 方式一: 使用 Python 脚本
cd intern-pilot-api
python database/init_sqlite.py

# 方式二: 重置数据库（删除旧数据）
python database/init_sqlite.py reset
```

### 2. 查看数据库

```bash
# 使用 SQLite 命令行
sqlite3 internpilot.db

# 查看所有表
.tables

# 查看表结构
.schema resumes

# 查询数据
SELECT * FROM resumes;

# 退出
.quit
```

### 3. 备份数据库

```bash
# 备份
cp internpilot.db internpilot_backup.db

# 或使用 SQLite 命令
sqlite3 internpilot.db ".backup internpilot_backup.db"
```

### 4. 配置应用

编辑 `.env` 文件:
```env
DATABASE_TYPE=sqlite
SQLITE_DB_NAME=internpilot.db
```

---

## PostgreSQL 使用

### 1. 安装 PostgreSQL

**Windows**:
```bash
# 下载安装包
https://www.postgresql.org/download/windows/

# 或使用 Chocolatey
choco install postgresql
```

**Linux**:
```bash
sudo apt-get install postgresql postgresql-contrib
```

**macOS**:
```bash
brew install postgresql
```

### 2. 创建数据库

```bash
# 登录 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE internpilot;

# 创建用户（可选）
CREATE USER internpilot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE internpilot TO internpilot_user;

# 退出
\q
```

### 3. 初始化表结构

```bash
# 执行 SQL 脚本
psql -U postgres -d internpilot -f database/init_postgresql.sql

# 或在 psql 中执行
\i database/init_postgresql.sql
```

### 4. 配置应用

编辑 `.env` 文件:
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=internpilot
```

### 5. 常用命令

```bash
# 连接数据库
psql -U postgres -d internpilot

# 查看所有表
\dt

# 查看表结构
\d resumes

# 查询数据
SELECT * FROM resumes;

# 查看视图
\dv

# 退出
\q
```

---

## 数据迁移

### SQLite → PostgreSQL

#### 方式一: 使用 pgloader

```bash
# 安装 pgloader
# Windows: 下载二进制文件
# Linux: sudo apt-get install pgloader
# macOS: brew install pgloader

# 执行迁移
pgloader internpilot.db postgresql://postgres:password@localhost/internpilot
```

#### 方式二: 导出导入

```bash
# 1. 从 SQLite 导出数据
sqlite3 internpilot.db .dump > dump.sql

# 2. 转换 SQL 语法（手动或使用工具）
# SQLite 和 PostgreSQL 语法有差异，需要调整

# 3. 导入到 PostgreSQL
psql -U postgres -d internpilot -f dump.sql
```

#### 方式三: 使用 Python 脚本

创建 `migrate.py`:
```python
import sqlite3
import psycopg2

# 连接 SQLite
sqlite_conn = sqlite3.connect('internpilot.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接 PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="internpilot",
    user="postgres",
    password="your_password"
)
pg_cursor = pg_conn.cursor()

# 迁移数据（示例：resumes 表）
sqlite_cursor.execute("SELECT * FROM resumes")
rows = sqlite_cursor.fetchall()

for row in rows:
    pg_cursor.execute(
        "INSERT INTO resumes VALUES (%s, %s, ...)",
        row
    )

pg_conn.commit()
print("✅ 数据迁移完成")
```

---

## 数据库维护

### 备份

**SQLite**:
```bash
# 文件复制
cp internpilot.db backup/internpilot_$(date +%Y%m%d).db
```

**PostgreSQL**:
```bash
# 使用 pg_dump
pg_dump -U postgres internpilot > backup_$(date +%Y%m%d).sql

# 压缩备份
pg_dump -U postgres internpilot | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 恢复

**SQLite**:
```bash
# 直接替换文件
cp backup/internpilot_20250101.db internpilot.db
```

**PostgreSQL**:
```bash
# 删除现有数据库
dropdb -U postgres internpilot

# 创建新数据库
createdb -U postgres internpilot

# 恢复数据
psql -U postgres internpilot < backup_20250101.sql

# 或从压缩文件恢复
gunzip -c backup_20250101.sql.gz | psql -U postgres internpilot
```

### 清理

```sql
-- 删除旧数据（保留最近 30 天）
DELETE FROM system_logs WHERE created_at < NOW() - INTERVAL '30 days';

-- 清理未使用的简历
DELETE FROM resumes WHERE parsed = FALSE AND created_at < NOW() - INTERVAL '7 days';

-- 真空优化（PostgreSQL）
VACUUM ANALYZE;

-- 真空优化（SQLite）
VACUUM;
```

---

## 性能优化

### 索引优化

```sql
-- 查看索引使用情况（PostgreSQL）
SELECT * FROM pg_stat_user_indexes;

-- 创建额外索引
CREATE INDEX idx_resumes_name_email ON resumes(name, email);
CREATE INDEX idx_match_score_desc ON match_analyses(match_score DESC);
```

### 查询优化

```sql
-- 使用 EXPLAIN 分析查询
EXPLAIN ANALYZE SELECT * FROM resumes WHERE name LIKE '%张%';

-- 优化 JSON 查询（PostgreSQL）
CREATE INDEX idx_skills_gin ON resumes USING gin(skills_json);
```

---

## 常见问题

### Q1: SQLite 数据库文件在哪里？
A: 默认在项目根目录 `internpilot.db`

### Q2: 如何查看数据库内容？
A: 使用 SQLite Browser 或 DBeaver 等图形化工具

### Q3: PostgreSQL 连接失败？
A: 检查：
1. PostgreSQL 服务是否启动
2. 端口是否正确（默认 5432）
3. 用户名密码是否正确
4. 防火墙设置

### Q4: 数据迁移会丢失数据吗？
A: 建议先备份，然后测试迁移，确认无误后再正式使用

### Q5: 如何重置数据库？
A: 
- SQLite: `python database/init_sqlite.py reset`
- PostgreSQL: 删除数据库后重新创建

---

## 推荐工具

### 图形化管理工具
- **DBeaver** - 通用数据库工具（推荐）
- **DB Browser for SQLite** - SQLite 专用
- **pgAdmin** - PostgreSQL 专用
- **DataGrip** - JetBrains 出品（付费）

### 命令行工具
- **sqlite3** - SQLite 命令行
- **psql** - PostgreSQL 命令行
- **pgcli** - PostgreSQL 增强命令行

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX
