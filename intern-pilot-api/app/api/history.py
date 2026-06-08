"""
历史记录 API
查看用户的简历、JD、匹配分析历史
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

from app.core.database import get_db
from app.services.db_service import DatabaseService
from app.api.auth import get_current_user


router = APIRouter()


# ============ Helper Functions ============

def safe_json_loads(data):
    """
    安全地解析 JSON 数据
    如果数据已经是 list/dict,直接返回
    如果是字符串,则解析
    否则返回空列表
    """
    if data is None:
        return []
    if isinstance(data, (list, dict)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return []
    return []


# ============ Response Models ============

class ResumeHistoryItem(BaseModel):
    """简历历史记录项"""
    resume_id: str
    filename: str
    name: Optional[str]
    target_position: Optional[str]
    parsed: bool
    created_at: str
    
    class Config:
        from_attributes = True


class JDHistoryItem(BaseModel):
    """JD 历史记录项"""
    jd_id: str
    keywords: Optional[List[str]] = []  # 关键词列表，用于标识 JD
    parsed: bool
    created_at: str
    
    class Config:
        from_attributes = True


class MatchHistoryItem(BaseModel):
    """匹配分析历史记录项"""
    match_id: str
    resume_id: str
    jd_id: str
    overall_score: float  # 改为 overall_score
    resume_name: Optional[str]
    jd_keywords: Optional[List[str]] = []  # JD 关键词
    position: Optional[str]
    created_at: str


class ResumeDetail(BaseModel):
    """简历详情"""
    resume_id: str
    filename: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    target_position: Optional[str]
    markdown_text: Optional[str]
    education: List[dict]
    skills: List[str]
    projects: List[dict]
    work_experience: List[dict]
    certifications: List[str]
    awards: List[str]
    created_at: str


class JDDetail(BaseModel):
    """JD 详情"""
    jd_id: str
    raw_text: str
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    requirements: List[str]
    keywords: List[str]
    created_at: str


class MatchDetail(BaseModel):
    """匹配分析详情"""
    match_id: str
    resume_id: str
    jd_id: str
    overall_score: float  # 改为 overall_score
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []  # 简短建议（从 analysis.suggestions）
    enhancements: List[dict] = []  # 详细增强建议（从 suggestions 字段）
    report_markdown: str
    created_at: str
    
    # 关联信息
    resume_name: Optional[str] = None
    jd_keywords: Optional[List[str]] = []


# ============ API Endpoints ============

@router.get("/resumes", response_model=List[ResumeHistoryItem])
async def get_resume_history(
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的简历历史记录
    
    - **limit**: 返回数量限制（默认 20）
    """
    db_service = DatabaseService(db)
    resumes = db_service.get_user_resumes(current_user.id, limit)
    
    return [
        ResumeHistoryItem(
            resume_id=str(r.resume_id),  # 将 UUID 转换为字符串
            filename=r.filename,
            name=r.name,
            target_position=r.target_position,
            parsed=r.parsed,
            created_at=r.created_at.isoformat()
        )
        for r in resumes
    ]


@router.get("/resumes/{resume_id}", response_model=ResumeDetail)
async def get_resume_detail(
    resume_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取简历详情
    
    - **resume_id**: 简历 ID
    """
    db_service = DatabaseService(db)
    resume = db_service.get_resume(resume_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历不存在"
        )
    
    # 验证权限
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此简历"
        )
    
    return ResumeDetail(
        resume_id=str(resume.resume_id),  # 将 UUID 转换为字符串
        filename=resume.filename,
        name=resume.name,
        email=resume.email,
        phone=resume.phone,
        target_position=resume.target_position,
        markdown_text=resume.markdown_text,
        education=safe_json_loads(resume.education_json),
        skills=safe_json_loads(resume.skills_json),
        projects=safe_json_loads(resume.projects_json),
        work_experience=safe_json_loads(resume.work_experience_json),
        certifications=safe_json_loads(resume.certifications_json),
        awards=safe_json_loads(resume.awards_json),
        created_at=resume.created_at.isoformat()
    )


@router.get("/jds", response_model=List[JDHistoryItem])
async def get_jd_history(
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的 JD 历史记录
    
    - **limit**: 返回数量限制（默认 20）
    """
    db_service = DatabaseService(db)
    jds = db_service.get_user_jds(current_user.id, limit)
    
    return [
        JDHistoryItem(
            jd_id=str(jd.jd_id),  # 将 UUID 转换为字符串
            keywords=jd.keywords if jd.keywords else [],
            parsed=jd.parsed,
            created_at=jd.created_at.isoformat()
        )
        for jd in jds
    ]


@router.get("/jds/{jd_id}", response_model=JDDetail)
async def get_jd_detail(
    jd_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取 JD 详情
    
    - **jd_id**: JD ID
    """
    db_service = DatabaseService(db)
    jd = db_service.get_jd(jd_id)
    
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JD 不存在"
        )
    
    # 验证权限
    if jd.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此 JD"
        )
    
    return JDDetail(
        jd_id=str(jd.jd_id),  # 将 UUID 转换为字符串
        raw_text=jd.raw_text,
        required_skills=jd.required_skills if jd.required_skills else [],
        preferred_skills=jd.preferred_skills if jd.preferred_skills else [],
        responsibilities=jd.responsibilities if jd.responsibilities else [],
        requirements=jd.requirements if jd.requirements else [],
        keywords=jd.keywords if jd.keywords else [],
        created_at=jd.created_at.isoformat()
    )


@router.get("/matches", response_model=List[MatchHistoryItem])
async def get_match_history(
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的匹配分析历史记录
    
    - **limit**: 返回数量限制（默认 20）
    """
    try:
        db_service = DatabaseService(db)
        matches = db_service.get_user_matches(current_user.id, limit)
        
        return [
            MatchHistoryItem(
                match_id=str(m.match_id),  # 将 UUID 转换为字符串
                resume_id=str(m.resume_id),  # 将 UUID 转换为字符串
                jd_id=str(m.jd_id),  # 将 UUID 转换为字符串
                overall_score=float(m.overall_score) if m.overall_score else 0.0,
                resume_name=m.resume.name if m.resume else None,
                jd_keywords=m.job_description.keywords if m.job_description and m.job_description.keywords else [],
                position=None,  # 添加 position 字段
                created_at=m.created_at.isoformat()
            )
            for m in matches
        ]
    except Exception as e:
        logger.error(f"❌ 获取匹配历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配历史失败: {str(e)}"
        )


@router.get("/matches/{match_id}", response_model=MatchDetail)
async def get_match_detail(
    match_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取匹配分析详情
    
    - **match_id**: 匹配分析 ID
    """
    try:
        db_service = DatabaseService(db)
        match = db_service.get_match_analysis(match_id)
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="匹配分析不存在"
            )
        
        # 验证权限
        if match.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此匹配分析"
            )
        
        # 从 enhancements 中提取 title 作为 suggestions
        enhancements_list = match.suggestions if match.suggestions else []
        suggestions_list = [enh.get('title', '') for enh in enhancements_list if isinstance(enh, dict)]
        
        return MatchDetail(
            match_id=str(match.match_id),
            resume_id=str(match.resume_id),
            jd_id=str(match.jd_id),
            overall_score=float(match.overall_score) if match.overall_score else 0.0,
            skill_match_score=float(match.skill_match_score) if match.skill_match_score else None,
            experience_match_score=float(match.experience_match_score) if match.experience_match_score else None,
            education_match_score=float(match.education_match_score) if match.education_match_score else None,
            matched_skills=match.matched_skills if match.matched_skills else [],
            missing_skills=match.missing_skills if match.missing_skills else [],
            strengths=match.strengths if match.strengths else [],
            weaknesses=match.weaknesses if match.weaknesses else [],
            suggestions=suggestions_list,  # 从 enhancements 提取 title
            enhancements=enhancements_list,  # 完整的 enhancements 数据
            report_markdown=match.analysis_report or "",
            created_at=match.created_at.isoformat(),
            resume_name=match.resume.name if match.resume else None,
            jd_keywords=match.job_description.keywords if match.job_description and match.job_description.keywords else []
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取匹配详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配详情失败: {str(e)}"
        )
