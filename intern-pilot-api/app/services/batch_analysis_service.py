"""
批量分析服务
处理爬取任务和 AI 分析
"""
import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from loguru import logger

from app.models.database import CrawlTask, BossJob, BatchAnalysis, Resume
from app.models.schemas import (
    CrawlTaskRequest, CrawlProgress, BossJobInfo,
    AggregatedJDAnalysis, BatchAnalysisResult, Resume as ResumeSchema,
    EnhancementSuggestion
)
from app.services.crawl_service import crawl_service
from app.services.ai_analysis_service import ai_analysis_service
from app.services.db_service import DatabaseService


# 模块级全局进度缓存，跨请求共享（每次请求都会新建 BatchAnalysisService 实例，
# 实例级字典无法在 execute_task 和 SSE stream 之间共享）
_tasks_progress: Dict[str, CrawlProgress] = {}


class BatchAnalysisService:
    """批量分析服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.db_service = DatabaseService(db)

    @property
    def tasks_progress(self) -> Dict[str, CrawlProgress]:
        return _tasks_progress
    
    async def create_task(self, request: CrawlTaskRequest, user_id: Optional[int] = None) -> str:
        """
        创建爬取任务
        
        Args:
            request: 任务请求
            user_id: 用户ID
            
        Returns:
            任务UUID
        """
        # 创建任务记录
        task = CrawlTask(
            user_id=user_id,
            keyword=request.keyword,
            city=request.city,
            max_pages=request.pages,
            status="pending"
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"创建爬取任务: task_id={task.task_id}, keyword={request.keyword}")
        
        # 初始化进度
        self.tasks_progress[task.task_id] = CrawlProgress(
            task_id=task.task_id,
            status="pending",
            total_pages=request.pages,
            message="任务已创建，等待执行"
        )
        
        return task.task_id
    
    async def execute_task(self, task_id: str):
        """
        执行爬取任务（异步）
        
        Args:
            task_id: 任务UUID
        """
        task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if not task:
            logger.error(f"任务不存在: task_id={task_id}")
            return
        
        try:
            # 更新任务状态
            task.status = "running"
            task.started_at = datetime.now()
            self.db.commit()
            
            # 更新进度
            self._update_progress(task_id, "running", 0, "开始爬取职位数据...", 0, 0)
            
            logger.info(f"开始执行任务: task_id={task_id}, keyword={task.keyword}, city={task.city}, pages={task.max_pages}")
            
            max_pages = task.max_pages or 3

            # 爬虫事件回调：实时更新进度缓存，让 SSE 流能看到中间状态
            def on_crawler_event(event):
                from boss_crawler.events import EventType
                if event.type == EventType.PROGRESS:
                    p = event.payload
                    page = int(p.get("page", 0))
                    total_jobs = int(p.get("total_jobs", 0))
                    unique_jobs = int(p.get("unique_jobs", 0))
                    completed = int(p.get("completed_jobs", 0))
                    pct = int(completed / unique_jobs * 100) if unique_jobs > 0 else int(page / max_pages * 50)
                    self._update_progress(
                        task_id, "running", pct,
                        event.message, total_jobs, unique_jobs,
                        current_page=page
                    )

            # 调用爬虫（传入实时事件回调）
            jobs, result = await crawl_service.crawl_jobs(
                keyword=task.keyword,
                city=task.city or "全国",
                pages=max_pages,
                fetch_details=True,
                event_handler=on_crawler_event
            )
            
            logger.info(f"爬虫返回结果: jobs_count={len(jobs)}, result={result}")
            
            # 更新进度：正在关闭浏览器
            self._update_progress(
                task_id, "running", 95,
                "正在关闭浏览器...", result.total_jobs, result.unique_jobs
            )
            
            # 保存职位数据
            if jobs:
                await self._save_jobs(task_id, jobs)
                logger.info(f"职位数据已保存: count={len(jobs)}")
            else:
                logger.warning(f"没有爬取到职位数据: task_id={task_id}")
            
            # 重新获取任务对象（因为 _save_jobs 可能导致会话刷新）
            task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if not task:
                logger.error(f"任务对象丢失: task_id={task_id}")
                return
            
            # 更新任务状态
            task.status = "completed"
            task.completed_at = datetime.now()
            task.total_jobs = result.total_jobs
            task.crawled_jobs = result.unique_jobs
            task.progress = 100
            self.db.commit()
            
            logger.info(f"任务状态已更新为 completed: task_id={task_id}")
            
            # 更新进度
            self._update_progress(
                task_id, "completed", 100,
                f"爬取完成！共找到 {result.unique_jobs} 个职位",
                result.total_jobs,
                result.unique_jobs
            )
            
            logger.info(f"任务完成: task_id={task_id}, total_jobs={result.total_jobs}, unique_jobs={result.unique_jobs}")
            
        except Exception as e:
            logger.error(f"任务执行失败: task_id={task_id}, error={e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 重新获取任务对象
            task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if task:
                # 更新任务状态
                task.status = "failed"
                task.completed_at = datetime.now()
                self.db.commit()
                logger.info(f"任务状态已更新为 failed: task_id={task_id}")
            
            # 更新进度
            self._update_progress(task_id, "failed", 0, f"爬取失败: {str(e)}", 0, 0)
    
    async def _save_jobs(self, task_id: str, jobs: List[Any]):
        """
        保存职位数据到数据库
        
        Args:
            task_id: 任务UUID
            jobs: 职位列表（JobInfo 对象）
        """
        from sqlalchemy.exc import IntegrityError
        
        saved_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i, job in enumerate(jobs):
            try:
                # 检查该任务下是否已存在相同的 job_id
                existing_job = self.db.query(BossJob).filter(
                    BossJob.task_id == task_id,
                    BossJob.job_id == job.job_id
                ).first()
                
                if existing_job:
                    skipped_count += 1
                    logger.debug(f"职位已存在，跳过: job_id={job.job_id}")
                    continue
                
                # 确保 job_tags 是列表类型
                job_tags = job.job_tags if isinstance(job.job_tags, list) else []
                
                boss_job = BossJob(
                    task_id=task_id,
                    job_id=job.job_id,
                    job_name=job.job_name,
                    company_name=job.company_name,
                    location=job.location,
                    salary=job.salary_range,
                    education=job.education,
                    experience=job.experience,
                    job_description=job.job_description,
                    welfare_tags=job_tags  # JSONB 字段，确保是列表
                )
                self.db.add(boss_job)
                saved_count += 1
                
                # 每 10 条提交一次，避免大事务
                if (i + 1) % 10 == 0:
                    try:
                        self.db.commit()
                        logger.debug(f"已保存 {saved_count} 条职位数据")
                    except IntegrityError as ie:
                        # 批量提交时遇到错误，回滚并继续
                        logger.warning(f"批量提交遇到错误，回滚: {ie}")
                        self.db.rollback()
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"保存职位数据失败 (第 {i+1} 条): job_id={job.job_id}, error={e}")
                self.db.rollback()
                continue
        
        # 提交剩余的数据
        try:
            self.db.commit()
            logger.info(f"保存职位数据完成: task_id={task_id}, 新增={saved_count}, 跳过={skipped_count}, 失败={failed_count}")
        except IntegrityError as ie:
            logger.warning(f"最终提交遇到错误: {ie}")
            self.db.rollback()
            # 不抛出异常，让任务继续
        except Exception as e:
            logger.error(f"最终提交失败: {e}")
            self.db.rollback()
            # 不抛出异常，让任务继续（因为数据可能已经部分保存）
            logger.warning(f"部分数据可能已保存，任务继续执行")
    
    def get_progress(self, task_id: str) -> CrawlProgress:
        """
        获取任务进度
        
        Args:
            task_id: 任务UUID
            
        Returns:
            进度信息
        """
        # 从缓存获取
        if task_id in self.tasks_progress:
            return self.tasks_progress[task_id]
        
        # 从数据库查询
        task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if not task:
            return CrawlProgress(
                task_id=task_id,
                status="not_found",
                total_pages=0,
                message="任务不存在"
            )
        
        return CrawlProgress(
            task_id=task.task_id,
            status=task.status,
            total_pages=task.max_pages,
            jobs_found=task.total_jobs,
            unique_jobs=task.crawled_jobs,
            progress_percentage=task.progress,
            message="任务进行中" if task.status == "running" else f"任务状态: {task.status}"
        )
    
    def _update_progress(
        self,
        task_id: str,
        status: str,
        progress: float,
        message: str,
        jobs_found: int = 0,
        unique_jobs: int = 0,
        current_page: int = 0
    ):
        """
        更新任务进度（同时写入全局缓存和数据库）
        """
        # 获取总页数
        total_pages = 0
        if task_id in self.tasks_progress:
            total_pages = self.tasks_progress[task_id].total_pages
        else:
            task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if task:
                total_pages = task.max_pages

        self.tasks_progress[task_id] = CrawlProgress(
            task_id=task_id,
            status=status,
            current_page=current_page,
            total_pages=total_pages,
            jobs_found=jobs_found,
            unique_jobs=unique_jobs,
            message=message,
            progress_percentage=progress
        )

        # 同步写数据库，让轮询 /progress 接口也能看到实时数据
        try:
            task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if task:
                task.total_jobs = jobs_found
                task.crawled_jobs = unique_jobs
                task.progress = progress
                self.db.commit()
        except Exception as e:
            logger.warning(f"更新数据库进度失败（不影响主流程）: {e}")
    
    def get_task_jobs(self, task_id: str) -> List[BossJobInfo]:
        """
        获取任务的所有职位
        
        Args:
            task_id: 任务UUID
            
        Returns:
            职位列表
        """
        jobs = self.db.query(BossJob).filter(BossJob.task_id == task_id).all()
        
        return [
            BossJobInfo(
                job_id=job.job_id,
                job_name=job.job_name,
                company_name=job.company_name,
                location=job.location,
                salary_range=job.salary,
                education=job.education,
                experience=job.experience,
                job_description=job.job_description,
                job_tags=job.welfare_tags if job.welfare_tags else []
            )
            for job in jobs
        ]
    
    async def stop_task(self, task_id: str):
        """
        停止任务
        
        Args:
            task_id: 任务UUID
        """
        task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if task and task.status == "running":
            task.status = "failed"  # SQL schema uses 'failed', not 'stopped'
            task.completed_at = datetime.now()
            self.db.commit()
            
            self._update_progress(task_id, "stopped", 0, "任务已停止")
            logger.info(f"任务已停止: task_id={task_id}")
    
    async def analyze_batch(self, task_id: str, resume_id: str) -> BatchAnalysisResult:
        """
        对爬取的职位进行批量 AI 分析
        
        Args:
            task_id: 任务UUID
            resume_id: 简历ID
            
        Returns:
            批量分析结果
        """
        logger.info(f"开始批量分析: task_id={task_id}, resume_id={resume_id}")
        
        # 刷新数据库会话，确保能读取到最新数据
        self.db.expire_all()
        
        try:
            # 1. 获取任务和职位数据
            task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if not task:
                logger.error(f"任务不存在: {task_id}")
                raise ValueError(f"任务不存在: {task_id}")
            
            logger.info(f"任务状态: {task.status}")
            if task.status != "completed":
                logger.error(f"任务未完成，无法分析: status={task.status}")
                raise ValueError(f"任务未完成，无法分析: status={task.status}")
            
            jobs = self.get_task_jobs(task_id)
            logger.info(f"获取到 {len(jobs)} 个职位")
            if not jobs:
                logger.error("没有找到职位数据")
                raise ValueError("没有找到职位数据")
        except Exception as e:
            logger.error(f"获取任务或职位数据失败: {e}")
            raise
        
        # 2. 获取简历数据
        try:
            resume_db = self.db.query(Resume).filter(Resume.resume_id == resume_id).first()
            if not resume_db:
                logger.error(f"简历不存在: {resume_id}")
                raise ValueError(f"简历不存在: {resume_id}")
            
            logger.info(f"开始解析简历数据: resume_id={resume_id}")
            resume = self._parse_resume_from_db(resume_db)
            logger.info(f"简历解析成功: name={resume.name}, skills_count={len(resume.skills)}")
        except Exception as e:
            logger.error(f"获取或解析简历失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # 3. AI 聚合分析
        try:
            logger.info(f"开始聚合分析 {len(jobs)} 个职位")
            aggregated = await ai_analysis_service.aggregate_jds(jobs, task.keyword)
            logger.info(f"聚合分析完成")
        except Exception as e:
            logger.error(f"AI 聚合分析失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # 4. 生成优化建议
        try:
            logger.info("开始生成优化建议")
            suggestions = await ai_analysis_service.generate_suggestions(
                resume, aggregated, task.keyword
            )
            logger.info(f"生成了 {len(suggestions)} 条优化建议")
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # 5. 计算每个职位的匹配度
        logger.info("开始计算每个职位的匹配度...")
        job_match_scores = []
        
        for job in jobs:
            # 为每个职位计算匹配度
            job_score = self._calculate_job_match_score(resume, job, aggregated.top_skills)
            job_match_scores.append({
                "job_id": job.job_id,
                "job_name": job.job_name,
                "company_name": job.company_name,
                "location": job.location,
                "salary_range": job.salary_range,
                "match_score": job_score["score"],
                "matched_skills": job_score["matched_skills"],
                "missing_skills": job_score["missing_skills"]
            })
        
        # 按匹配度排序
        job_match_scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 计算统计数据
        if job_match_scores:
            avg_match_score = sum(j["match_score"] for j in job_match_scores) / len(job_match_scores)
            max_match_score = job_match_scores[0]["match_score"]
            min_match_score = job_match_scores[-1]["match_score"]
            top_matched_jobs = job_match_scores[:10]  # 取前10个
        else:
            avg_match_score = 0.0
            max_match_score = 0.0
            min_match_score = 0.0
            top_matched_jobs = []
        
        logger.info(f"匹配度计算完成: avg={avg_match_score:.1f}, max={max_match_score:.1f}, min={min_match_score:.1f}")
        
        # 6. 生成 Markdown 报告
        try:
            logger.info("开始生成 Markdown 报告")
            report = await ai_analysis_service.generate_markdown_report(
                task.keyword, aggregated, suggestions, avg_match_score
            )
            logger.info("Markdown 报告生成完成")
        except Exception as e:
            logger.error(f"生成 Markdown 报告失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # 7. 保存分析结果到数据库
        try:
            # 检查是否已存在该任务的分析结果
            existing_batch = self.db.query(BatchAnalysis).filter(
                BatchAnalysis.crawl_task_id == task_id
            ).first()
            
            if existing_batch:
                # 如果已存在，更新现有记录
                logger.info(f"更新已存在的分析结果: batch_id={existing_batch.batch_id}")
                existing_batch.resume_id = resume_id
                existing_batch.total_jobs = aggregated.total_jobs
                existing_batch.analyzed_jobs = len(jobs)
                existing_batch.avg_match_score = avg_match_score
                existing_batch.max_match_score = max_match_score
                existing_batch.min_match_score = min_match_score
                existing_batch.top_matched_jobs_json = top_matched_jobs
                existing_batch.common_missing_skills_json = self._extract_missing_skills(resume, aggregated)
                existing_batch.common_suggestions_json = [s.dict() for s in suggestions]
                existing_batch.status = "completed"
                existing_batch.progress = 100
                existing_batch.completed_at = datetime.now()
                
                self.db.commit()
                self.db.refresh(existing_batch)
                
                logger.info(f"批量分析更新完成: batch_id={existing_batch.batch_id}")
                batch_id = existing_batch.batch_id
            else:
                # 如果不存在，创建新记录
                batch_analysis = BatchAnalysis(
                    resume_id=resume_id,
                    crawl_task_id=task_id,
                    user_id=task.user_id,
                    total_jobs=aggregated.total_jobs,
                    analyzed_jobs=len(jobs),
                    avg_match_score=avg_match_score,
                    max_match_score=max_match_score,
                    min_match_score=min_match_score,
                    top_matched_jobs_json=top_matched_jobs,
                    common_missing_skills_json=self._extract_missing_skills(resume, aggregated),
                    common_suggestions_json=[s.dict() for s in suggestions],
                    status="completed",
                    progress=100,
                    started_at=datetime.now(),
                    completed_at=datetime.now()
                )
                
                self.db.add(batch_analysis)
                self.db.commit()
                self.db.refresh(batch_analysis)
                
                logger.info(f"批量分析完成: batch_id={batch_analysis.batch_id}")
                batch_id = batch_analysis.batch_id
                
        except Exception as e:
            logger.error(f"保存分析结果到数据库失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.db.rollback()
            raise
        
        return BatchAnalysisResult(
            task_id=task_id,
            aggregated_analysis=aggregated,
            resume_match_score=avg_match_score,
            priority_suggestions=suggestions,
            report_markdown=report
        )
    
    def _parse_resume_from_db(self, resume_db: Resume) -> ResumeSchema:
        """
        从数据库模型解析为 Pydantic 模型
        
        Args:
            resume_db: 数据库简历模型
            
        Returns:
            Pydantic 简历模型
        """
        def safe_json_loads(json_data, default=[]):
            """安全地解析 JSON 数据（兼容 JSONB 和 Text 字段）"""
            if not json_data:
                return default
            
            # 如果已经是 list 或 dict（PostgreSQL JSONB 返回的），直接返回
            if isinstance(json_data, (list, dict)):
                return json_data
            
            # 如果是字符串，尝试解析
            if isinstance(json_data, str):
                try:
                    result = json.loads(json_data)
                    return result if result is not None else default
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"JSON 字符串解析失败: {e}, 使用默认值")
                    return default
            
            # 其他类型，返回默认值
            logger.warning(f"未知的 JSON 数据类型: {type(json_data)}, 使用默认值")
            return default
        
        return ResumeSchema(
            name=resume_db.name or "",
            email=resume_db.email or "",
            phone=resume_db.phone or "",
            target_position=resume_db.target_position or "",
            education=safe_json_loads(resume_db.education_json, []),
            skills=safe_json_loads(resume_db.skills_json, []),
            projects=safe_json_loads(resume_db.projects_json, []),
            work_experience=safe_json_loads(resume_db.work_experience_json, []),
            certifications=safe_json_loads(resume_db.certifications_json, []),
            awards=safe_json_loads(resume_db.awards_json, [])
        )
    
    def _calculate_job_match_score(
        self, 
        resume: ResumeSchema, 
        job: BossJobInfo,
        market_top_skills: List[Tuple[str, int]]
    ) -> Dict[str, Any]:
        """
        计算简历与单个职位的匹配度
        
        Args:
            resume: 简历数据
            job: 职位信息
            market_top_skills: 市场高频技能列表
            
        Returns:
            包含匹配度、匹配技能、缺失技能的字典
        """
        # 简历技能（小写）
        resume_skills = set([skill.lower() for skill in resume.skills])
        
        # 从职位描述中提取技能要求
        job_text = f"{job.job_name} {job.job_description or ''} {' '.join(job.job_tags)}"
        job_text_lower = job_text.lower()
        
        # 使用市场高频技能作为参考
        market_skills = [skill for skill, _ in market_top_skills]
        
        # 提取职位要求的技能（在职位描述中出现的市场技能）
        required_skills = set()
        for skill in market_skills:
            if skill.lower() in job_text_lower:
                required_skills.add(skill.lower())
        
        # 如果没有提取到技能，使用市场 Top 5 技能作为默认
        if not required_skills and market_skills:
            required_skills = set([skill.lower() for skill in market_skills[:5]])
        
        # 计算匹配的技能和缺失的技能
        matched_skills = list(resume_skills & required_skills)
        missing_skills = list(required_skills - resume_skills)
        
        # 计算匹配度
        if not required_skills:
            skill_match_ratio = 0.5  # 默认50%
        else:
            skill_match_ratio = len(matched_skills) / len(required_skills)
        
        # 基础分数：技能匹配度 * 60
        base_score = skill_match_ratio * 60
        
        # 加分项：项目经历（最多 +20 分）
        project_score = min(len(resume.projects) * 5, 20)
        
        # 加分项：工作经历（最多 +20 分）
        experience_score = min(len(resume.work_experience) * 10, 20)
        
        total_score = min(base_score + project_score + experience_score, 100.0)
        
        return {
            "score": round(total_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
    
    def _calculate_match_score(self, resume: ResumeSchema, aggregated: AggregatedJDAnalysis) -> float:
        """
        计算简历匹配度
        
        Args:
            resume: 简历数据
            aggregated: 聚合分析结果
            
        Returns:
            匹配度评分 (0-100)
        """
        # 简单版本：基于技能匹配
        resume_skills = set([skill.lower() for skill in resume.skills])
        required_skills = set([skill.lower() for skill, _ in aggregated.top_skills])
        
        logger.info(f"计算匹配度: resume_skills={len(resume_skills)}, required_skills={len(required_skills)}")
        logger.info(f"简历技能: {list(resume_skills)[:10]}")  # 只显示前10个
        logger.info(f"职位要求技能: {list(required_skills)[:10]}")  # 只显示前10个
        
        if not required_skills:
            logger.warning("职位要求技能为空，返回默认分数 50.0")
            return 50.0  # 默认分数
        
        matched_count = len(resume_skills & required_skills)
        match_ratio = matched_count / len(required_skills)
        
        logger.info(f"匹配的技能数: {matched_count}, 匹配比例: {match_ratio:.2f}")
        
        # 基础分数：技能匹配度 * 60
        base_score = match_ratio * 60
        
        # 加分项：项目经历（最多 +20 分）
        project_score = min(len(resume.projects) * 5, 20)
        
        # 加分项：工作经历（最多 +20 分）
        experience_score = min(len(resume.work_experience) * 10, 20)
        
        total_score = base_score + project_score + experience_score
        
        logger.info(f"匹配度计算完成: base_score={base_score:.1f}, project_score={project_score}, experience_score={experience_score}, total={total_score:.1f}")
        
        return min(total_score, 100.0)
    
    def _extract_missing_skills(self, resume: ResumeSchema, aggregated: AggregatedJDAnalysis) -> List[str]:
        """
        提取缺失的技能
        
        Args:
            resume: 简历数据
            aggregated: 聚合分析结果
            
        Returns:
            缺失技能列表
        """
        resume_skills = set([skill.lower() for skill in resume.skills])
        required_skills = [skill for skill, _ in aggregated.top_skills]
        
        missing = []
        for skill in required_skills:
            if skill.lower() not in resume_skills:
                missing.append(skill)
        
        return missing
    
    def get_batch_analysis(self, task_id: str) -> Optional[BatchAnalysisResult]:
        """
        获取批量分析结果
        
        Args:
            task_id: 任务UUID
            
        Returns:
            批量分析结果，如果不存在返回 None
        """
        batch = self.db.query(BatchAnalysis).filter(
            BatchAnalysis.crawl_task_id == task_id
        ).first()
        
        if not batch:
            return None
        
        # 获取任务信息
        task = self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if not task:
            return None
        
        # 获取职位数据用于重建聚合分析
        jobs = self.get_task_jobs(task_id)
        
        # 从数据库中的 JSONB 字段获取数据（PostgreSQL 自动返回 Python 对象）
        missing_skills = batch.common_missing_skills_json if batch.common_missing_skills_json else []
        
        # 重新计算 aggregated 数据（使用 AI 服务的方法）
        from app.services.ai_analysis_service import AIAnalysisService
        ai_service = AIAnalysisService()
        
        # 提取 top_skills
        top_skills = ai_service._extract_top_skills(jobs, top_n=10)
        
        # 计算学历分布
        education_dist = ai_service._calculate_education_distribution(jobs)
        
        # 计算经验分布
        experience_dist = ai_service._calculate_experience_distribution(jobs)
        
        # 计算薪资统计
        salary_stats = ai_service._calculate_salary_stats(jobs)
        
        # 重建 AggregatedJDAnalysis
        aggregated = AggregatedJDAnalysis(
            total_jobs=batch.total_jobs,
            top_skills=top_skills,
            education_distribution=education_dist,
            experience_distribution=experience_dist,
            salary_stats=salary_stats,
            common_requirements=[],  # 从数据库无法恢复，留空
            common_responsibilities=[]  # 从数据库无法恢复，留空
        )
        
        # 解析建议（JSONB 字段已经是 Python list）
        suggestions = []
        if batch.common_suggestions_json:
            try:
                suggestions_data = batch.common_suggestions_json
                # 如果是字符串，需要解析；如果已经是 list，直接使用
                if isinstance(suggestions_data, str):
                    suggestions_data = json.loads(suggestions_data)
                
                for item in suggestions_data:
                    suggestions.append(EnhancementSuggestion(
                        priority=item.get("priority", 3),
                        category=item.get("category", "general"),
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        example=item.get("example")
                    ))
            except Exception as e:
                logger.error(f"解析建议失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 生成完整的 Markdown 报告（使用重新计算的 aggregated 数据）
        report = f"""# 📊 批量职位分析报告

## 🎯 分析概览

- **目标职位**：{task.keyword}
- **分析职位数**：{batch.total_jobs} 个
- **简历匹配度**：{batch.avg_match_score:.1f}/100
- **分析时间**：{batch.completed_at.strftime('%Y-%m-%d %H:%M:%S') if batch.completed_at else '未知'}

---

## 💼 市场需求分析

### 1. 高频技能要求（Top 10）

"""
        
        for i, (skill, count) in enumerate(aggregated.top_skills, 1):
            percentage = (count / aggregated.total_jobs) * 100 if aggregated.total_jobs > 0 else 0
            report += f"{i}. **{skill}** - 出现 {count} 次（{percentage:.1f}%）\n"
        
        report += f"""

### 2. 学历要求分布

"""
        
        for edu, count in aggregated.education_distribution.items():
            percentage = (count / aggregated.total_jobs) * 100 if aggregated.total_jobs > 0 else 0
            report += f"- {edu}：{count} 个职位（{percentage:.1f}%）\n"
        
        report += f"""

### 3. 工作经验要求分布

"""
        
        for exp, count in aggregated.experience_distribution.items():
            percentage = (count / aggregated.total_jobs) * 100 if aggregated.total_jobs > 0 else 0
            report += f"- {exp}：{count} 个职位（{percentage:.1f}%）\n"
        
        salary_stats = aggregated.salary_stats
        report += f"""

### 4. 薪资范围统计

- **最低薪资**：{salary_stats.get('min', 0)}K/月
- **最高薪资**：{salary_stats.get('max', 0)}K/月
- **平均薪资**：{salary_stats.get('avg', 0)}K/月
- **中位数薪资**：{salary_stats.get('median', 0)}K/月
- **有效样本数**：{salary_stats.get('count', 0)} 个

---

## 💡 缺失的关键技能

"""
        
        for i, skill in enumerate(missing_skills, 1):
            report += f"{i}. {skill}\n"
        
        report += f"""

---

## 🚀 简历优化建议

"""
        
        for i, suggestion in enumerate(suggestions, 1):
            # 限制优先级在 1-5 范围内
            priority = max(1, min(5, suggestion.priority))
            report += f"### {i}. {suggestion.title}\n\n"
            report += f"**类别**：{suggestion.category}\n\n"
            report += f"**优先级**：{'🔴' * priority}{'⚪' * (5 - priority)}\n\n"
            report += f"{suggestion.description}\n\n"
            if suggestion.example:
                report += f"**示例**：\n```\n{suggestion.example}\n```\n\n"
            report += "---\n\n"
        
        return BatchAnalysisResult(
            task_id=task_id,
            aggregated_analysis=aggregated,
            resume_match_score=batch.avg_match_score,
            priority_suggestions=suggestions,
            report_markdown=report
        )
    
    def get_task_history(self, user_id: int, status_filter: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户的历史爬取任务列表
        
        Args:
            user_id: 用户ID
            status_filter: 状态过滤（可选）
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        query = self.db.query(CrawlTask).filter(CrawlTask.user_id == user_id)
        
        # 状态过滤
        if status_filter:
            query = query.filter(CrawlTask.status == status_filter)
        
        # 按创建时间倒序
        tasks = query.order_by(CrawlTask.created_at.desc()).limit(limit).all()
        
        result = []
        for task in tasks:
            result.append({
                "task_id": task.task_id,
                "keyword": task.keyword,
                "city": task.city,
                "status": task.status,
                "progress": task.progress,
                "total_jobs": task.total_jobs,
                "crawled_jobs": task.crawled_jobs,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
        
        return result
    
    def get_analysis_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户的历史分析报告列表
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            分析报告列表
        """
        # 联表查询：batch_analyses + crawl_tasks
        query = self.db.query(BatchAnalysis, CrawlTask).join(
            CrawlTask, BatchAnalysis.crawl_task_id == CrawlTask.task_id
        ).filter(
            CrawlTask.user_id == user_id
        ).order_by(
            BatchAnalysis.created_at.desc()
        ).limit(limit)
        
        results = []
        for batch, task in query.all():
            results.append({
                "batch_id": batch.batch_id,
                "task_id": task.task_id,
                "keyword": task.keyword,
                "city": task.city,
                "total_jobs": batch.total_jobs,
                "analyzed_jobs": batch.analyzed_jobs,
                "match_score": batch.avg_match_score,
                "status": batch.status,
                "created_at": batch.created_at.isoformat() if batch.created_at else None,
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None
            })
        
        return results
