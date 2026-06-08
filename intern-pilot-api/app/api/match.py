"""
匹配分析 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from app.models.schemas import MatchRequest, MatchResponse, ErrorResponse
from app.core.database import get_db
from app.services.db_service import DatabaseService
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/analyze", response_model=MatchResponse)
async def analyze_match(
    request: MatchRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析简历与 JD 的匹配度
    
    返回:
    - 匹配度评分
    - 优势/劣势分析
    - 已命中/缺失技能
    """
    try:
        from app.services.match_service import match_service
        from app.models.schemas import Resume, JobDescription
        import json
        
        # 1. 从数据库加载简历和 JD 数据
        db_service = DatabaseService(db)
        
        resume_db = db_service.get_resume(request.resume_id)
        jd_db = db_service.get_jd(request.jd_id)
        
        if not resume_db or not resume_db.parsed:
            raise HTTPException(
                status_code=404,
                detail=f"简历未找到或未解析: {request.resume_id}"
            )
        
        if not jd_db or not jd_db.parsed:
            raise HTTPException(
                status_code=404,
                detail=f"JD 未找到或未解析: {request.jd_id}"
            )
        
        # 验证简历和JD的所有权
        if resume_db.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="无权访问此简历"
            )
        
        if jd_db.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="无权访问此JD"
            )
        
        # 2. 转换为 Pydantic 模型（PostgreSQL JSONB 字段自动返回 Python 对象）
        resume = Resume(
            name=resume_db.name,
            email=resume_db.email,
            phone=resume_db.phone,
            target_position=resume_db.target_position,
            education=resume_db.education_json if resume_db.education_json else [],
            skills=resume_db.skills_json if resume_db.skills_json else [],
            projects=resume_db.projects_json if resume_db.projects_json else [],
            work_experience=resume_db.work_experience_json if resume_db.work_experience_json else [],
            certifications=resume_db.certifications_json if resume_db.certifications_json else [],
            awards=resume_db.awards_json if resume_db.awards_json else []
        )
        
        # 2. 构建 JD 对象（从数据库 JSONB 字段直接获取）
        jd = JobDescription(
            required_skills=jd_db.required_skills if jd_db.required_skills else [],
            preferred_skills=jd_db.preferred_skills if jd_db.preferred_skills else [],
            responsibilities=jd_db.responsibilities if jd_db.responsibilities else [],
            requirements=jd_db.requirements if jd_db.requirements else [],
            keywords=jd_db.keywords if jd_db.keywords else []
        )
        
        # 3. 执行匹配分析
        logger.info(f"🔍 开始匹配分析: {resume.name} vs JD (skills: {len(jd.required_skills)})")
        analysis = await match_service.analyze_match(resume, jd)
        
        # 4. 生成增强建议
        enhancements, report = await match_service.generate_enhancements(resume, jd, analysis)
        
        # 5. 生成匹配 ID 并保存到数据库
        match_id = str(uuid.uuid4())
        
        db_service.save_match_analysis(
            match_id=match_id,
            resume_id=request.resume_id,
            jd_id=request.jd_id,
            analysis=analysis,
            enhancements=enhancements,
            report_markdown=report,
            user_id=current_user.id  # 关联当前登录用户
        )
        
        logger.info(f"✅ 匹配分析完成: 总体匹配度 {analysis.overall_score}%, user_id={current_user.id}")
        
        return MatchResponse(
            match_id=match_id,
            analysis=analysis,
            enhancements=enhancements,
            report_markdown=report,
            message="匹配分析成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 匹配分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/enhance", response_model=MatchResponse)
async def enhance_resume(
    request: MatchRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成简历增强建议
    
    根据 JD 要求，给出针对性的简历修改建议
    """
    try:
        # enhance 接口与 analyze 接口功能相同
        # 都返回匹配分析 + 增强建议
        return await analyze_match(request, current_user, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 简历增强失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"增强失败: {str(e)}")


@router.get("/{match_id}")
async def get_match_result(match_id: str):
    """
    获取匹配分析结果
    """
    # TODO: 从数据库或缓存中获取匹配结果
    raise HTTPException(status_code=501, detail="功能开发中")
