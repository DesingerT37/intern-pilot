"""
SQLAlchemy ORM 模型定义
映射数据库表结构
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # 关系
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescriptionDB", back_populates="user", cascade="all, delete-orphan")
    match_analyses = relationship("MatchAnalysisDB", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("UserStatistics", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Resume(Base):
    """简历表"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # 文件信息
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_path = Column(String(500))
    
    # 基本信息
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    target_position = Column(String(100))
    
    # 原始文本
    raw_text = Column(Text)
    markdown_text = Column(Text)
    
    # 结构化数据（JSON）
    education_json = Column(Text)  # SQLite 用 Text，PostgreSQL 用 JSONB
    skills_json = Column(Text)
    projects_json = Column(Text)
    work_experience_json = Column(Text)
    certifications_json = Column(Text)
    awards_json = Column(Text)
    
    # 元数据
    parsed = Column(Boolean, default=False)
    parse_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="resumes")
    match_analyses = relationship("MatchAnalysisDB", back_populates="resume", cascade="all, delete-orphan")
    versions = relationship("ResumeVersionDB", back_populates="resume", cascade="all, delete-orphan")
    chat_messages = relationship("ResumeChatHistoryDB", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersionDB(Base):
    """简历版本历史表"""
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    resume_id = Column(
        UUID(as_uuid=False),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    resume = relationship("Resume", back_populates="versions")
    user = relationship("User")


class ResumeChatHistoryDB(Base):
    """简历优化对话历史表"""
    __tablename__ = "resume_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    resume_id = Column(
        UUID(as_uuid=False),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    modified_section = Column(Text)
    section_type = Column(String(50))
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    resume = relationship("Resume", back_populates="chat_messages")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_chat_role"),
    )


class JobDescriptionDB(Base):
    """
    职位描述表
    职责：存储用户输入的 JD 文本并解析出结构化信息用于简历匹配
    """
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # 原始 JD 文本（用户输入的完整职位描述）
    raw_text = Column(Text, nullable=False)
    
    # AI 解析出的结构化信息（JSONB 格式，用于简历匹配）
    required_skills = Column(JSONB)        # 必需技能列表
    preferred_skills = Column(JSONB)       # 优先技能列表
    responsibilities = Column(JSONB)       # 工作职责列表
    requirements = Column(JSONB)           # 任职要求列表
    keywords = Column(JSONB)               # 关键词列表（用于搜索和匹配）
    
    # 解析状态
    parsed = Column(Boolean, default=False)  # 是否已完成 AI 解析
    parse_error = Column(Text)               # 解析失败时的错误信息
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="job_descriptions")
    match_analyses = relationship("MatchAnalysisDB", back_populates="job_description", cascade="all, delete-orphan")


class MatchAnalysisDB(Base):
    """
    简历-JD 匹配分析表
    职责：存储简历与职位描述的匹配分析结果
    """
    __tablename__ = "match_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(
        UUID(as_uuid=False),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jd_id = Column(
        UUID(as_uuid=False),
        ForeignKey("job_descriptions.jd_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # 匹配分析结果
    overall_score = Column(Numeric(5, 2))              # 总体匹配度 (0-100)
    skill_match_score = Column(Numeric(5, 2))          # 技能匹配度
    experience_match_score = Column(Numeric(5, 2))     # 经验匹配度
    education_match_score = Column(Numeric(5, 2))      # 学历匹配度
    
    matched_skills = Column(JSONB)                     # 匹配的技能列表
    missing_skills = Column(JSONB)                     # 缺失的技能列表
    strengths = Column(JSONB)                          # 候选人优势列表
    weaknesses = Column(JSONB)                         # 候选人劣势列表
    suggestions = Column(JSONB)                        # 优化建议列表（实际存储的是 enhancements）
    
    # AI 生成的详细分析报告（Markdown 格式）
    analysis_report = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="match_analyses")
    resume = relationship("Resume", back_populates="match_analyses")
    job_description = relationship("JobDescriptionDB", back_populates="match_analyses")
    
    # 约束
    __table_args__ = (
        CheckConstraint('overall_score >= 0 AND overall_score <= 100', name='check_overall_score'),
    )



class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    status = Column(String(50), nullable=False, index=True)
    error_message = Column(Text)
    execution_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class UserStatistics(Base):
    """用户使用统计表"""
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # 使用统计
    total_resumes = Column(Integer, default=0)
    total_jds = Column(Integer, default=0)
    total_matches = Column(Integer, default=0)
    total_crawl_tasks = Column(Integer, default=0)
    
    # 最后活动
    last_login_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="statistics")


class CrawlTask(Base):
    """爬取任务表"""
    __tablename__ = "crawl_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(UUID(as_uuid=False), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # 任务配置
    keyword = Column(String(200), nullable=False)
    city = Column(String(100))
    max_pages = Column(Integer, default=5)
    
    # 任务状态
    status = Column(String(50), default="pending", index=True)  # pending/running/completed/failed
    progress = Column(Integer, default=0)
    total_jobs = Column(Integer, default=0)
    crawled_jobs = Column(Integer, default=0)
    
    # 时间戳
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    boss_jobs = relationship("BossJob", back_populates="crawl_task", cascade="all, delete-orphan")
    batch_analysis = relationship("BatchAnalysis", back_populates="crawl_task", uselist=False, cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint('status IN (\'pending\', \'running\', \'completed\', \'failed\')', name='check_crawl_task_status'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_crawl_task_progress'),
    )


class BossJob(Base):
    """BOSS 直聘职位数据表"""
    __tablename__ = "boss_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), nullable=False, index=True)  # 移除 unique=True，允许不同任务抓取相同职位
    
    # 基本信息
    job_name = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False)
    salary = Column(String(100))
    location = Column(String(200))
    experience = Column(String(100))
    education = Column(String(100))
    
    # 详细信息
    job_description = Column(Text)
    welfare_tags = Column(JSONB)
    
    # 爬取信息 - 职位属于任务，不直接属于用户
    task_id = Column(UUID(as_uuid=False), ForeignKey("crawl_tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    crawl_task = relationship("CrawlTask", back_populates="boss_jobs")


class BatchAnalysis(Base):
    """批量分析结果表"""
    __tablename__ = "batch_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(UUID(as_uuid=False), unique=True, nullable=False, index=True, server_default=func.uuid_generate_v4())
    resume_id = Column(
        UUID(as_uuid=False),
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crawl_task_id = Column(UUID(as_uuid=False), ForeignKey("crawl_tasks.task_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # 分析统计
    total_jobs = Column(Integer, default=0)
    analyzed_jobs = Column(Integer, default=0)
    avg_match_score = Column(Float)
    max_match_score = Column(Float)
    min_match_score = Column(Float)
    
    # 聚合结果（JSONB）
    top_matched_jobs_json = Column(JSONB)
    common_missing_skills_json = Column(JSONB)
    common_suggestions_json = Column(JSONB)
    
    # 状态
    status = Column(String(50), default="pending", index=True)  # pending/running/completed/failed
    progress = Column(Integer, default=0)
    
    # 时间戳
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    crawl_task = relationship("CrawlTask", back_populates="batch_analysis")
    
    # 约束
    __table_args__ = (
        CheckConstraint('status IN (\'pending\', \'running\', \'completed\', \'failed\')', name='check_batch_analysis_status'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_batch_analysis_progress'),
    )
