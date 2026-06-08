"""Qt application entrypoint."""

from __future__ import annotations

import sys


def run() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:
        raise RuntimeError(
            "未安装 PySide6，请先执行 `pip install -r requirements.txt`。"
        ) from exc

    from .main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("BOSS 直聘职位采集工具")
    window = MainWindow()
    window.show()
    return app.exec()
