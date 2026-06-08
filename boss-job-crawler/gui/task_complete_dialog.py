"""Task completion dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QLabel, QVBoxLayout

from .styles import COLORS, get_button_style, get_dialog_style


class TaskCompleteDialog(QDialog):
    """Show a polished summary when a task finishes."""

    def __init__(
        self,
        keyword: str,
        city: str,
        pages: int,
        total_jobs: int,
        unique_jobs: int,
        output_path: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("任务完成")
        self.resize(560, 320)
        self.setModal(True)
        self.setStyleSheet(get_dialog_style())

        title = QLabel("任务已完成")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {COLORS['success']}; padding: 8px 0;"
        )

        subtitle = QLabel("本次采集已经结束，结果已整理完毕。")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")

        info_frame = QFrame()
        info_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_secondary']}; border-radius: 8px; padding: 16px;}}"
        )

        summary = QLabel(
            "\n".join(
                [
                    f"<b>关键词：</b>{keyword or '-'}",
                    f"<b>城市：</b>{city or '-'}",
                    f"<b>页数：</b>{pages}",
                    f"<b>职位总数：</b><span style='color: {COLORS['primary']};'>{total_jobs}</span>",
                    f"<b>去重后职位数：</b><span style='color: {COLORS['success']};'>{unique_jobs}</span>",
                    f"<b>输出文件：</b>{output_path or '-'}",
                ]
            )
        )
        summary.setWordWrap(True)
        summary.setStyleSheet(f"font-size: 13px; line-height: 1.8; color: {COLORS['text_primary']};")

        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(summary)

        self.open_file_button = None
        self.open_dir_button = None

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        close_button = buttons.button(QDialogButtonBox.Close)
        close_button.setText("关闭")
        close_button.setStyleSheet(get_button_style("neutral"))

        if output_path:
            self.open_file_button = buttons.addButton("打开文件", QDialogButtonBox.ActionRole)
            self.open_dir_button = buttons.addButton("打开目录", QDialogButtonBox.ActionRole)
            self.open_file_button.setStyleSheet(get_button_style("primary"))
            self.open_dir_button.setStyleSheet(get_button_style("neutral"))

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(info_frame)
        layout.addStretch(1)
        layout.addWidget(buttons)
