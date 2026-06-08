"""Crawler controller."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from logging import Logger
from time import monotonic
from typing import Any
from urllib.parse import quote

from .browser import BrowserDriver
from .config import CrawlerConfig
from .events import Event, EventType, TaskStatus
from .exceptions import ListenerError, ParseError, TaskStateError
from .exporter import ExcelExporter
from .listener import APIListener
from .login import LoginManager
from .models import CrawlResult, JobInfo
from .parser import DataParser
from .storage import DataStorage
from .utils import build_output_file_path, setup_logging

EventHandler = Callable[[Event], None]


class CrawlerController:
    """Unified entrypoint for crawl tasks."""

    def __init__(
        self,
        config: CrawlerConfig | None = None,
        event_handler: EventHandler | None = None,
        *,
        browser: BrowserDriver | None = None,
        login_manager: LoginManager | None = None,
        listener: APIListener | None = None,
        parser: DataParser | None = None,
        storage: DataStorage | None = None,
        exporter: ExcelExporter | None = None,
    ):
        self.config = config or CrawlerConfig()
        self.logger: Logger = setup_logging(self.config)
        self.event_handler = event_handler
        self._status = TaskStatus.IDLE
        self.browser = browser or BrowserDriver(config=self.config)
        self.login_manager = login_manager or LoginManager(config=self.config, browser=self.browser)
        self.listener = listener or APIListener()
        self.parser = parser or DataParser()
        self.storage = storage or DataStorage(enable_deduplication=self.config.runtime.enable_deduplication)
        self.exporter = exporter or ExcelExporter()

    def emit_event(self, event_type: EventType, message: str, **payload: object) -> None:
        event = Event(type=event_type, message=message, payload=dict(payload))
        if self.event_handler:
            self.event_handler(event)
        self.logger.info("%s | %s", event.type.value, event.message)

    def start(self, keyword: str, max_pages: int, fetch_details: bool = True, output_filename: str | None = None, export_excel: bool = True) -> CrawlResult:
        """开始爬取任务。
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大页数
            fetch_details: 是否抓取职位详情（职位描述）。默认 True。
                          设为 False 可加快速度，但不会获取职位描述。
            output_filename: 输出文件名（可选）。如果不提供，使用关键词生成。
            export_excel: 是否导出 Excel 文件。默认 True。
                         设为 False 时只返回数据，不导出文件（用于 API 调用）。
        """
        if self.is_running():
            raise TaskStateError("当前已有爬取任务在运行")
        if not keyword.strip():
            raise TaskStateError("关键词不能为空")
        if max_pages <= 0:
            raise TaskStateError("页数必须大于 0")

        self._status = TaskStatus.RUNNING
        self.storage.clear()
        started_at = monotonic()
        self.emit_event(
            EventType.TASK_STATUS, 
            "任务已开始", 
            keyword=keyword, 
            max_pages=max_pages,
            fetch_details=fetch_details
        )

        try:
            login_status = self.login_manager.ensure_logged_in()
            if not login_status.is_logged_in:
                raise TaskStateError(login_status.message or "开始爬取前请先完成登录")

            page = self.browser.get_page()
            
            # 使用 DrissionPage 4.x 的 listen API
            # 监听包含 'joblist' 的 API 请求
            page.listen.start('joblist')
            
            total_jobs = 0
            pages_crawled = 0
            completed_jobs = 0

            # 阶段一：抓取各页职位列表（去重后总量在全部列表完成后才确定）
            for page_number in range(1, max_pages + 1):
                self._ensure_not_stopped()
                self.emit_event(EventType.INFO, f"正在加载第 {page_number} 页", page=page_number)

                self.browser.open_url(self._build_search_url(keyword=keyword, page=page_number))
                response = self._get_response_with_retries(page_number, page)
                jobs = self.parser.parse_job_list(response)

                total_jobs += len(jobs)
                self.storage.add_jobs_batch(jobs)
                pages_crawled = page_number

                self.emit_event(
                    EventType.PROGRESS,
                    f"第 {page_number} 页职位列表已获取",
                    page=page_number,
                    max_pages=max_pages,
                    total_jobs=total_jobs,
                    unique_jobs=self.storage.get_job_count(),
                    completed_jobs=completed_jobs,
                )

                if page_number < max_pages:
                    try:
                        page.scroll.to_bottom()
                        self.browser.wait(self.config.retry.page_delay_seconds)
                    except Exception:
                        pass

            unique_total = self.storage.get_job_count()

            if fetch_details and unique_total > 0:
                self.emit_event(
                    EventType.INFO,
                    f"列表抓取完成，共 {unique_total} 个去重职位，开始获取详情...",
                )
                completed_jobs = self._fetch_job_details(
                    self.storage.get_all_jobs(),
                    pages_crawled,
                    total_jobs,
                    max_pages,
                    unique_total,
                    completed_jobs,
                )
            else:
                if not fetch_details:
                    self.emit_event(EventType.INFO, "跳过职位详情抓取（快速模式）")
                completed_jobs = unique_total
                self.emit_event(
                    EventType.PROGRESS,
                    "职位列表抓取完成",
                    page=pages_crawled,
                    max_pages=max_pages,
                    total_jobs=total_jobs,
                    unique_jobs=unique_total,
                    completed_jobs=completed_jobs,
                )

            # 导出 Excel（可选）
            exported_file = None
            if export_excel:
                output_path = build_output_file_path(self.config.paths.output_dir, keyword)
                
                # 如果用户指定了文件名，使用用户指定的文件名
                if output_filename and output_filename.strip():
                    filename = output_filename.strip()
                    # 确保文件名有 .xlsx 扩展名
                    if not filename.endswith('.xlsx'):
                        filename += '.xlsx'
                    output_path = self.config.paths.output_dir / filename
                
                try:
                    exported_file = self.exporter.export(self.storage.get_all_jobs(), output_path)
                    self.emit_event(EventType.INFO, f"Excel 文件已导出: {exported_file}")
                except Exception as export_exc:
                    # 导出失败不影响爬取结果
                    self.logger.warning(f"导出 Excel 失败: {export_exc}")
                    self.emit_event(EventType.WARNING, f"导出 Excel 失败: {export_exc}")
            else:
                self.emit_event(EventType.INFO, "跳过 Excel 导出（API 调用模式）")

            self._status = TaskStatus.COMPLETED
            result = CrawlResult(
                success=True,
                total_jobs=total_jobs,
                unique_jobs=self.storage.get_job_count(),
                pages_crawled=pages_crawled,
                output_file=str(exported_file) if exported_file else None,
                crawl_duration=monotonic() - started_at,
            )
            self.emit_event(
                EventType.RESULT,
                "任务已完成",
                output_file=result.output_file or "无",
                total_jobs=result.total_jobs,
                unique_jobs=result.unique_jobs,
            )
            self.emit_event(EventType.TASK_STATUS, "任务已完成", status=self._status.value)
            return result
        except Exception as exc:
            if self._status == TaskStatus.STOPPING:
                self._status = TaskStatus.STOPPED
                self.emit_event(EventType.TASK_STATUS, "任务已停止", status=self._status.value)
                return CrawlResult(
                    success=False,
                    total_jobs=self.storage.get_job_count(),
                    unique_jobs=self.storage.get_job_count(),
                    pages_crawled=0,
                    error_message="任务已由用户停止",
                    crawl_duration=monotonic() - started_at,
                )

            self._status = TaskStatus.FAILED
            self.emit_event(EventType.ERROR, str(exc))
            self.emit_event(EventType.TASK_STATUS, "任务失败", status=self._status.value)
            return CrawlResult(
                success=False,
                total_jobs=self.storage.get_job_count(),
                unique_jobs=self.storage.get_job_count(),
                pages_crawled=0,
                error_message=str(exc),
                crawl_duration=monotonic() - started_at,
            )
        finally:
            # 停止监听；若用户已关闭浏览器窗口，释放失效的 page 引用以便下次复用 profile 重连
            try:
                if self.browser.is_alive():
                    page = self.browser.page
                    if page is not None and hasattr(page, "listen") and hasattr(page.listen, "stop"):
                        page.listen.stop()
            except Exception:
                pass
            if not self.browser.is_alive():
                self.browser.release()

            if self._status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.STOPPED}:
                pass
            elif self._status == TaskStatus.RUNNING:
                self._status = TaskStatus.IDLE

    def stop(self) -> None:
        if self._status != TaskStatus.RUNNING:
            self._status = TaskStatus.STOPPED
            self.emit_event(EventType.TASK_STATUS, "任务已停止", status=self._status.value)
            return

        self._status = TaskStatus.STOPPING
        
        try:
            if self.browser.is_alive():
                page = self.browser.page
                if page is not None and hasattr(page, "listen") and hasattr(page.listen, "stop"):
                    page.listen.stop()
        except Exception:
            pass

        self.emit_event(EventType.TASK_STATUS, "正在停止任务", status=self._status.value)

    def is_running(self) -> bool:
        return self._status in {TaskStatus.RUNNING, TaskStatus.STOPPING}

    def open_login_page(self) -> None:
        self.login_manager.open_login_page()
        self.emit_event(EventType.LOGIN_STATUS, "登录页面已打开，请在浏览器中完成登录。")

    def check_login_status(self) -> bool:
        status = self.login_manager.check_login_status()
        self.emit_event(
            EventType.LOGIN_STATUS,
            status.message,
            is_logged_in=status.is_logged_in,
            checked_at=status.checked_at,
        )
        return status.is_logged_in

    def _build_search_url(self, keyword: str, page: int) -> str:
        query = quote(keyword.strip())
        city = quote(self.config.runtime.city_code)
        return f"https://www.zhipin.com/web/geek/jobs?query={query}&city={city}&page={page}"

    def _get_response_with_retries(self, page_number: int, page: Any) -> dict[str, object]:
        """使用 DrissionPage 4.x listen API 获取 API 响应。"""
        last_error: Exception | None = None
        attempts = self.config.retry.max_retries + 1

        for attempt in range(1, attempts + 1):
            self._ensure_not_stopped()
            try:
                # 等待 API 响应（DrissionPage 4.x）
                resp = page.listen.wait(timeout=self.config.retry.request_timeout_seconds)
                
                # 获取响应体
                json_data = resp.response.body
                
                # 验证响应格式
                if not isinstance(json_data, dict):
                    raise ParseError(f"API 响应格式错误：期望 dict，实际 {type(json_data)}")
                
                if "zpData" not in json_data:
                    raise ParseError("API 响应缺少 zpData 字段")
                
                if "jobList" not in json_data.get("zpData", {}):
                    raise ParseError("API 响应缺少 jobList 字段")
                
                return json_data
                
            except (ListenerError, ParseError) as exc:
                last_error = exc
                self.emit_event(
                    EventType.WARNING,
                    f"第 {page_number} 页第 {attempt}/{attempts} 次尝试失败：{exc}",
                    page=page_number,
                    attempt=attempt,
                )
            except Exception as exc:
                # 捕获其他异常（如超时）
                last_error = ListenerError(f"等待 API 响应失败：{exc}")
                self.emit_event(
                    EventType.WARNING,
                    f"第 {page_number} 页第 {attempt}/{attempts} 次尝试失败：{last_error}",
                    page=page_number,
                    attempt=attempt,
                )
        
        # 所有重试都失败了，尝试使用 HTML 解析作为回退方案
        self.emit_event(
            EventType.WARNING,
            f"第 {page_number} 页网络监听失败，尝试使用 HTML 解析...",
            page=page_number,
        )
        
        try:
            from .parser_html import HTMLParser
            html_parser = HTMLParser()
            
            # 获取当前页面的 HTML
            html = self.browser.get_html()
            if not html:
                raise ParseError("无法获取页面 HTML")
            
            # 从 HTML 中提取职位列表
            jobs = html_parser.parse_job_list_from_html(html)
            
            if not jobs:
                raise ParseError("HTML 解析未找到职位数据")
            
            self.emit_event(
                EventType.INFO,
                f"第 {page_number} 页使用 HTML 解析成功，找到 {len(jobs)} 个职位",
                page=page_number,
            )
            
            # 返回与 API 响应相同格式的数据
            return {"zpData": {"jobList": jobs}}
            
        except Exception as html_exc:
            self.emit_event(
                EventType.ERROR,
                f"第 {page_number} 页 HTML 解析也失败了：{html_exc}",
                page=page_number,
            )
            raise ListenerError(
                f"第 {page_number} 页获取职位数据失败。"
                f"网络监听错误：{last_error}，HTML 解析错误：{html_exc}"
            )

    def _ensure_not_stopped(self) -> None:
        if self._status == TaskStatus.STOPPING:
            raise TaskStateError("任务已由用户停止")
    
    def _fetch_job_details(
        self,
        jobs: list[JobInfo],
        page_number: int,
        total_jobs: int,
        max_pages: int,
        unique_total: int,
        completed_jobs: int,
    ) -> int:
        """抓取职位详情（职位描述和完整薪资）。

        Returns:
            更新后的已完成条数（用于进度条：completed_jobs / unique_total）。
        """
        total_count = len(jobs)
        for i, job in enumerate(jobs):
            self._ensure_not_stopped()

            try:
                if not job.job_id:
                    self.logger.warning(f"职位 {job.job_name} 没有 job_id，跳过详情抓取")
                    completed_jobs += 1
                    self._emit_detail_progress(
                        page_number,
                        max_pages,
                        total_jobs,
                        unique_total,
                        completed_jobs,
                        i + 1,
                        total_count,
                        job.job_name,
                    )
                    continue

                detail_url = f"https://www.zhipin.com/job_detail/{job.job_id}.html"
                self.emit_event(
                    EventType.INFO,
                    f"获取职位详情 ({completed_jobs + 1}/{unique_total}): {job.job_name}",
                    job_index=i + 1,
                    total_jobs_in_page=total_count,
                )

                self.browser.open_url(detail_url)

                delay = random.uniform(1.5, 3.0)
                time.sleep(delay)

                html = self.browser.get_html()
                if html:
                    description, salary = self._extract_job_detail_from_html(html)

                    if description:
                        job.job_description = description
                        self.logger.info(f"✓ 获取职位描述: {job.job_name}")

                    if salary and not job.salary_range:
                        job.salary_range = salary
                        self.logger.info(f"✓ 获取薪资信息: {job.job_name} - {salary}")

                completed_jobs += 1
                self._emit_detail_progress(
                    page_number,
                    max_pages,
                    total_jobs,
                    unique_total,
                    completed_jobs,
                    i + 1,
                    total_count,
                    job.job_name,
                )

            except Exception as e:
                self.logger.warning(f"获取职位详情失败: {job.job_name}, {e}")
                completed_jobs += 1
                self._emit_detail_progress(
                    page_number,
                    max_pages,
                    total_jobs,
                    unique_total,
                    completed_jobs,
                    i + 1,
                    total_count,
                    job.job_name,
                )
                continue

        return completed_jobs

    def _emit_detail_progress(
        self,
        page_number: int,
        max_pages: int,
        total_jobs: int,
        unique_total: int,
        completed_jobs: int,
        job_index: int,
        total_count: int,
        job_name: str,
    ) -> None:
        self.emit_event(
            EventType.PROGRESS,
            f"获取详情 ({job_index}/{total_count}): {job_name}",
            page=page_number,
            max_pages=max_pages,
            total_jobs=total_jobs,
            unique_jobs=unique_total,
            completed_jobs=completed_jobs,
            current_job_index=job_index,
            total_jobs_in_page=total_count,
        )
    
    def _extract_job_detail_from_html(self, html: str) -> tuple[str, str]:
        """从 HTML 中提取职位描述和薪资。
        
        Returns:
            tuple[str, str]: (职位描述, 薪资)
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            self.logger.error("未安装 beautifulsoup4，无法解析职位详情。请执行: pip install beautifulsoup4")
            return "", ""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取职位描述
            description = ""
            desc_elem = soup.select_one('.job-sec-text')
            if desc_elem:
                # 清理 HTML 标签，保留文本，使用换行符分隔
                description = desc_elem.get_text(separator='\n', strip=True)
                # 移除多余的空行
                description = '\n'.join(line for line in description.split('\n') if line.strip())
            
            # 提取薪资（如果列表 API 中没有）
            salary = ""
            salary_elem = soup.select_one('.job-salary')
            if salary_elem:
                salary = salary_elem.get_text(strip=True)
            
            return description, salary
            
        except Exception as e:
            self.logger.error(f"解析 HTML 失败: {e}")
            return "", ""
