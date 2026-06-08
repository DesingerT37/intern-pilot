"""Top status bar widget."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from ..styles import COLORS


class StatusChip(QFrame):
    def __init__(self, title: str, value: str = "-", tone: str = "neutral") -> None:
        super().__init__()
        self.title_label = QLabel(title)
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.set_tone(tone)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_tone(self, tone: str) -> None:
        tones = {
            "neutral": (COLORS["bg_tertiary"], COLORS["border"], COLORS["text_primary"]),
            "success": (COLORS["success_light"], COLORS["success"], COLORS["success"]),
            "warning": (COLORS["warning_light"], COLORS["warning"], COLORS["warning"]),
            "danger": (COLORS["danger_light"], COLORS["danger"], COLORS["danger"]),
            "info": (COLORS["primary_light"], COLORS["primary"], COLORS["primary"]),
        }
        bg, border, fg = tones.get(tone, tones["neutral"])
        self.setStyleSheet(
            f"QFrame {{background: {bg}; border: 1px solid {border}; border-radius: 8px;}}"
        )
        self.title_label.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 500; background: transparent; border: none;"
        )
        self.value_label.setStyleSheet(
            f"color: {fg}; font-size: 13px; font-weight: 600; background: transparent; border: none;"
        )


class StatusBarWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.login_chip = StatusChip("登录状态", "未检查", "warning")
        self.browser_chip = StatusChip("浏览器", "就绪", "neutral")
        self.disclaimer_chip = StatusChip("使用提示", "已确认", "success")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.login_chip)
        layout.addWidget(self.browser_chip)
        layout.addWidget(self.disclaimer_chip)

    def set_login_status(self, value: str, ok: bool) -> None:
        self.login_chip.set_value(value)
        self.login_chip.set_tone("success" if ok else "warning")

    def set_browser_status(self, value: str) -> None:
        tone = "danger" if value == "异常" else "info" if value in {"运行中", "启动中", "检查中"} else "neutral"
        self.browser_chip.set_value(value)
        self.browser_chip.set_tone(tone)

    def set_disclaimer_status(self, value: str) -> None:
        self.disclaimer_chip.set_value(value)
        self.disclaimer_chip.set_tone("success")
