"""
Pydantic 数据模型定义
用于 API 请求/响应和 LLM 结构化输出
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ 简历相关模型 ============

class Education(BaseModel):
    """教育背景"""
    school: Optional[str] = Field(None, description="学校名称")
    degree: Optional[str] = Field(None, description="学位：本科/硕士/博士")
    major: Optional[str] = Field(None, description="专业")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    gpa: Optional[float] = Field(None, description="GPA")


class Project(BaseModel):
    """项目经历"""
    name: Optional[str] = Field(None, description="项目名称")
    role: Optional[str] = Field(None, description="担任角色")
    tech_stack: List[str] = Field(default_factory=list, description="技术栈")
    description: Optional[str] = Field(None, description="项目描述")
    achievements: List[str] = Field(default_factory=list, description="项目成果")
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class WorkExperience(BaseModel):
    """工作/实习经历"""
    company: Optional[str] = Field(None, description="公司名称")
    position: Optional[str] = Field(None, description="职位")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    responsibilities: List[str] = Field(default_factory=list, description="工作职责")
    achievements: List[str] = Field(default_factory=list, description="工作成果")


class Resume(BaseModel):
    """简历结构化数据"""
    name: Optional[str] = Field(None, description="姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    target_position: Optional[str] = Field(None, description="目标职位")
    education: List[Education] = Field(default_factory=list, description="教育背景")
    skills: List[str] = Field(default_factory=list, description="技能清单")
    projects: List[Project] = Field(default_factory=list, description="项目经历")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="工作经历")
    certifications: List[str] = Field(default_factory=list, description="证书")
    awards: List[str] = Field(default_factory=list, description="获奖情况")


# ============ JD 相关模型 ============

class JobDescription(BaseModel):
    """
    职位描述结构化数据
    用于存储 AI 解析后的 JD 信息，用于简历匹配分析
    """
    required_skills: List[str] = Field(default_factory=list, description="必需技能列表")
    preferred_skills: List[str] = Field(default_factory=list, description="优先技能列表")
    responsibilities: List[str] = Field(default_factory=list, description="工作职责列表")
    requirements: List[str] = Field(default_factory=list, description="任职要求列表")
    keywords: List[str] = Field(default_factory=list, description="关键词列表（用于搜索和匹配）")


# ============ 匹配分析相关模型 ============

class MatchAnalysis(BaseModel):
    """匹配分析结果"""
    overall_score: float = Field(description="总体匹配度 (0-100)")
    skill_match_score: Optional[float] = Field(None, description="技能匹配度")
    experience_match_score: Optional[float] = Field(None, description="经验匹配度")
    education_match_score: Optional[float] = Field(None, description="学历匹配度")
    matched_skills: List[str] = Field(description="匹配的技能列表")
    missing_skills: List[str] = Field(description="缺失的技能列表")
    strengths: List[str] = Field(default_factory=list, description="候选人优势列表")
    weaknesses: List[str] = Field(default_factory=list, description="候选人劣势列表")
    suggestions: List[str] = Field(description="优化建议列表")


class EnhancementSuggestion(BaseModel):
    """简历增强建议"""
    priority: int = Field(description="优先级 (1-5)")
    category: str = Field(description="类别：技能/项目/描述/格式")
    title: str = Field(description="建议标题")
    description: str = Field(description="详细说明")
    example: Optional[str] = Field(None, description="示例")


# ============ API 请求/响应模型 ============

class ResumeUploadResponse(BaseModel):
    """简历上传响应"""
    resume_id: str
    filename: str
    file_size: int
    message: str


class ResumeParseResponse(BaseModel):
    """简历解析响应"""
    resume_id: str
    resume_data: Resume
    raw_text: str
    message: str


class JDParseRequest(BaseModel):
    """JD 解析请求"""
    jd_text: str = Field(description="岗位需求文本")


class JDParseResponse(BaseModel):
    """JD 解析响应"""
    jd_id: str
    jd_data: JobDescription
    keywords: List[str]
    message: str


class MatchRequest(BaseModel):
    """匹配分析请求"""
    resume_id: str
    jd_id: str


class MatchResponse(BaseModel):
    """匹配分析响应"""
    match_id: str
    analysis: MatchAnalysis
    enhancements: List[EnhancementSuggestion]
    report_markdown: str
    message: str


# ============ 通用响应模型 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """成功响应"""
    message: str
    data: Optional[dict] = None


# ============ 批量分析相关模型 ============

class CrawlTaskRequest(BaseModel):
    """爬取任务请求"""
    resume_id: Optional[str] = Field(None, description="简历ID（可选）")
    keyword: str = Field(description="职位关键词，如'Python后端'")
    city: str = Field(default="全国", description="城市")
    pages: int = Field(default=3, ge=1, le=10, description="抓取页数")
    fetch_details: bool = Field(default=True, description="是否抓取职位详情")


class CrawlProgress(BaseModel):
    """爬取进度"""
    task_id: str  # UUID
    status: str  # pending/running/completed/failed/stopped
    current_page: int = 0
    total_pages: int
    jobs_found: int = 0
    unique_jobs: int = 0
    message: str
    progress_percentage: float = 0.0


class BossJobInfo(BaseModel):
    """BOSS 职位信息"""
    job_id: Optional[str] = None
    job_name: str
    company_name: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    job_description: Optional[str] = None
    job_tags: List[str] = Field(default_factory=list)


class AggregatedJDAnalysis(BaseModel):
    """聚合的 JD 分析"""
    total_jobs: int
    top_skills: List[tuple[str, int]] = Field(description="(技能, 出现次数)")
    education_distribution: Dict[str, int] = Field(description="学历分布")
    experience_distribution: Dict[str, int] = Field(description="经验分布")
    salary_stats: Dict[str, Any] = Field(description="薪资统计")
    common_requirements: List[str] = Field(description="高频任职要求")
    common_responsibilities: List[str] = Field(description="高频工作职责")


class BatchAnalysisResult(BaseModel):
    """批量分析结果"""
    task_id: str  # UUID
    aggregated_analysis: AggregatedJDAnalysis
    resume_match_score: float = Field(description="简历匹配度 (0-100)")
    priority_suggestions: List[EnhancementSuggestion]
    report_markdown: str


class CrawlTaskResponse(BaseModel):
    """爬取任务响应"""
    task_id: str  # UUID
    message: str
    status: str


# ============ 简历优化 Agent 相关模型 ============

class ResumeChatMessage(BaseModel):
    """简历优化聊天消息"""
    role: str = Field(description="角色：user | assistant")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    modified_section: Optional[str] = Field(None, description="修改后的段落（Markdown）")
    section_type: Optional[str] = Field(None, description="段落类型：education/work_experience/projects/skills")
    explanation: Optional[str] = Field(None, description="修改说明")


class ResumeChatRequest(BaseModel):
    """简历优化聊天请求"""
    resume_id: str = Field(description="简历 ID")
    resume_content: str = Field(description="当前简历完整内容（Markdown）")
    message: str = Field(description="用户消息")
    context: List[ResumeChatMessage] = Field(default_factory=list, description="历史对话上下文（最近 5 轮）")
    suggestions: Optional[List[str]] = Field(None, description="参考建议列表")


class ResumeChatResponse(BaseModel):
    """简历优化聊天响应"""
    message: str = Field(description="AI 回复")
    modified_section: Optional[str] = Field(None, description="修改后的段落（Markdown）")
    section_type: Optional[str] = Field(None, description="段落类型：education/work_experience/projects/skills")
    explanation: Optional[str] = Field(None, description="修改说明")


class ResumeVersion(BaseModel):
    """简历版本"""
    version_id: str = Field(description="版本唯一标识（UUID）")
    resume_id: str = Field(description="简历 ID")
    content: str = Field(description="该版本的 Markdown 内容")
    description: Optional[str] = Field(None, description="版本说明（用户备注）")
    created_at: datetime = Field(description="创建时间")


class VersionCreateRequest(BaseModel):
    """版本创建请求"""
    description: Optional[str] = Field(None, description="版本说明")


class VersionResponse(BaseModel):
    """版本创建响应"""
    version_id: str = Field(description="版本 ID")
    resume_id: str = Field(description="简历 ID")
    content: str = Field(description="版本 Markdown 内容")
    description: Optional[str] = Field(None, description="版本说明")
    created_at: datetime = Field(description="创建时间")


class VersionListItem(BaseModel):
    """版本列表项（不含完整内容）"""
    version_id: str = Field(description="版本 ID")
    resume_id: str = Field(description="简历 ID")
    description: Optional[str] = Field(None, description="版本说明")
    created_at: datetime = Field(description="创建时间")
    content_preview: str = Field(description="内容预览")


class ResumeListItem(BaseModel):
    """简历列表项"""
    resume_id: str = Field(description="简历 ID")
    filename: str = Field(description="文件名")
    name: Optional[str] = Field(None, description="姓名")
    target_position: Optional[str] = Field(None, description="目标职位")
    parsed: bool = Field(description="是否已解析")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ResumeContentResponse(BaseModel):
    """简历内容响应"""
    resume_id: str = Field(description="简历 ID")
    markdown_text: str = Field(description="简历 Markdown 内容")
    name: Optional[str] = Field(None, description="姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    target_position: Optional[str] = Field(None, description="目标职位")
    updated_at: datetime = Field(description="更新时间")


class ResumeUpdateRequest(BaseModel):
    """简历更新请求"""
    markdown_text: str = Field(description="Markdown 内容")
    description: Optional[str] = Field(None, description="版本说明")


class ExportRequest(BaseModel):
    """导出请求"""
    resume_id: str = Field(description="简历 ID")
    markdown_content: str = Field(description="Markdown 内容")
    format: str = Field(description="导出格式：pdf | docx")
    style: Optional[str] = Field("default", description="样式模板：default/modern/classic")


class Suggestion(BaseModel):
    """优化建议"""
    priority: int = Field(description="优先级 (1-5，1 为最高)")
    category: str = Field(description="类别：skill/project/description/format")
    title: str = Field(description="建议标题")
    description: str = Field(description="详细说明")
    example: Optional[str] = Field(None, description="示例")


class MatchAnalysisListItem(BaseModel):
    """简历关联的匹配分析列表项"""
    source: str = Field(default="jd_match", description="来源：jd_match")
    match_id: str = Field(description="匹配分析 ID")
    resume_id: str = Field(description="简历 ID")
    overall_score: float = Field(description="总体匹配度 (0-100)")
    job_label: str = Field(description="职位/关键词展示名")
    suggestion_count: int = Field(default=0, description="优化建议条数")
    created_at: datetime = Field(description="创建时间")


class BatchAnalysisListItem(BaseModel):
    """简历关联的批量分析列表项"""
    source: str = Field(default="batch", description="来源：batch")
    task_id: str = Field(description="爬取任务 ID")
    batch_id: str = Field(description="批量分析 ID")
    resume_id: str = Field(description="简历 ID")
    keyword: str = Field(description="搜索关键词")
    total_jobs: int = Field(default=0, description="分析职位数")
    avg_match_score: Optional[float] = Field(None, description="平均匹配分")
    status: str = Field(description="分析状态")
    suggestion_count: int = Field(default=0, description="优化建议条数")
    created_at: datetime = Field(description="创建时间")


class MatchSuggestionResponse(BaseModel):
    """匹配建议响应"""
    match_id: str = Field(description="匹配分析 ID")
    job_name: str = Field(description="职位名称")
    company_name: str = Field(description="公司名称")
    overall_score: float = Field(description="总体匹配度 (0-100)")
    suggestions: List[Suggestion] = Field(description="优化建议列表")
    matched_skills: List[str] = Field(description="匹配的技能列表")
    missing_skills: List[str] = Field(description="缺失的技能列表")
    strengths: List[str] = Field(default_factory=list, description="候选人优势列表")
    weaknesses: List[str] = Field(default_factory=list, description="候选人劣势列表")


class BatchSuggestionResponse(BaseModel):
    """批量建议响应"""
    task_id: str = Field(description="批量分析任务 ID")
    keyword: str = Field(description="搜索关键词")
    total_jobs: int = Field(description="分析的职位总数")
    common_missing_skills: List[str] = Field(description="常见缺失技能列表")
    priority_suggestions: List[Suggestion] = Field(description="优先级建议列表")
    top_skills: List[tuple[str, int]] = Field(description="高频技能及其出现次数")
