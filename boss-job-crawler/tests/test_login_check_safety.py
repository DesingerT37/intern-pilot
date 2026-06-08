"""测试登录检查：仅依据 cookie，不启动浏览器。"""

import json
from pathlib import Path

from boss_crawler import CrawlerConfig, LoginManager


class _FakeBrowser:
    def __init__(self, should_fail: bool = False, alive: bool = True):
        self.page = None
        self.profile_dir = Path("/tmp/test_profile")
        self.should_fail = should_fail
        self.alive = alive
        self.start_count = 0
        self.release_count = 0
        self.urls_opened: list[str] = []

    def is_alive(self) -> bool:
        return self.page is not None and self.alive

    def release(self) -> None:
        self.release_count += 1
        self.page = None

    def start(self):
        if self.page is not None:
            if self.is_alive():
                return self.page
            self.release()
        self.start_count += 1
        if self.should_fail:
            raise Exception("浏览器启动失败")
        self.page = object()
        self.alive = True
        return self.page

    def get_cookies(self):
        return [
            {"name": "__zp_stoken__", "value": "test"},
            {"name": "wt2", "value": "test"},
        ]

    def get_current_url(self):
        return "https://www.zhipin.com/web/geek/job"

    def open_url(self, url: str) -> None:
        self.urls_opened.append(url)

    def close(self):
        self.release()


def test_check_login_reads_saved_cookie_names_without_starting_browser(tmp_path):
    config = CrawlerConfig()
    config.paths.session_dir = tmp_path / "sessions"
    config.paths.session_dir.mkdir(parents=True, exist_ok=True)

    browser = _FakeBrowser()
    browser.profile_dir = config.paths.session_dir / "browser_profile"
    manager = LoginManager(config=config, browser=browser)

    state_file = config.paths.session_dir / "login_state.json"
    state_file.write_text(
        json.dumps({"cookie_names": ["__zp_stoken__", "wt2"]}),
        encoding="utf-8",
    )

    status = manager.check_login_status()

    assert browser.start_count == 0
    assert status.is_logged_in


def test_check_login_without_cookie_is_not_logged_in(tmp_path):
    config = CrawlerConfig()
    config.paths.session_dir = tmp_path / "sessions"
    config.paths.session_dir.mkdir(parents=True, exist_ok=True)

    browser = _FakeBrowser()
    browser.profile_dir = config.paths.session_dir / "browser_profile"
    manager = LoginManager(config=config, browser=browser)

    status = manager.check_login_status()

    assert browser.start_count == 0
    assert not status.is_logged_in


def test_check_login_uses_live_browser_cookies_when_already_open():
    config = CrawlerConfig()
    browser = _FakeBrowser()
    manager = LoginManager(config=config, browser=browser)

    browser.start()
    status = manager.check_login_status()

    assert browser.start_count == 1
    assert status.is_logged_in


def test_stale_page_released_before_open_login(tmp_path):
    config = CrawlerConfig()
    config.paths.session_dir = tmp_path / "sessions"
    config.paths.session_dir.mkdir(parents=True, exist_ok=True)

    browser = _FakeBrowser()
    browser.profile_dir = config.paths.session_dir / "browser_profile"
    manager = LoginManager(config=config, browser=browser)
    browser.page = object()
    browser.alive = False

    manager.open_login_page()

    assert browser.release_count >= 1
    assert browser.start_count >= 1
