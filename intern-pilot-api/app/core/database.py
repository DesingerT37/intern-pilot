"""
数据库配置和连接管理
支持 SQLite 和 PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
if settings.DATABASE_TYPE == "sqlite":
    # SQLite 配置
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.SQLITE_DB_NAME}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 需要
        echo=settings.DEBUG  # 开发模式下打印 SQL
    )
else:
    # PostgreSQL 配置
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,  # 连接池大小
        max_overflow=20,  # 最大溢出连接数
        pool_pre_ping=True,  # 连接前检查
        echo=settings.DEBUG
    )

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表初始化完成")


def drop_db():
    """删除所有表（谨慎使用！）"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️  所有数据库表已删除")
