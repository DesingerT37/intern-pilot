"""核心数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class JobInfo:
    """单个职位信息。"""

    job_name: str
    company_name: str
    location: str
    education: str = ""
    experience: str = ""
    salary_range: str = ""
    job_tags: list[str] = field(default_factory=list)
    job_description: str = ""
    recruiter_name: str = ""
    recruiter_position: str = ""
    company_industry: str = ""
    company_scale: str = ""
    job_id: str | None = None
    crawl_time: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def build_dedup_key(self) -> str:
        """生成职位去重键。
        
        优先使用 job_id（最准确）。
        如果没有 job_id，使用 公司名称::职位名称::地点 组合。
        """
        if self.job_id and self.job_id.strip():
            return f"id::{self.job_id.strip()}"
        
        # 回退方案：使用公司+职位+地点组合
        # 注意：这个组合包含了公司名称，所以不同公司的同名职位不会被去重
        return "::".join(
            [
                self.company_name.strip(),
                self.job_name.strip(),
                self.location.strip(),
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为导出友好的字典。"""
        return {
            "岗位名称": self.job_name,
            "公司名称": self.company_name,
            "工作地点": self.location,
            "学历要求": self.education,
            "工作经验": self.experience,
            "薪资范围": self.salary_range,
            "职位标签": ", ".join(self.job_tags),
            "职位描述": self.job_description,
            "招聘人姓名": self.recruiter_name,
            "招聘人职位": self.recruiter_position,
            "公司行业": self.company_industry,
            "公司规模": self.company_scale,
            "职位ID": self.job_id or "",
            "抓取时间": self.crawl_time,
        }


@dataclass
class CrawlResult:
    """单次抓取结果。"""

    success: bool
    total_jobs: int = 0
    unique_jobs: int = 0
    pages_crawled: int = 0
    output_file: str | None = None
    error_message: str | None = None
    crawl_duration: float = 0.0


@dataclass
class LoginStatus:
    """登录状态快照。"""

    is_logged_in: bool
    username: str | None = None
    message: str = ""
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
