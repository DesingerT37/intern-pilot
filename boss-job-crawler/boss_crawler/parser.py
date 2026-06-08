"""Job-data parser."""

from __future__ import annotations

from typing import Any

from .exceptions import ParseError
from .models import JobInfo


class DataParser:
    """Convert captured job-list payloads into structured job models."""

    JOB_LIST_PATHS = (
        ("zpData", "jobList"),
        ("data", "jobList"),
        ("jobList",),
        ("zpData", "data", "jobList"),
    )

    def parse_job_list(self, json_data: dict[str, Any]) -> list[JobInfo]:
        if not isinstance(json_data, dict):
            raise ParseError("job payload must be a dict")

        job_list = self._extract_job_list(json_data)
        parsed_jobs: list[JobInfo] = []

        for item in job_list:
            if not isinstance(item, dict):
                continue
            job = self.extract_job_info(item)
            if self.validate_job_info(job):
                parsed_jobs.append(job)

        return parsed_jobs

    def extract_job_info(self, item: dict[str, Any]) -> JobInfo:
        if not isinstance(item, dict):
            raise ParseError("job item must be a dict")

        location = self._build_location(item)
        labels = self._normalize_labels(item.get("jobLabels") or item.get("skills") or item.get("labels"))
        recruiter_name, recruiter_position = self._extract_recruiter(item)
        company_industry = self._first_non_empty(
            item.get("brandIndustry"),
            item.get("industryName"),
            item.get("brandIndustryName"),
        )
        company_scale = self._first_non_empty(
            item.get("brandScaleName"),
            item.get("brandStageName"),
            item.get("scaleName"),
        )
        description = self._first_non_empty(
            item.get("postDescription"),
            item.get("jobDescription"),
            item.get("description"),
        )

        return JobInfo(
            job_name=self._first_non_empty(item.get("jobName"), item.get("positionName")),
            company_name=self._first_non_empty(item.get("brandName"), item.get("companyName")),
            location=location,
            education=self._first_non_empty(item.get("jobDegree"), item.get("degreeName")),
            experience=self._first_non_empty(item.get("jobExperience"), item.get("experienceName")),
            salary_range=self._first_non_empty(item.get("salaryDesc"), item.get("salary")),
            job_tags=labels,
            job_description=description,
            recruiter_name=recruiter_name,
            recruiter_position=recruiter_position,
            company_industry=company_industry,
            company_scale=company_scale,
            job_id=self._first_non_empty(item.get("encryptJobId"), item.get("jobId"), item.get("securityId")),
        )

    def validate_job_info(self, job_info: JobInfo) -> bool:
        return bool(
            job_info.job_name.strip()
            and job_info.company_name.strip()
            and job_info.location.strip()
        )

    def _extract_job_list(self, json_data: dict[str, Any]) -> list[Any]:
        for path in self.JOB_LIST_PATHS:
            current: Any = json_data
            for key in path:
                if not isinstance(current, dict) or key not in current:
                    current = None
                    break
                current = current[key]
            if isinstance(current, list):
                return current

        raise ParseError("job list not found in payload")

    def _build_location(self, item: dict[str, Any]) -> str:
        direct = self._first_non_empty(item.get("locationName"), item.get("jobArea"))
        if direct:
            return direct

        parts = [
            self._first_non_empty(item.get("cityName")),
            self._first_non_empty(item.get("areaDistrict")),
            self._first_non_empty(item.get("businessDistrict")),
        ]
        return " / ".join([part for part in parts if part])

    def _extract_recruiter(self, item: dict[str, Any]) -> tuple[str, str]:
        recruiter = item.get("bossVO")
        if isinstance(recruiter, dict):
            return (
                self._first_non_empty(recruiter.get("name"), item.get("bossName")),
                self._first_non_empty(recruiter.get("title"), item.get("bossTitle")),
            )
        return (
            self._first_non_empty(item.get("bossName"), item.get("recruiterName")),
            self._first_non_empty(item.get("bossTitle"), item.get("recruiterTitle")),
        )

    @staticmethod
    def _normalize_labels(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return []

    @staticmethod
    def _first_non_empty(*values: Any) -> str:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return ""
