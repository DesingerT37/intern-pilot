"""
用户认证 API
注册、登录、获取当前用户信息
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import AuthService


router = APIRouter()
security = HTTPBearer()


# ============ Request/Response Models ============

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ 依赖注入：获取当前用户 ============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    从 JWT token 中获取当前用户
    用于需要认证的接口
    """
    token = credentials.credentials
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ============ API Endpoints ============

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **username**: 用户名（唯一）
    - **email**: 邮箱（唯一）
    - **password**: 密码（至少 6 位）
    """
    # 验证密码长度
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为 6 位"
        )
    
    # 注册用户
    auth_service = AuthService(db)
    try:
        user = auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT token，用于后续请求认证
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token = auth_service.login(
            username=request.username,
            password=request.password
        )
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at.isoformat()
            )
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要在 Header 中携带 JWT token:
    ```
    Authorization: Bearer <token>
    ```
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.get("/stats")
async def get_user_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户使用统计
    
    返回用户的简历数、JD数、匹配分析数等统计信息
    """
    from app.services.db_service import DatabaseService
    
    db_service = DatabaseService(db)
    stats = db_service.get_user_statistics(current_user.id)
    
    if not stats:
        return {
            "total_resumes": 0,
            "total_jds": 0,
            "total_matches": 0,
            "last_login_at": None,
            "last_activity_at": None
        }
    
    return {
        "total_resumes": stats.total_resumes,
        "total_jds": stats.total_jds,
        "total_matches": stats.total_matches,
        "last_login_at": stats.last_login_at.isoformat() if stats.last_login_at else None,
        "last_activity_at": stats.last_activity_at.isoformat() if stats.last_activity_at else None
    }
