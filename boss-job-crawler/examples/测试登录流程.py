"""第二阶段登录流程测试脚本。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from boss_crawler import BrowserError, CrawlerConfig, LoginError, LoginManager


def main() -> None:
    config = CrawlerConfig()
    manager = LoginManager(config=config)

    print("=== BOSS直聘登录流程测试 ===")
    print("1. 程序将打开 BOSS 登录页")
    print("2. 请在浏览器中手动扫码或验证码登录")
    print("3. 登录完成后，回到终端按回车继续检测")
    print()

    try:
        manager.open_login_page()
    except BrowserError as exc:
        print(f"浏览器启动失败：{exc}")
        return

    input("完成登录后按回车继续检测...")

    try:
        status = manager.check_login_status()
    except LoginError as exc:
        print(f"登录检测失败：{exc}")
        return

    print(f"登录结果：{'已登录' if status.is_logged_in else '未登录'}")
    print(f"提示信息：{status.message}")
    print(f"检测时间：{status.checked_at}")
    print(f"状态文件：{manager.state_file}")


if __name__ == "__main__":
    main()
