"""Background worker for crawl jobs."""

from __future__ import annotations

from boss_crawler import CrawlerController, Event, EventType
from PySide6.QtCore import QObject, Signal, Slot


class CrawlWorker(QObject):
    """Run crawler work without blocking the UI."""

    event_received = Signal(object)
    progress_changed = Signal(int, int, int, int)
    finished = Signal(object)
    failed = Signal(str)
    stopped = Signal()

    def __init__(self, controller: CrawlerController, keyword: str, max_pages: int, fetch_details: bool = True, output_filename: str | None = None) -> None:
        super().__init__()
        self.controller = controller
        self.keyword = keyword
        self.max_pages = max_pages
        self.fetch_details = fetch_details
        self.output_filename = output_filename
        self._stop_requested = False

    @Slot()
    def run(self) -> None:
        original_handler = self.controller.event_handler
        self.controller.event_handler = self._forward_event
        try:
            self.event_received.emit(
                Event(
                    type=EventType.PROGRESS,
                    message="任务已启动",
                    payload={
                        "page": 0,
                        "max_pages": self.max_pages,
                        "total_jobs": 0,
                        "unique_jobs": 0,
                        "completed_jobs": 0,
                    },
                )
            )
            result = self.controller.start(
                keyword=self.keyword, 
                max_pages=self.max_pages, 
                fetch_details=self.fetch_details,
                output_filename=self.output_filename
            )
            
            # Check if task was stopped
            if self._stop_requested or not result.success:
                error_msg = result.error_message or ""
                if "停止" in error_msg or "已由用户停止" in error_msg:
                    self.stopped.emit()
                    return
            
            self.progress_changed.emit(result.pages_crawled, self.max_pages, result.total_jobs, result.unique_jobs)
            self.finished.emit(result)
        except Exception as exc:
            if self._stop_requested:
                self.stopped.emit()
            else:
                self.failed.emit(str(exc))
        finally:
            self.controller.event_handler = original_handler

    def stop(self) -> None:
        self._stop_requested = True
        self.controller.stop()

    def _forward_event(self, event: Event) -> None:
        self.event_received.emit(event)
        if event.type == EventType.PROGRESS:
            self.progress_changed.emit(
                int(event.payload.get("page", 0)),
                int(event.payload.get("max_pages", self.max_pages)),
                int(event.payload.get("total_jobs", 0)),
                int(event.payload.get("unique_jobs", 0)),
            )
