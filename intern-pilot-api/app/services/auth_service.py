"""
用户认证服务
处理注册、登录、JWT 生成
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.services.db_service import DatabaseService
from app.models.database import User


# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天


class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.db_service = DatabaseService(db)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建 JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """解码 JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register(self, username: str, email: str, password: str) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        if self.db_service.get_user_by_username(username):
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        if self.db_service.get_user_by_email(email):
            raise ValueError("邮箱已被注册")
        
        # 创建用户
        password_hash = self.hash_password(password)
        user = self.db_service.create_user(username, email, password_hash)
        
        return user
    
    def login(self, username: str, password: str) -> tuple[User, str]:
        """用户登录"""
        # 获取用户
        user = self.db_service.get_user_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            raise ValueError("用户名或密码错误")
        
        # 检查用户是否激活
        if not user.is_active:
            raise ValueError("用户已被禁用")
        
        # 生成 token
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # 更新最后登录时间
        stats = self.db_service.get_user_statistics(user.id)
        if stats:
            stats.last_login_at = datetime.now()
            self.db.commit()
        
        return user, access_token
    
    def get_current_user(self, token: str) -> Optional[User]:
        """根据 token 获取当前用户"""
        payload = self.decode_token(token)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        user = self.db_service.get_user_by_username(username)
        return user
