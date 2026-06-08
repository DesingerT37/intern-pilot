"""登录管理模块。"""

from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from .browser import BrowserDriver
from .config import CrawlerConfig
from .exceptions import BrowserError, LoginError
from .models import LoginStatus


class LoginManager:
    """负责登录页打开、登录检测和会话清理。"""

    LOGIN_URL = "https://www.zhipin.com/web/user/"
    COOKIE_HINTS = {
        "__zp_stoken__",
        "bst",
        "wt2",
        "wbg",
        "wd_guid",
        "historyState",
    }

    def __init__(self, config: CrawlerConfig | None = None, browser: BrowserDriver | None = None):
        self.config = config or CrawlerConfig()
        self.browser = browser or BrowserDriver(config=self.config)
        self.state_file: Path = self.config.paths.session_dir / "login_state.json"

    def open_login_page(self) -> None:
        """打开 BOSS 登录页，供用户手动扫码或验证码登录。"""
        try:
            self.browser.start()
            self.browser.open_url(self.LOGIN_URL)
            self._write_state({"last_action": "open_login_page", "message": "已打开登录页。"})
        except BrowserError:
            raise
        except Exception as exc:
            error_msg = str(exc).lower()
            if (
                "连接已断开" in error_msg
                or "已关闭" in error_msg
                or "not defined" in error_msg
                or "browser is not" in error_msg
            ):
                self.browser.release()
                raise BrowserError("浏览器窗口已被关闭。如需登录，请重新点击'打开登录页'。") from exc
            raise BrowserError(f"打开登录页失败：{exc}") from exc

    def check_login_status(self, open_test_page: bool = False) -> LoginStatus:
        """检测登录态：只检查 cookie，不主动打开浏览器。

        open_test_page 已废弃，保留参数仅为兼容旧调用。
        """
        del open_test_page
        try:
            if self.browser.page is not None and not self.browser.is_alive():
                self.browser.release()

            # 浏览器已在运行时，直接读当前页 cookie（不跳转、不新开窗口）
            if self.browser.page is not None and self.browser.is_alive():
                return self._check_current_page_login_status()

            cookie_names = self._read_profile_cookie_names()
            is_logged_in = bool(cookie_names & self.COOKIE_HINTS)
            message = (
                "检测到有效登录 cookie。"
                if is_logged_in
                else "未检测到登录 cookie，请先点击「打开登录页」完成登录。"
            )
            status = LoginStatus(is_logged_in=is_logged_in, message=message)
            if is_logged_in:
                self._write_state(
                    {
                        "is_logged_in": True,
                        "message": message,
                        "checked_at": status.checked_at,
                        "cookie_names": sorted(cookie_names),
                        "profile_dir": str(self.browser.profile_dir),
                    }
                )
            return status
        except LoginError:
            raise
        except Exception as exc:
            raise LoginError(f"登录状态检测失败：{exc}") from exc

    def ensure_logged_in(self) -> LoginStatus:
        """爬取前检查是否已有登录 cookie。"""
        return self.check_login_status()

    def _read_profile_cookie_names(self) -> set[str]:
        """从本地 browser_profile 的 Cookies 数据库读取 BOSS 相关 cookie 名。"""
        profile_dir = self.browser.profile_dir
        db_candidates = [
            profile_dir / "Default" / "Network" / "Cookies",
            profile_dir / "Default" / "Cookies",
        ]
        for db_path in db_candidates:
            if db_path.exists():
                names = self._load_cookie_names_from_sqlite(db_path)
                if names:
                    return names

        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
                saved = state.get("cookie_names") or []
                return {str(name) for name in saved}
            except Exception:
                pass
        return set()

    def _load_cookie_names_from_sqlite(self, db_path: Path) -> set[str]:
        names: set[str] = set()
        uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
        try:
            with sqlite3.connect(uri, uri=True, timeout=1) as conn:
                rows = conn.execute(
                    "SELECT name FROM cookies "
                    "WHERE host_key LIKE '%zhipin%' OR host_key LIKE '%boss%'"
                ).fetchall()
                names = {str(row[0]) for row in rows}
        except Exception:
            pass

        if names:
            return names

        # 数据库可能被占用，复制到临时文件再读
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".cookies") as tmp:
                tmp_path = Path(tmp.name)
            shutil.copy2(db_path, tmp_path)
            with sqlite3.connect(tmp_path, timeout=1) as conn:
                rows = conn.execute(
                    "SELECT name FROM cookies "
                    "WHERE host_key LIKE '%zhipin%' OR host_key LIKE '%boss%'"
                ).fetchall()
                names = {str(row[0]) for row in rows}
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        return names

    def _check_current_page_login_status(self) -> LoginStatus:
        """检查当前浏览器页面的 cookie（浏览器已打开时）。"""
        try:
            cookie_names = self._extract_cookie_names(self.browser.get_cookies())
            is_logged_in = bool(cookie_names & self.COOKIE_HINTS)
            message = "检测到有效登录 cookie。" if is_logged_in else "未检测到有效登录 cookie，请在浏览器中完成登录。"

            status = LoginStatus(is_logged_in=is_logged_in, message=message)
            self._write_state(
                {
                    "is_logged_in": status.is_logged_in,
                    "message": status.message,
                    "checked_at": status.checked_at,
                    "current_url": self.browser.get_current_url().lower(),
                    "cookie_names": sorted(cookie_names),
                    "profile_dir": str(self.browser.profile_dir),
                }
            )
            return status
        except Exception as exc:
            self.browser.release()
            raise LoginError(f"检查登录状态时发生错误：{exc}") from exc

    def save_session(self) -> None:
        """将当前会话元信息写入本地。"""
        if self.browser.page is None or not self.browser.is_alive():
            return
        self._check_current_page_login_status()

    def clear_session(self) -> None:
        """清除本地浏览器用户目录和登录状态文件。"""
        self.browser.close()

        if self.browser.profile_dir.exists():
            shutil.rmtree(self.browser.profile_dir)
        if self.state_file.exists():
            self.state_file.unlink()

    def _write_state(self, payload: dict[str, Any]) -> None:
        self.config.paths.ensure_directories()
        self.state_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def _extract_cookie_names(cls, cookies: Any) -> set[str]:
        if isinstance(cookies, dict):
            return {str(name) for name in cookies.keys()}

        names: set[str] = set()
        if isinstance(cookies, (list, tuple)):
            for item in cookies:
                if isinstance(item, dict):
                    name = item.get("name")
                    if name:
                        names.add(str(name))
        return names
