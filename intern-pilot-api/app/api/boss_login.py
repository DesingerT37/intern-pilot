"""
BOSS 直聘登录管理 API
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path

# 添加爬虫模块路径
crawler_path = Path(__file__).parent.parent.parent.parent / "boss-job-crawler"
if str(crawler_path) not in sys.path:
    sys.path.insert(0, str(crawler_path))

from boss_crawler.login import LoginManager
from boss_crawler.config import CrawlerConfig
from boss_crawler.exceptions import LoginError, BrowserError

router = APIRouter()

# 全局登录管理器实例
_login_manager: Optional[LoginManager] = None


def get_login_manager() -> LoginManager:
    """获取登录管理器单例"""
    global _login_manager
    if _login_manager is None:
        config = CrawlerConfig()
        _login_manager = LoginManager(config=config)
    return _login_manager


# ============ Response Models ============

class LoginStatusResponse(BaseModel):
    """登录状态响应"""
    is_logged_in: bool
    message: str
    checked_at: str


class LoginActionResponse(BaseModel):
    """登录操作响应"""
    success: bool
    message: str


# ============ API Endpoints ============

@router.get("/status", response_model=LoginStatusResponse)
async def check_login_status():
    """
    检查 BOSS 直聘登录状态
    
    返回:
    - is_logged_in: 是否已登录
    - message: 状态消息
    - checked_at: 检查时间
    """
    try:
        login_manager = get_login_manager()
        status = login_manager.check_login_status()
        
        return LoginStatusResponse(
            is_logged_in=status.is_logged_in,
            message=status.message,
            checked_at=status.checked_at
        )
    except LoginError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查登录状态失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}"
        )


@router.post("/open", response_model=LoginActionResponse)
async def open_login_page():
    """
    打开 BOSS 直聘登录页
    
    在浏览器中打开登录页面,供用户扫码或输入验证码登录
    """
    try:
        login_manager = get_login_manager()
        login_manager.open_login_page()
        
        return LoginActionResponse(
            success=True,
            message="登录页面已打开,请在浏览器中完成登录"
        )
    except BrowserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"打开登录页失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}"
        )


@router.post("/clear", response_model=LoginActionResponse)
async def clear_session():
    """
    清除登录会话
    
    清除本地浏览器用户目录和登录状态文件
    """
    try:
        login_manager = get_login_manager()
        login_manager.clear_session()
        
        # 重置全局实例
        global _login_manager
        _login_manager = None
        
        return LoginActionResponse(
            success=True,
            message="登录会话已清除"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除会话失败: {str(e)}"
        )
