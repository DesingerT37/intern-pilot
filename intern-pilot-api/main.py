"""
InternPilot API - 主入口文件
AI实习求职助手后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os
from pathlib import Path

from app.core.config import settings
from app.api import resume, jd, match, auth, history, batch_analysis, boss_login, resume_optimization

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 创建 FastAPI 应用
app = FastAPI(
    title="InternPilot API",
    description="AI实习求职助手后端服务 - 简历优化与岗位匹配",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])
app.include_router(resume.router, prefix="/api/resume", tags=["简历管理"])
app.include_router(jd.router, prefix="/api/jd", tags=["岗位需求"])
app.include_router(match.router, prefix="/api/match", tags=["匹配分析"])
app.include_router(batch_analysis.router, prefix="/api", tags=["批量分析"])
app.include_router(boss_login.router, prefix="/api/boss/login", tags=["BOSS登录"])
app.include_router(
    resume_optimization.router,
    prefix="/api/resume-optimization",
    tags=["简历优化"],
)

# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "InternPilot API is running",
        "version": "1.0.0"
    }

@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {
        "message": "Welcome to InternPilot API",
        "docs": "/docs",
        "health": "/health"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 InternPilot API 启动中...")
    
    # 初始化数据库
    try:
        from app.core.database import init_db
        init_db()
        logger.info("✅ 数据库初始化完成")
    except Exception as e:
        logger.warning(f"⚠️  数据库初始化失败: {str(e)}")
    
    logger.info(f"📝 API 文档: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔍 健康检查: http://{settings.HOST}:{settings.PORT}/health")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 InternPilot API 关闭")

if __name__ == "__main__":
    import uvicorn
    
    # 直接传递 app 对象而不是字符串，避免 reload 模式下的导入问题
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
