"""
数据库服务层
提供 CRUD 操作
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import json
import uuid

from app.models.database import (
    User, Resume, JobDescriptionDB, MatchAnalysisDB,
    SystemLog, UserStatistics, ResumeVersionDB, ResumeChatHistoryDB,
    CrawlTask, BatchAnalysis,
)
from app.models.schemas import (
    Resume as ResumeSchema,
    JobDescription as JDSchema,
    MatchAnalysis as MatchAnalysisSchema,
    EnhancementSuggestion
)


class DatabaseService:
    """数据库服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ 用户相关 ============
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # 创建用户统计
        stats = UserStatistics(user_id=user.id)
        self.db.add(stats)
        self.db.commit()
        
        return user
    
    def update_user_activity(self, user_id: int):
        """更新用户最后活动时间"""
        stats = self.db.query(UserStatistics).filter(
            UserStatistics.user_id == user_id
        ).first()
        if stats:
            stats.last_activity_at = datetime.now()
            self.db.commit()
    
    # ============ 简历相关 ============
    
    def save_resume(
        self, 
        resume_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        user_id: Optional[int] = None
    ) -> Resume:
        """保存简历（上传阶段）"""
        resume = Resume(
            resume_id=resume_id,
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            file_type=file_type,
            parsed=False
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        
        # 更新统计
        if user_id:
            self._increment_user_stat(user_id, 'total_resumes')
        
        return resume
    
    def update_resume_parsed(
        self,
        resume_id: str,
        resume_data: ResumeSchema,
        raw_text: str,
        markdown_text: str
    ) -> Resume:
        """更新简历解析结果"""
        resume = self.db.query(Resume).filter(Resume.resume_id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        
        # 更新基本信息
        resume.name = resume_data.name
        resume.email = resume_data.email
        resume.phone = resume_data.phone
        resume.target_position = resume_data.target_position
        
        # 更新文本
        resume.raw_text = raw_text
        resume.markdown_text = markdown_text
        
        # 更新结构化数据（JSONB 字段，PostgreSQL 自动处理）
        resume.education_json = [edu.dict() for edu in resume_data.education]
        resume.skills_json = resume_data.skills
        resume.projects_json = [proj.dict() for proj in resume_data.projects]
        resume.work_experience_json = [exp.dict() for exp in resume_data.work_experience]
        resume.certifications_json = resume_data.certifications
        resume.awards_json = resume_data.awards
        
        resume.parsed = True
        resume.parse_error = None
        
        self.db.commit()
        self.db.refresh(resume)
        return resume
    
    def get_resume(self, resume_id: str) -> Optional[Resume]:
        """获取简历（resume_id 支持 str / UUID）"""
        from app.utils.ids import as_str_id
        rid = as_str_id(resume_id)
        return self.db.query(Resume).filter(Resume.resume_id == rid).first()
    
    def get_user_resumes(self, user_id: int, limit: int = 20) -> List[Resume]:
        """获取用户的所有简历"""
        return self.db.query(Resume).filter(
            Resume.user_id == user_id
        ).order_by(desc(Resume.created_at)).limit(limit).all()
    
    # ============ JD 相关 ============
    
    def save_jd(
        self,
        jd_id: str,
        raw_text: str,
        user_id: Optional[int] = None
    ) -> JobDescriptionDB:
        """保存 JD（输入阶段）"""
        jd = JobDescriptionDB(
            jd_id=jd_id,
            user_id=user_id,
            raw_text=raw_text,
            parsed=False
        )
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        
        # 更新统计
        if user_id:
            self._increment_user_stat(user_id, 'total_jds')
        
        return jd
    
    def update_jd_parsed(
        self,
        jd_id: str,
        jd_data: JDSchema,
        keywords: List[str]
    ) -> JobDescriptionDB:
        """更新 JD 解析结果"""
        jd = self.db.query(JobDescriptionDB).filter(JobDescriptionDB.jd_id == jd_id).first()
        if not jd:
            raise ValueError(f"JD {jd_id} not found")
        
        # 更新结构化数据（JSONB 字段，PostgreSQL 自动处理）
        jd.required_skills = jd_data.required_skills
        jd.preferred_skills = jd_data.preferred_skills
        jd.responsibilities = jd_data.responsibilities
        jd.requirements = jd_data.requirements
        jd.keywords = keywords
        
        jd.parsed = True
        jd.parse_error = None
        
        self.db.commit()
        self.db.refresh(jd)
        return jd
    
    def get_jd(self, jd_id: str) -> Optional[JobDescriptionDB]:
        """获取 JD"""
        return self.db.query(JobDescriptionDB).filter(JobDescriptionDB.jd_id == jd_id).first()
    
    def get_user_jds(self, user_id: int, limit: int = 20) -> List[JobDescriptionDB]:
        """获取用户的所有 JD"""
        return self.db.query(JobDescriptionDB).filter(
            JobDescriptionDB.user_id == user_id
        ).order_by(desc(JobDescriptionDB.created_at)).limit(limit).all()
    
    # ============ 匹配分析相关 ============
    
    def save_match_analysis(
        self,
        match_id: str,
        resume_id: str,
        jd_id: str,
        analysis: MatchAnalysisSchema,
        enhancements: List[EnhancementSuggestion],
        report_markdown: str,
        user_id: Optional[int] = None
    ) -> MatchAnalysisDB:
        """保存匹配分析结果"""
        match = MatchAnalysisDB(
            match_id=match_id,
            resume_id=resume_id,
            jd_id=jd_id,
            user_id=user_id,
            overall_score=analysis.overall_score,
            skill_match_score=analysis.skill_match_score,
            experience_match_score=analysis.experience_match_score,
            education_match_score=analysis.education_match_score,
            matched_skills=analysis.matched_skills,
            missing_skills=analysis.missing_skills,
            strengths=analysis.strengths,  # 添加 strengths
            weaknesses=analysis.weaknesses,  # 添加 weaknesses
            suggestions=[enh.dict() for enh in enhancements],
            analysis_report=report_markdown
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        
        # 更新统计
        if user_id:
            self._increment_user_stat(user_id, 'total_matches')
        
        return match
    
    def get_match_analysis(self, match_id: str) -> Optional[MatchAnalysisDB]:
        """获取匹配分析"""
        return self.db.query(MatchAnalysisDB).options(
            joinedload(MatchAnalysisDB.resume),
            joinedload(MatchAnalysisDB.job_description)
        ).filter(MatchAnalysisDB.match_id == match_id).first()
    
    def get_user_matches(self, user_id: int, limit: int = 20) -> List[MatchAnalysisDB]:
        """获取用户的所有匹配分析"""
        return self.db.query(MatchAnalysisDB).options(
            joinedload(MatchAnalysisDB.resume),
            joinedload(MatchAnalysisDB.job_description)
        ).filter(
            MatchAnalysisDB.user_id == user_id
        ).order_by(desc(MatchAnalysisDB.created_at)).limit(limit).all()
    
    def get_resume_matches(
        self,
        resume_id: str,
        user_id: int,
        limit: int = 50,
    ) -> List[MatchAnalysisDB]:
        """获取某个简历的 JD 匹配分析（通过 resume 归属校验用户）"""
        return (
            self.db.query(MatchAnalysisDB)
            .options(
                joinedload(MatchAnalysisDB.job_description),
                joinedload(MatchAnalysisDB.resume),
            )
            .join(Resume, MatchAnalysisDB.resume_id == Resume.resume_id)
            .filter(
                MatchAnalysisDB.resume_id == resume_id,
                Resume.user_id == user_id,
            )
            .order_by(desc(MatchAnalysisDB.created_at))
            .limit(limit)
            .all()
        )

    def get_resume_batch_analyses(
        self,
        resume_id: str,
        user_id: int,
        limit: int = 20,
    ) -> List[BatchAnalysis]:
        """获取某个简历的批量分析（通过 resume 归属校验用户）"""
        return (
            self.db.query(BatchAnalysis)
            .options(joinedload(BatchAnalysis.crawl_task))
            .join(Resume, BatchAnalysis.resume_id == Resume.resume_id)
            .filter(
                BatchAnalysis.resume_id == resume_id,
                Resume.user_id == user_id,
            )
            .order_by(desc(BatchAnalysis.created_at))
            .limit(limit)
            .all()
        )

    def get_user_batch_analyses(
        self,
        user_id: int,
        limit: int = 30,
    ) -> List[BatchAnalysis]:
        """获取用户全部批量分析（用于无 resume 关联时的回退）"""
        return (
            self.db.query(BatchAnalysis)
            .options(joinedload(BatchAnalysis.crawl_task))
            .join(Resume, BatchAnalysis.resume_id == Resume.resume_id)
            .filter(Resume.user_id == user_id)
            .order_by(desc(BatchAnalysis.created_at))
            .limit(limit)
            .all()
        )

    # ============ 简历优化相关 ============

    def update_resume_markdown(
        self,
        resume_id: str,
        markdown_text: str,
    ) -> Optional[Resume]:
        """更新简历 Markdown 内容"""
        resume = self.get_resume(resume_id)
        if not resume:
            return None
        resume.markdown_text = markdown_text
        resume.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_resume_versions(
        self,
        resume_id: str,
        user_id: int,
        limit: int = 30,
    ) -> List[ResumeVersionDB]:
        """获取简历版本列表"""
        return (
            self.db.query(ResumeVersionDB)
            .filter(
                ResumeVersionDB.resume_id == resume_id,
                ResumeVersionDB.user_id == user_id,
            )
            .order_by(desc(ResumeVersionDB.created_at))
            .limit(limit)
            .all()
        )

    def get_resume_version(
        self,
        version_id: str,
        user_id: int,
    ) -> Optional[ResumeVersionDB]:
        """获取单个版本"""
        return (
            self.db.query(ResumeVersionDB)
            .filter(
                ResumeVersionDB.version_id == version_id,
                ResumeVersionDB.user_id == user_id,
            )
            .first()
        )

    def create_resume_version(
        self,
        resume_id: str,
        user_id: int,
        content: str,
        description: Optional[str] = None,
    ) -> ResumeVersionDB:
        """创建简历版本快照"""
        version = ResumeVersionDB(
            version_id=str(uuid.uuid4()),
            resume_id=resume_id,
            user_id=user_id,
            content=content,
            description=description,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_resume_chat_history(
        self,
        resume_id: str,
        user_id: int,
        limit: int = 10,
    ) -> List[ResumeChatHistoryDB]:
        """获取简历对话历史（默认最近 5 轮 = 10 条消息）"""
        messages = (
            self.db.query(ResumeChatHistoryDB)
            .filter(
                ResumeChatHistoryDB.resume_id == resume_id,
                ResumeChatHistoryDB.user_id == user_id,
            )
            .order_by(desc(ResumeChatHistoryDB.created_at))
            .limit(limit)
            .all()
        )
        return list(reversed(messages))

    def save_chat_message(
        self,
        resume_id: str,
        user_id: int,
        role: str,
        content: str,
        modified_section: Optional[str] = None,
        section_type: Optional[str] = None,
        explanation: Optional[str] = None,
    ) -> ResumeChatHistoryDB:
        """保存对话消息"""
        message = ResumeChatHistoryDB(
            chat_id=str(uuid.uuid4()),
            resume_id=resume_id,
            user_id=user_id,
            role=role,
            content=content,
            modified_section=modified_section,
            section_type=section_type,
            explanation=explanation,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_crawl_task(self, task_id: str) -> Optional[CrawlTask]:
        """获取爬取任务"""
        return self.db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()

    def get_batch_analysis_by_task(self, task_id: str) -> Optional[BatchAnalysis]:
        """根据爬取任务 ID 获取批量分析"""
        return (
            self.db.query(BatchAnalysis)
            .filter(BatchAnalysis.crawl_task_id == task_id)
            .first()
        )

    # ============ 系统日志 ============
    
    def log_action(
        self,
        action: str,
        status: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """记录系统日志"""
        log = SystemLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            error_message=error_message,
            execution_time=execution_time
        )
        self.db.add(log)
        self.db.commit()
    
    # ============ 统计相关 ============
    
    def get_user_statistics(self, user_id: int) -> Optional[UserStatistics]:
        """获取用户统计"""
        return self.db.query(UserStatistics).filter(
            UserStatistics.user_id == user_id
        ).first()
    
    def _increment_user_stat(self, user_id: int, field: str):
        """增加用户统计计数"""
        stats = self.db.query(UserStatistics).filter(
            UserStatistics.user_id == user_id
        ).first()
        if stats:
            current_value = getattr(stats, field, 0)
            setattr(stats, field, current_value + 1)
            stats.last_activity_at = datetime.now()
            self.db.commit()
