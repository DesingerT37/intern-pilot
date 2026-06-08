"""基于 HTML 解析的职位数据提取器。

当网络监听不可用时，直接从页面 HTML 中提取职位信息。
"""

from __future__ import annotations

import json
import re
from typing import Any

from .exceptions import ParseError


class HTMLParser:
    """从页面 HTML 中提取职位数据。"""

    def parse_job_list_from_html(self, html: str) -> list[dict[str, Any]]:
        """从 HTML 中提取职位列表。
        
        Args:
            html: 页面 HTML 内容
            
        Returns:
            职位列表
            
        Raises:
            ParseError: 解析失败
        """
        jobs = []
        
        # 方法1：尝试从 <script> 标签中提取 JSON 数据
        jobs_from_script = self._extract_from_script_tags(html)
        if jobs_from_script:
            return jobs_from_script
        
        # 方法2：尝试从 HTML 元素中提取
        jobs_from_elements = self._extract_from_html_elements(html)
        if jobs_from_elements:
            return jobs_from_elements
        
        raise ParseError("无法从页面 HTML 中提取职位数据")
    
    def _extract_from_script_tags(self, html: str) -> list[dict[str, Any]]:
        """从 script 标签中提取 JSON 数据。"""
        # BOSS 直聘通常会在页面中嵌入 JSON 数据
        # 查找包含 jobList 的 script 标签
        
        # 模式1：window.__INITIAL_STATE__ = {...}
        pattern1 = r'window\.__INITIAL_STATE__\s*=\s*({.+?});'
        matches = re.findall(pattern1, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                jobs = self._extract_jobs_from_json(data)
                if jobs:
                    return jobs
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 模式2：var jobList = [...]
        pattern2 = r'var\s+jobList\s*=\s*(\[.+?\]);'
        matches = re.findall(pattern2, html, re.DOTALL)
        for match in matches:
            try:
                jobs = json.loads(match)
                if isinstance(jobs, list) and jobs:
                    return [self._normalize_job(job) for job in jobs]
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 模式3：zpData = {...}
        pattern3 = r'zpData\s*=\s*({.+?});'
        matches = re.findall(pattern3, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                if "jobList" in data:
                    return [self._normalize_job(job) for job in data["jobList"]]
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 模式4：查找所有 <script> 标签中的 JSON
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
        for script_content in scripts:
            # 尝试查找 JSON 对象
            json_pattern = r'\{[^{}]*"jobList"[^{}]*:\s*\[[^\]]*\][^{}]*\}'
            json_matches = re.findall(json_pattern, script_content, re.DOTALL)
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if "jobList" in data and isinstance(data["jobList"], list):
                        return [self._normalize_job(job) for job in data["jobList"]]
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return []
    
    def _extract_from_html_elements(self, html: str) -> list[dict[str, Any]]:
        """从 HTML 元素中提取职位数据。"""
        jobs = []
        
        # 找到所有职位卡片的起始位置
        start_pattern = r'<li[^>]*class="[^"]*job-card[^"]*"[^>]*>'
        starts = [(m.start(), m.end()) for m in re.finditer(start_pattern, html)]
        
        if not starts:
            return []
        
        # 提取每个完整的卡片
        for start_pos, start_end in starts:
            try:
                # 手动匹配结束标签（处理嵌套的 <li>）
                depth = 1
                pos = start_end
                while pos < len(html) and depth > 0:
                    if html[pos:pos+3] == '<li':
                        depth += 1
                    elif html[pos:pos+5] == '</li>':
                        depth -= 1
                        if depth == 0:
                            pos += 5
                            break
                    pos += 1
                
                card_html = html[start_pos:pos]
                job = self._parse_job_card(card_html)
                if job:
                    jobs.append(job)
            except Exception:
                continue
        
        return jobs
    
    def _parse_job_card(self, card_html: str) -> dict[str, Any] | None:
        """解析单个职位卡片。"""
        job = {}
        
        # 提取职位名称 - 尝试多种模式
        job_name_patterns = [
            r'class="job-name"[^>]*>(.*?)</a>',
            r'<a[^>]*class="[^"]*job-name[^"]*"[^>]*>(.*?)</a>',
            r'<span[^>]*class="[^"]*job-name[^"]*"[^>]*>(.*?)</span>',
            r'<div[^>]*class="[^"]*job-title[^"]*"[^>]*>(.*?)</div>',
        ]
        for pattern in job_name_patterns:
            match = re.search(pattern, card_html, re.DOTALL)
            if match:
                job["jobName"] = self._clean_text(match.group(1))
                break
        
        # 提取薪资 - 尝试多种模式
        salary_patterns = [
            r'class="job-salary"[^>]*>(.*?)</span>',
            r'<span[^>]*class="[^"]*salary[^"]*"[^>]*>(.*?)</span>',
            r'<div[^>]*class="[^"]*salary[^"]*"[^>]*>(.*?)</div>',
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, card_html, re.DOTALL)
            if match:
                salary_text = self._clean_text(match.group(1))
                # 过滤掉无效的薪资（如 "-元/天", "-K"）
                if salary_text and salary_text not in ['-元/天', '-K', '-', '面议']:
                    # 检查是否包含有效薪资关键字
                    if any(keyword in salary_text for keyword in ['K', 'k', '元', '万', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                        job["salaryDesc"] = salary_text
                break
        
        # 提取公司名称 - 使用 boss-name 类
        company_patterns = [
            r'class="boss-name"[^>]*>(.*?)</span>',
            r'<span[^>]*class="[^"]*boss-name[^"]*"[^>]*>(.*?)</span>',
            r'class="company-name"[^>]*>(.*?)</a>',
            r'class="company-name"[^>]*>(.*?)</h3>',
            r'class="company-name"[^>]*>(.*?)</div>',
        ]
        for pattern in company_patterns:
            company_match = re.search(pattern, card_html, re.DOTALL)
            if company_match:
                company_text = self._clean_text(company_match.group(1))
                if company_text:
                    job["brandName"] = company_text
                    break
        
        # 提取城市 - 使用 company-location 类
        city_patterns = [
            r'class="company-location"[^>]*>(.*?)</span>',
            r'<span[^>]*class="[^"]*company-location[^"]*"[^>]*>(.*?)</span>',
            r'class="city"[^>]*>(.*?)</span>',
            r'class="job-area"[^>]*>(.*?)</span>',
        ]
        for pattern in city_patterns:
            city_match = re.search(pattern, card_html)
            if city_match:
                city_text = self._clean_text(city_match.group(1))
                # 提取城市名称（去掉区域信息）
                if city_text:
                    # 格式如 "深圳·南山区·西丽"，提取第一部分
                    city_parts = city_text.split('·')
                    job["cityName"] = city_parts[0].strip() if city_parts else city_text
                    # 保存完整地址信息
                    if len(city_parts) >= 2:
                        job["areaDistrict"] = city_parts[1].strip() if len(city_parts) > 1 else ""
                        job["businessDistrict"] = city_parts[2].strip() if len(city_parts) > 2 else ""
                    break
        
        # 提取职位标签（tag-list）
        tag_list_match = re.search(r'<ul[^>]*class="[^"]*tag-list[^"]*"[^>]*>(.*?)</ul>', card_html, re.DOTALL)
        if tag_list_match:
            tags_html = tag_list_match.group(1)
            tags = re.findall(r'<li[^>]*>(.*?)</li>', tags_html, re.DOTALL)
            if tags:
                cleaned_tags = [self._clean_text(tag) for tag in tags if self._clean_text(tag)]
                job["jobLabels"] = cleaned_tags
                
                # 尝试从标签中提取学历和经验要求
                for tag in cleaned_tags:
                    tag_lower = tag.lower()
                    # 学历关键词
                    if any(edu in tag for edu in ['本科', '硕士', '博士', '大专', '高中', '中专', '初中']):
                        job["jobDegree"] = tag
                    # 经验关键词
                    elif any(exp in tag for exp in ['年', '经验', '应届', '在校']):
                        job["jobExperience"] = tag
        
        # 提取职位 ID - 尝试多种属性
        job_id_patterns = [
            r'href="/job_detail/([^"]+)\.html"',
            r'data-jobid="([^"]+)"',
            r'data-job-id="([^"]+)"',
            r'data-lid="([^"]+)"',
        ]
        for pattern in job_id_patterns:
            job_id_match = re.search(pattern, card_html)
            if job_id_match:
                job["encryptJobId"] = job_id_match.group(1)
                break
        
        # 如果至少有职位名称，就认为是有效的
        return job if "jobName" in job else None
    
    def _extract_jobs_from_json(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """从 JSON 数据中提取职位列表。"""
        # 尝试不同的路径
        paths = [
            ["jobList"],
            ["zpData", "jobList"],
            ["data", "jobList"],
            ["result", "jobList"],
        ]
        
        for path in paths:
            current = data
            try:
                for key in path:
                    current = current[key]
                if isinstance(current, list) and current:
                    return [self._normalize_job(job) for job in current]
            except (KeyError, TypeError):
                continue
        
        return []
    
    def _normalize_job(self, job: dict[str, Any]) -> dict[str, Any]:
        """标准化职位数据格式，确保与 DataParser 期望的格式一致。"""
        # 确保必需字段存在
        normalized = {
            "jobName": job.get("jobName", ""),
            "brandName": job.get("brandName", ""),
            "cityName": job.get("cityName", ""),
            "encryptJobId": job.get("encryptJobId", ""),
            "salaryDesc": job.get("salaryDesc", ""),
            # 添加 DataParser 期望的其他字段
            "jobDegree": job.get("jobDegree", ""),
            "jobExperience": job.get("jobExperience", ""),
            "jobLabels": job.get("jobLabels", []),
            "areaDistrict": job.get("areaDistrict", ""),
            "businessDistrict": job.get("businessDistrict", ""),
            "brandIndustry": job.get("brandIndustry", ""),
            "brandScaleName": job.get("brandScaleName", ""),
            "bossName": job.get("bossName", ""),
            "bossTitle": job.get("bossTitle", ""),
        }
        
        # 复制其他字段
        for key, value in job.items():
            if key not in normalized:
                normalized[key] = value
        
        return normalized
    
    def _clean_text(self, text: str) -> str:
        """清理文本，移除 HTML 标签和多余空白。"""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
