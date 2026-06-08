"""
简历优化 Agent API 路由
"""
import json
import os
import tempfile
import time
from collections import defaultdict
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import SessionLocal, get_db
from app.models.database import Resume
from app.models.schemas import (
    BatchAnalysisListItem,
    BatchSuggestionResponse,
    ExportRequest,
    MatchAnalysisListItem,
    MatchSuggestionResponse,
    ResumeChatMessage,
    ResumeChatRequest,
    ResumeChatResponse,
    ResumeContentResponse,
    ResumeListItem,
    ResumeUpdateRequest,
    SuccessResponse,
    Suggestion,
    VersionCreateRequest,
    VersionListItem,
    VersionResponse,
)
from app.services.db_service import DatabaseService
from app.services.export_service import ExportService
from app.services.resume_optimization_service import resume_optimization_service
from app.utils.ids import as_str_id

router = APIRouter()

# 导出频率限制：每用户 5 次/分钟
_EXPORT_RATE_WINDOW_SEC = 60
_EXPORT_RATE_MAX = 5
_export_timestamps: dict[int, list[float]] = defaultdict(list)

_CATEGORY_MAP = {
    "技能": "skill",
    "skill": "skill",
    "项目": "project",
    "project": "project",
    "描述": "description",
    "description": "description",
    "格式": "format",
    "format": "format",
    "general": "description",
}


def _get_resume_or_403(db: Session, resume_id: str, user_id: int) -> Resume:
    db_service = DatabaseService(db)
    resume = db_service.get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此简历")
    return resume


def _resume_markdown(resume: Resume) -> str:
    if resume.markdown_text:
        return resume.markdown_text
    if resume.raw_text:
        return resume.raw_text
    return ""


def _db_messages_to_context(messages) -> List[ResumeChatMessage]:
    return [
        ResumeChatMessage(
            role=m.role,
            content=m.content,
            timestamp=m.created_at,
            modified_section=m.modified_section,
            section_type=m.section_type,
            explanation=m.explanation,
        )
        for m in messages
    ]


def _normalize_category(category: str) -> str:
    if not category:
        return "description"
    key = category.strip().lower()
    return _CATEGORY_MAP.get(category, _CATEGORY_MAP.get(key, "description"))


def _enhancement_to_suggestion(item: dict) -> Suggestion:
    if isinstance(item, str):
        return Suggestion(
            priority=3,
            category="description",
            title=item,
            description=item,
        )
    return Suggestion(
        priority=max(1, min(5, int(item.get("priority", 3)))),
        category=_normalize_category(item.get("category", "description")),
        title=item.get("title", ""),
        description=item.get("description", ""),
        example=item.get("example"),
    )


def _check_export_rate_limit(user_id: int) -> None:
    now = time.time()
    timestamps = [t for t in _export_timestamps[user_id] if now - t < _EXPORT_RATE_WINDOW_SEC]
    if len(timestamps) >= _EXPORT_RATE_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="导出请求过于频繁，请稍后再试（限制：5 次/分钟）",
        )
    timestamps.append(now)
    _export_timestamps[user_id] = timestamps


# ============ 简历管理 ============


@router.get("/resumes", response_model=List[ResumeListItem])
async def get_user_resumes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有简历列表"""
    db_service = DatabaseService(db)
    resumes = db_service.get_user_resumes(current_user.id, limit=100)
    return [
        ResumeListItem(
            resume_id=as_str_id(r.resume_id),
            filename=r.filename,
            name=r.name,
            target_position=r.target_position,
            parsed=bool(r.parsed),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in resumes
    ]


@router.get("/resumes/{resume_id}", response_model=ResumeContentResponse)
async def get_resume_content(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取简历 Markdown 内容"""
    resume = _get_resume_or_403(db, resume_id, current_user.id)
    return ResumeContentResponse(
        resume_id=as_str_id(resume.resume_id),
        markdown_text=_resume_markdown(resume),
        name=resume.name,
        email=resume.email,
        phone=resume.phone,
        target_position=resume.target_position,
        updated_at=resume.updated_at,
    )


@router.put("/resumes/{resume_id}", response_model=SuccessResponse)
async def update_resume_content(
    resume_id: str,
    request: ResumeUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新简历 Markdown 内容"""
    _get_resume_or_403(db, resume_id, current_user.id)
    db_service = DatabaseService(db)
    updated = db_service.update_resume_markdown(resume_id, request.markdown_text)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return SuccessResponse(message="简历已保存", data={"resume_id": resume_id})


@router.post("/resumes/{resume_id}/versions", response_model=VersionResponse)
async def create_resume_version(
    resume_id: str,
    request: VersionCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建简历版本快照"""
    resume = _get_resume_or_403(db, resume_id, current_user.id)
    content = _resume_markdown(resume)
    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="简历内容为空，无法创建版本",
        )
    db_service = DatabaseService(db)
    version = db_service.create_resume_version(
        resume_id=resume_id,
        user_id=current_user.id,
        content=content,
        description=request.description,
    )
    return VersionResponse(
        version_id=as_str_id(version.version_id),
        resume_id=as_str_id(version.resume_id),
        content=version.content,
        description=version.description,
        created_at=version.created_at,
    )


@router.get("/resumes/{resume_id}/versions", response_model=List[VersionListItem])
async def list_resume_versions(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取简历版本历史列表"""
    _get_resume_or_403(db, resume_id, current_user.id)
    db_service = DatabaseService(db)
    versions = db_service.get_resume_versions(resume_id, current_user.id)
    return [
        VersionListItem(
            version_id=as_str_id(v.version_id),
            resume_id=as_str_id(v.resume_id),
            description=v.description,
            created_at=v.created_at,
            content_preview=(v.content[:200] + "…") if len(v.content) > 200 else v.content,
        )
        for v in versions
    ]


@router.get("/resumes/{resume_id}/versions/{version_id}", response_model=VersionResponse)
async def get_resume_version(
    resume_id: str,
    version_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定版本完整内容（用于回滚预览）"""
    _get_resume_or_403(db, resume_id, current_user.id)
    db_service = DatabaseService(db)
    version = db_service.get_resume_version(version_id, current_user.id)
    if not version or as_str_id(version.resume_id) != resume_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")
    return VersionResponse(
        version_id=as_str_id(version.version_id),
        resume_id=as_str_id(version.resume_id),
        content=version.content,
        description=version.description,
        created_at=version.created_at,
    )


# ============ AI 对话 ============


@router.post("/chat", response_model=ResumeChatResponse)
async def chat_with_ai(
    request: ResumeChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 对话优化简历（非流式）"""
    _get_resume_or_403(db, request.resume_id, current_user.id)
    db_service = DatabaseService(db)

    history = db_service.get_resume_chat_history(
        request.resume_id, current_user.id, limit=10
    )
    context = _db_messages_to_context(history)
    if request.context:
        context = request.context[-5:] if len(request.context) > 5 else request.context

    db_service.save_chat_message(
        resume_id=request.resume_id,
        user_id=current_user.id,
        role="user",
        content=request.message,
    )

    try:
        result = await resume_optimization_service.chat(
            resume_content=request.resume_content,
            user_message=request.message,
            context=context,
            suggestions=request.suggestions,
        )
    except Exception as e:
        logger.error(f"AI 对话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable, please try again later",
        ) from e

    db_service.save_chat_message(
        resume_id=request.resume_id,
        user_id=current_user.id,
        role="assistant",
        content=result["message"],
        modified_section=result.get("modified_section"),
        section_type=result.get("section_type"),
        explanation=result.get("explanation"),
    )

    return ResumeChatResponse(
        message=result["message"],
        modified_section=result.get("modified_section"),
        section_type=result.get("section_type"),
        explanation=result.get("explanation"),
    )


@router.post("/chat/stream")
async def chat_with_ai_stream(
    request: ResumeChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 对话优化简历（SSE 流式）"""
    _get_resume_or_403(db, request.resume_id, current_user.id)
    db_service = DatabaseService(db)

    history = db_service.get_resume_chat_history(
        request.resume_id, current_user.id, limit=10
    )
    context = _db_messages_to_context(history)
    if request.context:
        context = request.context[-5:] if len(request.context) > 5 else request.context

    db_service.save_chat_message(
        resume_id=request.resume_id,
        user_id=current_user.id,
        role="user",
        content=request.message,
    )

    resume_id = request.resume_id
    user_id = current_user.id

    async def event_generator():
        full_response = ""
        metadata = {}

        try:
            async for chunk in resume_optimization_service.chat_stream(
                resume_content=request.resume_content,
                user_message=request.message,
                context=context,
                suggestions=request.suggestions,
            ):
                yield chunk
                if chunk.startswith("data: "):
                    try:
                        payload = json.loads(chunk[6:].strip())
                        if payload.get("type") == "content":
                            full_response += payload.get("data", "")
                        elif payload.get("type") == "metadata":
                            metadata = payload.get("data", {})
                    except json.JSONDecodeError:
                        pass
        finally:
            if full_response or metadata:
                save_db = SessionLocal()
                try:
                    svc = DatabaseService(save_db)
                    svc.save_chat_message(
                        resume_id=resume_id,
                        user_id=user_id,
                        role="assistant",
                        content=full_response or metadata.get("explanation", ""),
                        modified_section=metadata.get("modified_section"),
                        section_type=metadata.get("section_type"),
                        explanation=metadata.get("explanation"),
                    )
                finally:
                    save_db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============ 建议获取 ============


def _match_job_label(match) -> str:
    resume = match.resume
    jd = match.job_description
    if resume and resume.target_position:
        return resume.target_position
    keywords = (jd.keywords if jd and jd.keywords else []) or []
    if keywords:
        return " · ".join(str(k) for k in keywords[:2])
    return "职位匹配分析"


def _suggestion_count_from_json(raw) -> int:
    if not raw:
        return 0
    if isinstance(raw, list):
        return len(raw)
    return 0


@router.get(
    "/resumes/{resume_id}/match-analyses",
    response_model=List[MatchAnalysisListItem],
)
async def list_resume_match_analyses(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出当前简历在 match_analyses 表中的匹配分析记录"""
    _get_resume_or_403(db, resume_id, current_user.id)
    db_service = DatabaseService(db)
    matches = db_service.get_resume_matches(resume_id, current_user.id)
    if not matches:
        matches = [
            m
            for m in db_service.get_user_matches(current_user.id, limit=50)
            if as_str_id(m.resume_id) == resume_id
        ]
    return [
        MatchAnalysisListItem(
            source="jd_match",
            match_id=as_str_id(m.match_id),
            resume_id=as_str_id(m.resume_id),
            overall_score=float(m.overall_score or 0),
            job_label=_match_job_label(m),
            suggestion_count=_suggestion_count_from_json(m.suggestions),
            created_at=m.created_at,
        )
        for m in matches
    ]


@router.get(
    "/resumes/{resume_id}/batch-analyses",
    response_model=List[BatchAnalysisListItem],
)
async def list_resume_batch_analyses(
    resume_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出当前简历在 batch_analyses 表中的批量分析记录"""
    _get_resume_or_403(db, resume_id, current_user.id)
    db_service = DatabaseService(db)
    batches = db_service.get_resume_batch_analyses(resume_id, current_user.id)
    if not batches:
        batches = [
            b
            for b in db_service.get_user_batch_analyses(current_user.id, limit=50)
            if as_str_id(b.resume_id) == resume_id
        ]
    items: List[BatchAnalysisListItem] = []
    for b in batches:
        task = b.crawl_task
        keyword = task.keyword if task else "批量分析"
        task_id = as_str_id(b.crawl_task_id)
        items.append(
            BatchAnalysisListItem(
                source="batch",
                task_id=task_id,
                batch_id=as_str_id(b.batch_id),
                resume_id=as_str_id(b.resume_id),
                keyword=keyword,
                total_jobs=int(b.total_jobs or 0),
                avg_match_score=float(b.avg_match_score) if b.avg_match_score is not None else None,
                status=b.status or "pending",
                suggestion_count=_suggestion_count_from_json(b.common_suggestions_json),
                created_at=b.created_at,
            )
        )
    return items


@router.get("/suggestions/match/{match_id}", response_model=MatchSuggestionResponse)
async def get_match_suggestions(
    match_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取匹配分析的优化建议"""
    db_service = DatabaseService(db)
    match = db_service.get_match_analysis(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="匹配分析不存在")
    resume = db_service.get_resume(as_str_id(match.resume_id))
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此匹配分析")

    enhancements_raw = match.suggestions or []
    suggestions = sorted(
        [_enhancement_to_suggestion(e) for e in enhancements_raw if e],
        key=lambda s: s.priority,
    )

    jd = match.job_description
    resume = match.resume
    keywords = (jd.keywords if jd and jd.keywords else []) or []
    job_name = (
        resume.target_position
        if resume and resume.target_position
        else (keywords[0] if keywords else "职位匹配分析")
    )
    company_name = keywords[1] if len(keywords) > 1 else "—"

    return MatchSuggestionResponse(
        match_id=as_str_id(match.match_id),
        job_name=job_name,
        company_name=company_name,
        overall_score=float(match.overall_score or 0),
        suggestions=suggestions,
        matched_skills=match.matched_skills or [],
        missing_skills=match.missing_skills or [],
        strengths=match.strengths or [],
        weaknesses=match.weaknesses or [],
    )


@router.get("/suggestions/batch/{task_id}", response_model=BatchSuggestionResponse)
async def get_batch_suggestions(
    task_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取批量分析的优化建议（优先读 batch_analyses.common_suggestions_json）"""
    db_service = DatabaseService(db)
    batch = db_service.get_batch_analysis_by_task(task_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="批量分析结果不存在")

    resume = db_service.get_resume(as_str_id(batch.resume_id))
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此批量分析")

    task = db_service.get_crawl_task(task_id)
    keyword = task.keyword if task else "批量分析"

    raw_suggestions = batch.common_suggestions_json
    if isinstance(raw_suggestions, str):
        try:
            raw_suggestions = json.loads(raw_suggestions)
        except json.JSONDecodeError:
            raw_suggestions = []

    priority_suggestions = sorted(
        [_enhancement_to_suggestion(e) for e in (raw_suggestions or []) if e],
        key=lambda s: s.priority,
    )

    total_jobs = int(batch.total_jobs or 0)
    top_skills: list = []

    if not priority_suggestions and batch.status == "completed":
        from app.services.batch_analysis_service import BatchAnalysisService

        service = BatchAnalysisService(db)
        result = service.get_batch_analysis(task_id)
        if result:
            priority_suggestions = sorted(
                [
                    Suggestion(
                        priority=max(1, min(5, s.priority)),
                        category=_normalize_category(s.category),
                        title=s.title,
                        description=s.description,
                        example=s.example,
                    )
                    for s in result.priority_suggestions
                ],
                key=lambda s: s.priority,
            )
            total_jobs = result.aggregated_analysis.total_jobs
            top_skills = result.aggregated_analysis.top_skills

    if batch.status != "completed" and not priority_suggestions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批量分析尚未完成，暂无建议",
        )

    missing_skills = batch.common_missing_skills_json or []
    if isinstance(missing_skills, str):
        try:
            missing_skills = json.loads(missing_skills)
        except json.JSONDecodeError:
            missing_skills = []

    return BatchSuggestionResponse(
        task_id=task_id,
        keyword=keyword,
        total_jobs=total_jobs,
        common_missing_skills=missing_skills if isinstance(missing_skills, list) else [],
        priority_suggestions=priority_suggestions,
        top_skills=top_skills,
    )


# ============ 导出 ============


def _export_file(
    request: ExportRequest,
    current_user,
    db: Session,
    file_ext: str,
    media_type: str,
    export_fn,
) -> FileResponse:
    _check_export_rate_limit(current_user.id)
    _get_resume_or_403(db, request.resume_id, current_user.id)

    style = request.style or "default"
    if style not in ExportService.STYLES:
        style = "default"

    tmp_dir = tempfile.mkdtemp(prefix="resume_export_")
    filename = f"resume_{request.resume_id[:8]}.{file_ext}"
    output_path = os.path.join(tmp_dir, filename)

    try:
        export_fn(request.markdown_content, output_path, style)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"导出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {e}",
        ) from e

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=filename,
        background=None,
    )


@router.post("/export/pdf")
async def export_to_pdf(
    request: ExportRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导出简历为 PDF"""
    return _export_file(
        request,
        current_user,
        db,
        "pdf",
        "application/pdf",
        ExportService.export_to_pdf,
    )


@router.post("/export/docx")
async def export_to_docx(
    request: ExportRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导出简历为 DOCX"""
    return _export_file(
        request,
        current_user,
        db,
        "docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ExportService.export_to_docx,
    )
