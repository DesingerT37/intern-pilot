"""测试停止功能。"""

import time
from pathlib import Path

from boss_crawler import CrawlerConfig, CrawlerController, LoginStatus


class _FakeBrowser:
    def __init__(self):
        self.urls = []

    def get_page(self):
        return object()

    def open_url(self, url: str) -> None:
        self.urls.append(url)

    def wait(self, seconds: float) -> None:
        time.sleep(0.01)  # 模拟短暂延迟


class _FakeLoginManager:
    def __init__(self, logged_in: bool = True):
        self.logged_in = logged_in

    def check_login_status(self):
        return LoginStatus(is_logged_in=self.logged_in, message="ok" if self.logged_in else "not logged in")

    def open_login_page(self):
        return None


class _SlowListener:
    """模拟慢速响应的监听器，用于测试停止功能。"""

    def __init__(self, responses, delay_per_page=0.1):
        self.responses = list(responses)
        self.bound_page = None
        self.started_pattern = None
        self.stopped = False
        self.delay_per_page = delay_per_page

    def bind_page(self, page):
        self.bound_page = page

    def start(self, pattern: str):
        self.started_pattern = pattern

    def get_job_response(self, timeout):
        # 模拟网络延迟
        time.sleep(self.delay_per_page)
        if self.responses:
            return self.responses.pop(0)
        return {"zpData": {"jobList": []}}

    def stop(self):
        self.stopped = True


def test_controller_stops_gracefully(tmp_path):
    """测试控制器能够优雅地停止任务。"""
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.retry.page_delay_seconds = 0
    config.retry.request_timeout_seconds = 1
    config.validate()

    # 准备多页数据，模拟长时间运行的任务
    listener = _SlowListener(
        [
            {"zpData": {"jobList": [{"jobName": "Job1", "brandName": "A", "cityName": "北京", "encryptJobId": "1"}]}},
            {"zpData": {"jobList": [{"jobName": "Job2", "brandName": "B", "cityName": "上海", "encryptJobId": "2"}]}},
            {"zpData": {"jobList": [{"jobName": "Job3", "brandName": "C", "cityName": "深圳", "encryptJobId": "3"}]}},
        ],
        delay_per_page=0.05,
    )

    controller = CrawlerController(
        config=config,
        browser=_FakeBrowser(),
        login_manager=_FakeLoginManager(logged_in=True),
        listener=listener,
    )

    # 在另一个线程中启动爬取
    import threading

    result_holder = {}

    def run_crawl():
        result_holder["result"] = controller.start(keyword="python", max_pages=3)

    crawl_thread = threading.Thread(target=run_crawl)
    crawl_thread.start()

    # 等待一小段时间后停止
    time.sleep(0.08)
    controller.stop()

    # 等待线程完成
    crawl_thread.join(timeout=2.0)

    # 验证结果
    result = result_holder.get("result")
    assert result is not None
    assert result.success is False
    assert "停止" in result.error_message
    assert listener.stopped is True


def test_controller_stop_sets_correct_status(tmp_path):
    """测试停止操作设置正确的状态。"""
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.validate()

    controller = CrawlerController(
        config=config,
        browser=_FakeBrowser(),
        login_manager=_FakeLoginManager(logged_in=True),
        listener=_SlowListener([]),
    )

    # 在未运行时调用停止
    controller.stop()
    assert controller.is_running() is False


if __name__ == "__main__":
    import pytest
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
