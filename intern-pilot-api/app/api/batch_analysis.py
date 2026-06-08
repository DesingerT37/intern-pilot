"""
批量分析 API
爬取职位 + AI 分析
"""
import asyncio
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import (
    CrawlTaskRequest, CrawlTaskResponse, CrawlProgress, BossJobInfo
)
from app.services.batch_analysis_service import BatchAnalysisService
from app.api.auth import get_current_user


router = APIRouter()


@router.post("/batch-analysis/start", response_model=CrawlTaskResponse)
async def start_batch_analysis(
    request: CrawlTaskRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    启动批量分析任务
    
    - **resume_id**: 简历ID（可选）
    - **keyword**: 职位关键词
    - **city**: 城市（默认：全国）
    - **pages**: 抓取页数（1-10，默认：3）
    - **fetch_details**: 是否抓取职位详情（默认：True）
    """
    service = BatchAnalysisService(db)
    
    try:
        # 创建任务
        task_id = await service.create_task(request, current_user.id)
        
        # 异步执行任务
        asyncio.create_task(service.execute_task(task_id))
        
        return CrawlTaskResponse(
            task_id=task_id,
            message="任务已启动",
            status="pending"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动任务失败: {str(e)}"
        )


@router.get("/batch-analysis/{task_id}/stream")
async def stream_progress(
    task_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    SSE 流式推送任务进度
    
    - **task_id**: 任务UUID
    - **token**: JWT token (可选,从查询参数获取,因为 EventSource 不支持自定义 headers)
    
    返回 Server-Sent Events 流
    """
    # 验证 token
    if token:
        try:
            from app.services.auth_service import AuthService
            auth_service = AuthService(db)
            current_user = auth_service.get_current_user(token)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的 token"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"认证失败: {str(e)}"
            )
    
    service = BatchAnalysisService(db)
    
    async def event_generator():
        """事件生成器"""
        while True:
            try:
                # 查询任务进度
                progress = service.get_progress(task_id)
                
                # 推送进度事件
                data = progress.dict()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # 任务完成，结束流
                if progress.status in ["completed", "failed", "stopped", "not_found"]:
                    break
                
                # 每秒推送一次
                await asyncio.sleep(1)
            
            except Exception as e:
                error_data = {
                    "task_id": task_id,
                    "status": "error",
                    "message": f"获取进度失败: {str(e)}"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@router.get("/batch-analysis/{task_id}/progress", response_model=CrawlProgress)
async def get_progress(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取任务进度（单次查询）
    
    - **task_id**: 任务UUID
    """
    service = BatchAnalysisService(db)
    return service.get_progress(task_id)


@router.get("/batch-analysis/{task_id}/jobs", response_model=list[BossJobInfo])
async def get_task_jobs(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取任务爬取的所有职位
    
    - **task_id**: 任务UUID
    """
    service = BatchAnalysisService(db)
    return service.get_task_jobs(task_id)


@router.post("/batch-analysis/{task_id}/stop")
async def stop_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    停止任务
    
    - **task_id**: 任务UUID
    """
    service = BatchAnalysisService(db)
    
    try:
        await service.stop_task(task_id)
        return {"message": "任务已停止", "task_id": task_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止任务失败: {str(e)}"
        )


@router.post("/batch-analysis/{task_id}/analyze")
async def analyze_batch(
    task_id: str,
    resume_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    对爬取的职位进行批量 AI 分析
    
    - **task_id**: 任务UUID
    - **resume_id**: 简历ID
    
    返回聚合分析结果和优化建议
    """
    service = BatchAnalysisService(db)
    
    try:
        result = await service.analyze_batch(task_id, resume_id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/batch-analysis/{task_id}/result")
async def get_batch_result(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取批量分析结果
    
    - **task_id**: 任务UUID
    """
    service = BatchAnalysisService(db)
    
    result = service.get_batch_analysis(task_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析结果不存在"
        )
    
    return result


@router.get("/batch-analysis/history")
async def get_task_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 20
):
    """
    获取用户的历史爬取任务列表
    
    - **status**: 任务状态过滤（可选：completed, running, failed）
    - **limit**: 返回数量限制（默认20）
    
    返回任务列表，按创建时间倒序
    """
    service = BatchAnalysisService(db)
    
    try:
        tasks = service.get_task_history(current_user.id, status, limit)
        return tasks
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史任务失败: {str(e)}"
        )


@router.get("/batch-analysis/reports")
async def get_analysis_reports(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = 20
):
    """
    获取用户的历史分析报告列表
    
    - **limit**: 返回数量限制（默认20）
    
    返回分析报告列表，按创建时间倒序
    """
    service = BatchAnalysisService(db)
    
    try:
        reports = service.get_analysis_history(current_user.id, limit)
        return reports
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史报告失败: {str(e)}"
        )
