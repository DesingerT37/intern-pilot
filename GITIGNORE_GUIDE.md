# .gitignore 配置说明

## 📁 项目中的 .gitignore 文件

本项目采用**多层级 .gitignore** 策略：

```
InternPilot/
├── .gitignore                        # ✅ 根目录（整个项目通用规则）
├── intern-pilot-api/.gitignore       # ✅ 后端项目（Python 特定规则）
├── intern-pilot-web/.gitignore       # ✅ 前端项目（Node.js 特定规则）
└── venv/.gitignore                   # ✅ 虚拟环境（Python 自动生成）
```

## ❓ 为什么有多个 .gitignore？

### 1. Git 的层级规则机制

- `.gitignore` 文件是**层级生效**的
- 子目录的 `.gitignore` 会与父目录的规则**叠加**
- **不会冲突**，更具体的规则优先级更高

### 2. 最佳实践

**根目录 `.gitignore`** (InternPilot/.gitignore):
- 项目整体的通用忽略规则
- IDE 配置文件（.idea, .vscode）
- 操作系统文件（.DS_Store, Thumbs.db）
- 项目特定目录（docs/, .kiro/, venv/）

**子项目 `.gitignore`** (intern-pilot-api/.gitignore, intern-pilot-web/.gitignore):
- 各自技术栈的特定规则
- Python: `__pycache__/`, `*.pyc`, `venv/`
- Node.js: `node_modules/`, `dist/`, `*.log`

### 3. 优势

✅ **模块化管理** - 每个子项目管理自己的忽略规则  
✅ **易于维护** - 后端和前端的规则分开，不会混淆  
✅ **团队协作** - 不同技术栈的开发者只需关注自己的 .gitignore  
✅ **可复用** - 子项目的 .gitignore 可以独立复用到其他项目

## 📋 当前配置的忽略内容

### 根目录 .gitignore 忽略的内容

| 类别 | 忽略内容 | 说明 |
|------|----------|------|
| **IDE** | `.idea/`, `.vscode/` | JetBrains、VS Code 配置 |
| **Kiro** | `.kiro/` | Kiro AI 助手配置 |
| **文档** | `docs/` | 项目文档（避免频繁更新） |
| **虚拟环境** | `venv/`, `env/` | Python 虚拟环境 |
| **数据库** | `*.db`, `*.sqlite` | SQLite 数据库文件 |
| **上传文件** | `uploads/` (部分) | 用户上传的简历和文件 |
| **配置文件** | `.env`, `*.key` | 敏感配置和密钥 |
| **日志** | `*.log`, `logs/` | 运行日志 |
| **爬虫** | `boss-job-crawler/sessions/` | 爬虫会话和输出 |

### 子项目 .gitignore 额外忽略的内容

**intern-pilot-api/.gitignore** (后端):
- Python 编译文件: `__pycache__/`, `*.pyc`
- 构建产物: `dist/`, `build/`, `*.egg-info/`

**intern-pilot-web/.gitignore** (前端):
- Node 依赖: `node_modules/`
- 构建产物: `dist/`, `dist-ssr/`
- 本地配置: `*.local`

## 🎯 特殊说明

### 1. uploads 目录

```gitignore
# 忽略所有上传文件
uploads/

# 但保留截图目录结构
!uploads/screenshots/

# 忽略截图文件本身
uploads/screenshots/*.png
uploads/screenshots/*.jpg
```

**原理**: 
- 保留 `uploads/screenshots/` 目录结构
- 使用 `.gitkeep` 文件保持目录存在
- 实际的截图文件不会被上传

### 2. 爬虫目录

```gitignore
# 忽略爬虫的运行数据
boss-job-crawler/sessions/
boss-job-crawler/output/*.xlsx
boss-job-crawler/logs/*.log

# 但保留目录结构
!boss-job-crawler/sessions/.gitkeep
```

**原因**: 
- 会话数据和输出结果是运行时生成的
- 不需要上传到 GitHub
- 保留目录结构便于其他开发者理解项目结构

### 3. 文档目录

```gitignore
docs/
```

**说明**: 
- 如果你希望文档也上传到 GitHub，删除这一行即可
- 当前配置是不上传 `docs/` 目录，避免文档频繁更新影响代码提交

## 🔧 如何修改配置

### 如果你想上传 docs/ 文档

**编辑根目录 `.gitignore`**:
```diff
- docs/
+ # docs/  (已注释，文档将被上传)
```

### 如果你想上传某些截图

**编辑根目录 `.gitignore`**:
```gitignore
# 忽略所有截图
uploads/screenshots/*.png

# 但保留 logo.png
!uploads/screenshots/logo.png
```

### 如果你想保留数据库文件

**编辑根目录 `.gitignore`**:
```diff
- *.db
+ # *.db  (已注释，数据库将被上传)
```

## ✅ 验证 .gitignore 是否生效

### 方法 1: 使用 git status

```bash
# 查看哪些文件会被提交
git status

# 应该看不到 .idea/, venv/, docs/ 等被忽略的目录
```

### 方法 2: 使用 git check-ignore

```bash
# 检查某个文件是否被忽略
git check-ignore -v .idea/
git check-ignore -v venv/
git check-ignore -v docs/

# 如果被忽略，会显示匹配的规则
```

### 方法 3: 查看 .gitignore 覆盖范围

```bash
# 列出所有被忽略的文件
git status --ignored
```

## 🚨 常见问题

### Q1: 为什么我的 .idea 还是被提交了？

**A**: 如果文件**已经被 git 跟踪**，需要先删除：

```bash
# 从 git 中移除（但保留本地文件）
git rm -r --cached .idea/

# 提交更改
git commit -m "Remove .idea from repository"
```

### Q2: 子目录的 .gitignore 会覆盖根目录的吗？

**A**: 不会覆盖，会**叠加**。例如：

- 根目录忽略 `*.log`
- 子目录忽略 `*.tmp`
- 最终效果: 两种文件都被忽略

### Q3: 我想在某个子目录中保留 .log 文件怎么办？

**A**: 在子目录的 `.gitignore` 中使用 `!` 取消忽略：

```gitignore
# 在子目录的 .gitignore 中
!important.log
```

## 📚 参考资料

- [Git 官方文档 - gitignore](https://git-scm.com/docs/gitignore)
- [GitHub .gitignore 模板](https://github.com/github/gitignore)
- [gitignore.io](https://www.toptal.com/developers/gitignore) - 在线生成 .gitignore

---

**总结**: 多个 .gitignore 是正常且推荐的做法，不会产生冲突！✅
