"""浏览器驱动模块。"""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

from .config import CrawlerConfig
from .exceptions import BrowserError


class BrowserDriver:
    """对 DrissionPage 浏览器实例做一层薄封装。"""

    def __init__(self, config: CrawlerConfig | None = None):
        self.config = config or CrawlerConfig()
        self.page: Any | None = None
        self.options: Any | None = None
        self.profile_dir: Path = self.config.paths.session_dir / "browser_profile"

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _resolve_browser_path(self) -> str:
        configured = self.config.runtime.browser_name.strip().lower()
        candidates = []

        if configured in {"edge", "msedge"}:
            candidates.extend(
                [
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                ]
            )
        else:
            candidates.extend(
                [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                ]
            )

        for candidate in candidates:
            if Path(candidate).exists():
                return candidate

        raise BrowserError("未找到可用的 Chrome/Edge 浏览器可执行文件。")

    def _build_options(self) -> Any:
        """构建浏览器配置选项，兼容 DrissionPage 3.x 和 4.x。"""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        browser_path = self._resolve_browser_path()
        local_port = self._find_free_port()
        
        # 尝试导入 DrissionPage
        try:
            from DrissionPage import ChromiumOptions
        except ImportError as exc:
            raise BrowserError(
                "未安装 DrissionPage，无法启动浏览器。请先执行 `pip install -r requirements.txt`。"
            ) from exc
        
        options = ChromiumOptions()
        
        # 检测版本并使用对应的 API
        # 4.x 有 set_local_port，3.x 没有
        if hasattr(options, "set_local_port"):
            # DrissionPage 4.x
            options.set_local_port(local_port)
            options.set_user_data_path(str(self.profile_dir))
            options.set_browser_path(browser_path)
            options.set_argument("--disable-blink-features=AutomationControlled")
            options.set_argument("--disable-dev-shm-usage")
            options.set_argument("--no-sandbox")
            options.set_argument("--disable-gpu")
            options.set_argument("--disable-extensions")
            if self.config.runtime.headless:
                options.set_argument("--headless=new")
            options.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            )
        else:
            # DrissionPage 3.x
            # 3.x 使用 auto_port 自动分配端口
            options.auto_port(True)
            
            # 3.x 使用 set_paths 设置浏览器路径和用户数据目录
            # 参数签名: (browser_path=None, local_port=None, debugger_address=None, 
            #            download_path=None, user_data_path=None, cache_path=None)
            options.set_paths(
                browser_path=browser_path,
                user_data_path=str(self.profile_dir)
            )
            
            # 设置参数
            options.set_argument("--disable-blink-features=AutomationControlled")
            options.set_argument("--disable-dev-shm-usage")
            options.set_argument("--no-sandbox")
            options.set_argument("--disable-gpu")
            options.set_argument("--disable-extensions")
            
            if self.config.runtime.headless:
                if hasattr(options, "set_headless"):
                    options.set_headless(True)
                else:
                    options.set_argument("--headless")
            
            if hasattr(options, "set_user_agent"):
                options.set_user_agent(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
                )
        
        return options

    def is_alive(self) -> bool:
        """判断当前页面对象是否仍与浏览器进程保持有效连接。"""
        if self.page is None:
            return False
        try:
            states = getattr(self.page, "states", None)
            if states is not None and hasattr(states, "is_alive"):
                return bool(states.is_alive)
            _ = getattr(self.page, "url", None)
            return True
        except Exception:
            return False

    def release(self) -> None:
        """断开页面对象引用（保留 user_data 目录中的登录 cookies）。"""
        if self.page is None:
            return
        try:
            if hasattr(self.page, "quit"):
                self.page.quit()
            elif hasattr(self.page, "close"):
                self.page.close()
        except Exception:
            pass
        finally:
            self.page = None

    def start(self) -> Any:
        """启动浏览器并返回页面对象。"""
        if self.page is not None:
            if self.is_alive():
                return self.page
            self.release()

        self.config.validate()
        
        try:
            self.options = self._build_options()
        except Exception as exc:
            raise BrowserError(f"构建浏览器配置失败：{exc}") from exc

        # 导入页面类
        try:
            from DrissionPage import ChromiumPage
        except ImportError as exc:
            raise BrowserError(
                "当前环境缺少 DrissionPage，无法创建页面对象。"
            ) from exc

        try:
            self.page = ChromiumPage(self.options)
            
            # 注入反检测脚本
            self._inject_anti_detection_script()
            
        except Exception as exc:
            # 提供更详细的错误信息
            error_details = []
            error_details.append(f"原始错误：{exc}")
            
            if hasattr(self.options, "browser_path"):
                error_details.append(f"浏览器路径：{self.options.browser_path}")
            
            if hasattr(self.options, "address"):
                error_details.append(f"连接地址：{self.options.address}")
            
            if hasattr(self.options, "user_data_path"):
                error_details.append(f"用户数据目录：{self.options.user_data_path}")
            
            error_msg = "浏览器启动失败。" + " | ".join(error_details)
            
            # 添加常见问题提示
            error_msg += "\n\n可能的原因："
            error_msg += "\n1. 浏览器正在被其他程序使用"
            error_msg += "\n2. 端口被占用"
            error_msg += "\n3. DrissionPage 版本不兼容"
            error_msg += "\n4. 浏览器路径不正确"
            error_msg += "\n\n建议："
            error_msg += "\n1. 关闭所有浏览器窗口后重试"
            error_msg += "\n2. 运行 diagnose_browser.py 进行详细诊断"
            error_msg += "\n3. 更新 DrissionPage：pip install --upgrade DrissionPage"
            
            raise BrowserError(error_msg) from exc

        return self.page
    
    def _inject_anti_detection_script(self) -> None:
        """注入反检测 JavaScript 脚本。"""
        if self.page is None:
            return
        
        try:
            # 隐藏 webdriver 特征
            anti_detection_js = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 隐藏自动化控制特征
            window.navigator.chrome = {
                runtime: {}
            };
            
            // 覆盖 permissions 查询
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Cypress.state('denied') }) :
                    originalQuery(parameters)
            );
            
            // 隐藏 Playwright/Puppeteer 特征
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
            
            # 尝试执行脚本
            if hasattr(self.page, "run_js"):
                self.page.run_js(anti_detection_js)
            elif hasattr(self.page, "execute_script"):
                self.page.execute_script(anti_detection_js)
        except Exception:
            # 如果注入失败，不影响主流程
            pass

    def get_page(self) -> Any:
        """获取当前页面对象；连接失效时自动用同一 profile 重新启动。"""
        return self.start()

    def open_url(self, url: str) -> None:
        """打开指定 URL。
        
        Raises:
            BrowserError: 如果浏览器连接已断开或打开 URL 失败
        """
        try:
            page = self.get_page()
            page.get(url)
        except Exception as exc:
            # 检查是否是连接断开错误
            error_msg = str(exc).lower()
            if (
                "连接已断开" in error_msg
                or "connection" in error_msg
                or "disconnect" in error_msg
                or "not defined" in error_msg
                or "browser is not" in error_msg
            ):
                self.release()
                raise BrowserError("浏览器窗口已关闭，请重新打开登录页。") from exc
            else:
                raise BrowserError(f"打开网页失败：{exc}") from exc

    def get_current_url(self) -> str:
        """获取当前页面 URL。"""
        try:
            page = self.get_page()
            return str(getattr(page, "url", "") or "")
        except Exception:
            return ""

    def get_html(self) -> str:
        """获取当前页面 HTML。"""
        try:
            page = self.get_page()
            return str(getattr(page, "html", "") or "")
        except Exception:
            return ""

    def get_cookies(self) -> Any:
        """获取当前浏览器 cookies。"""
        try:
            page = self.get_page()
            
            # DrissionPage 3.x: cookies 是属性（dict）
            # DrissionPage 4.x: cookies 是方法
            cookies_attr = getattr(page, "cookies", None)
            
            if cookies_attr is None:
                return []
            
            # 如果是可调用的（4.x），尝试调用
            if callable(cookies_attr):
                try:
                    return cookies_attr(as_dict=False)
                except TypeError:
                    return cookies_attr()
            else:
                # 如果是属性（3.x），直接返回
                return cookies_attr
        except Exception:
            return []

    def wait(self, seconds: float) -> None:
        """等待若干秒。"""
        page = self.get_page()
        wait_obj = getattr(page, "wait", None)
        if wait_obj and hasattr(wait_obj, "sleep"):
            wait_obj.sleep(seconds)
            return

        import time

        time.sleep(seconds)

    def close(self) -> None:
        """关闭浏览器。"""
        self.release()
