"""
简历管理 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import uuid
from pathlib import Path
from typing import Optional

from app.models.schemas import ResumeUploadResponse, ResumeParseResponse, ErrorResponse
from app.core.config import settings
from app.core.database import get_db
from app.services.db_service import DatabaseService
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传简历文件
    
    支持格式: PDF, DOCX, DOC, Markdown
    """
    try:
        # 验证文件类型
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 验证文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {file_size} bytes。最大允许: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # 生成唯一文件名
        resume_id = str(uuid.uuid4())
        filename = f"{resume_id}{file_ext}"
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        # 保存文件
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 保存到数据库
        db_service = DatabaseService(db)
        
        db_service.save_resume(
            resume_id=resume_id,
            filename=file.filename,
            file_size=file_size,
            file_type=file_ext,
            user_id=current_user.id  # 关联当前登录用户
        )
        
        logger.info(f"✅ 简历上传成功: {filename} ({file_size} bytes), user_id={current_user.id}")
        
        return ResumeUploadResponse(
            resume_id=resume_id,
            filename=file.filename,
            file_size=file_size,
            message="简历上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 简历上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/parse/{resume_id}", response_model=ResumeParseResponse)
async def parse_resume(
    resume_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解析简历文件，提取结构化信息
    
    使用 LLM 进行智能解析
    """
    try:
        # 1. 验证简历所有权
        db_service = DatabaseService(db)
        resume = db_service.get_resume(resume_id)
        
        if not resume:
            raise HTTPException(
                status_code=404,
                detail=f"简历不存在: {resume_id}"
            )
        
        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="无权访问此简历"
            )
        
        # 2. 根据 resume_id 找到文件
        from app.services.resume_service import resume_service
        
        # 查找上传的文件
        upload_dir = Path(settings.UPLOAD_DIR)
        file_path = None
        
        for ext in settings.ALLOWED_EXTENSIONS:
            potential_path = upload_dir / f"{resume_id}{ext}"
            if potential_path.exists():
                file_path = str(potential_path)
                break
        
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"简历文件未找到: {resume_id}"
            )
        
        # 3. 解析简历
        logger.info(f"🔍 开始解析简历: {resume_id}, user_id={current_user.id}")
        md_text, resume_data = await resume_service.parse_resume_file(file_path)
        
        # 4. 保存到数据库
        db_service.update_resume_parsed(
            resume_id=resume_id,
            resume_data=resume_data,
            raw_text=md_text,
            markdown_text=md_text
        )
        
        logger.info(f"✅ 简历解析完成: {resume_data.name}, user_id={current_user.id}")
        
        return ResumeParseResponse(
            resume_id=resume_id,
            resume_data=resume_data,
            raw_text=md_text[:500] + "..." if len(md_text) > 500 else md_text,
            message="简历解析成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 简历解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """
    获取已解析的简历数据
    """
    # TODO: 从数据库或缓存中获取简历数据
    raise HTTPException(status_code=501, detail="功能开发中")


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """
    删除简历
    """
    # TODO: 删除文件和数据库记录
    raise HTTPException(status_code=501, detail="功能开发中")
