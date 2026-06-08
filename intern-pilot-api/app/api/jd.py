"""
岗位需求 (JD) API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from app.models.schemas import JDParseRequest, JDParseResponse, ErrorResponse
from app.core.database import get_db
from app.services.db_service import DatabaseService
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/parse", response_model=JDParseResponse)
async def parse_jd(
    request: JDParseRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解析岗位需求 (JD) 文本
    
    提取关键信息：
    - 必备技能 vs 加分项
    - 岗位关键词
    - 工作内容摘要
    - 任职要求
    """
    try:
        if not request.jd_text or len(request.jd_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="JD 文本过短，请提供完整的岗位描述"
            )
        
        # 解析 JD
        from app.services.jd_service import jd_service
        
        logger.info(f"🔍 开始解析 JD ({len(request.jd_text)} 字符)")
        jd_data, keywords = await jd_service.parse_jd(request.jd_text)
        
        # 生成 JD ID 并保存到数据库
        jd_id = str(uuid.uuid4())
        db_service = DatabaseService(db)
        
        # 先保存原始文本
        db_service.save_jd(
            jd_id=jd_id,
            raw_text=request.jd_text,
            user_id=current_user.id  # 关联当前登录用户
        )
        
        # 再更新解析结果
        db_service.update_jd_parsed(
            jd_id=jd_id,
            jd_data=jd_data,
            keywords=keywords
        )
        
        logger.info(f"✅ JD 解析完成: jd_id={jd_id}, user_id={current_user.id}, skills_count={len(jd_data.required_skills)}")
        
        return JDParseResponse(
            jd_id=jd_id,
            jd_data=jd_data,
            keywords=keywords,
            message="JD 解析成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ JD 解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get("/{jd_id}")
async def get_jd(jd_id: str):
    """
    获取已解析的 JD 数据
    """
    # TODO: 从数据库或缓存中获取 JD 数据
    raise HTTPException(status_code=501, detail="功能开发中")


@router.delete("/{jd_id}")
async def delete_jd(jd_id: str):
    """
    删除 JD
    """
    # TODO: 删除数据库记录
    raise HTTPException(status_code=501, detail="功能开发中")
