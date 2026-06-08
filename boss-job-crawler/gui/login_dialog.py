"""Login guide dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from .styles import COLORS, get_button_style, get_dialog_style


class LoginDialog(QDialog):
    """Explain the manual browser login flow."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("登录引导")
        self.setModal(True)
        self.resize(500, 260)
        self.setStyleSheet(get_dialog_style())

        intro = QLabel(
            "1. 点击确认后，程序会打开浏览器登录页面。\n"
            "2. 请在浏览器中完成扫码登录或验证码登录。\n"
            "3. 回到程序后，点击“检查状态”确认登录是否生效。"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(
            f"font-size: 14px; line-height: 1.6; padding: 12px; color: {COLORS['text_primary']};"
        )

        note = QLabel("程序会复用浏览器登录状态，不会保存你的明文密码。")
        note.setWordWrap(True)
        note.setStyleSheet(
            f"font-size: 12px; color: {COLORS['text_secondary']}; "
            f"padding: 10px; background-color: {COLORS['primary_light']}; border-radius: 6px;"
        )

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        ok_button.setText("打开浏览器")
        cancel_button.setText("取消")
        ok_button.setStyleSheet(get_button_style("primary"))
        cancel_button.setStyleSheet(get_button_style("neutral"))

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(intro)
        layout.addWidget(note)
        layout.addStretch(1)
        layout.addWidget(buttons)
