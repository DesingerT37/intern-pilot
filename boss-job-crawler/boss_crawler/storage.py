"""In-memory job storage with deduplication support."""

from __future__ import annotations

import logging

from .models import JobInfo

logger = logging.getLogger(__name__)


class DataStorage:
    """Store parsed jobs for a single crawl session."""

    def __init__(self, enable_deduplication: bool = True) -> None:
        self.enable_deduplication = enable_deduplication
        self._jobs: list[JobInfo] = []
        self._dedup_keys: set[str] = set()

    def add_job(self, job_info: JobInfo) -> bool:
        """添加职位，返回是否成功添加（False 表示重复）。"""
        key = job_info.build_dedup_key()
        if self.enable_deduplication and key in self._dedup_keys:
            logger.debug(
                f"去重：跳过重复职位 - {job_info.job_name} @ {job_info.company_name} "
                f"(去重键: {key})"
            )
            return False

        self._jobs.append(job_info)
        self._dedup_keys.add(key)
        logger.debug(
            f"添加职位：{job_info.job_name} @ {job_info.company_name} "
            f"(去重键: {key})"
        )
        return True

    def add_jobs_batch(self, jobs: list[JobInfo]) -> int:
        """批量添加职位，返回实际添加的数量。"""
        added = 0
        skipped = 0
        for job in jobs:
            if self.add_job(job):
                added += 1
            else:
                skipped += 1
        
        if skipped > 0:
            logger.info(f"批量添加完成：添加 {added} 个，跳过重复 {skipped} 个")
        
        return added

    def get_all_jobs(self) -> list[JobInfo]:
        return list(self._jobs)

    def get_job_count(self) -> int:
        return len(self._jobs)

    def clear(self) -> None:
        self._jobs.clear()
        self._dedup_keys.clear()
