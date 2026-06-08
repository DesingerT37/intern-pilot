# InternPilot API

AI实习求职助手 - 后端服务

## 快速开始

### 1. 创建虚拟环境

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置 LLM API Key：

```env
OPENAI_API_KEY=your_api_key_here
```

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

## API 文档

启动服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 项目结构

```
intern-pilot-api/
├── app/
│   ├── api/              # API 路由
│   │   ├── resume.py     # 简历管理
│   │   ├── jd.py         # 岗位需求
│   │   └── match.py      # 匹配分析
│   ├── services/         # 业务服务
│   │   └── llm_service.py  # LLM 调用服务
│   ├── agents/           # Agent 逻辑 (Sprint 1+)
│   ├── models/           # 数据模型
│   │   └── schemas.py    # Pydantic 模型
│   ├── core/             # 核心配置
│   │   └── config.py     # 配置管理
│   └── tools/            # 工具函数 (Sprint 1+)
├── uploads/              # 上传文件目录
├── main.py               # 应用入口
├── requirements.txt      # 依赖列表
└── .env                  # 环境变量 (需自行创建)
```

## 开发进度

### Sprint 0 ✅ (已完成)
- [x] 项目脚手架
- [x] FastAPI 基础配置
- [x] 路由结构
- [x] 数据模型定义
- [x] LLM 服务封装
- [x] 简历上传接口

### Sprint 1 (进行中)
- [ ] 简历解析 (PDF/Word → Markdown)
- [ ] JD 解析 (文本 → 结构化数据)
- [ ] LLM 结构化输出集成

### Sprint 2 (计划中)
- [ ] 匹配分析
- [ ] 简历增强建议
- [ ] 流式输出 (SSE)

## 技术栈

- **框架**: FastAPI 0.109+
- **LLM**: OpenAI API / 国产大模型
- **文档解析**: PyMuPDF4LLM, pdfplumber, python-docx
- **数据验证**: Pydantic 2.5+
- **日志**: Loguru
- **数据库**: SQLite (MVP) → PostgreSQL (生产)

## 许可证

MIT
