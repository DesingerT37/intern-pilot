"""浏览器连接生命周期测试。"""

from boss_crawler.browser import BrowserDriver
from boss_crawler import CrawlerConfig


def test_is_alive_false_when_page_missing():
    config = CrawlerConfig()
    browser = BrowserDriver(config=config)
    assert not browser.is_alive()


def test_release_clears_stale_page():
    config = CrawlerConfig()
    browser = BrowserDriver(config=config)

    class _DeadPage:
        @property
        def url(self):
            raise RuntimeError("connection disconnected")

    browser.page = _DeadPage()
    assert not browser.is_alive()
    browser.release()
    assert browser.page is None
