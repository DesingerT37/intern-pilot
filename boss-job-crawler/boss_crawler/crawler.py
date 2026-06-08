"""兼容保留的爬虫入口骨架。"""

from __future__ import annotations

from .config import CrawlerConfig
from .controller import CrawlerController
from .models import CrawlResult


class BossCrawler:
    """旧接口兼容层，内部转到控制器。"""

    def __init__(self, config: CrawlerConfig | None = None):
        self.controller = CrawlerController(config=config)

    def start_crawl(self, keyword: str, max_pages: int) -> CrawlResult:
        return self.controller.start(keyword=keyword, max_pages=max_pages)

    def stop_crawl(self) -> None:
        self.controller.stop()
