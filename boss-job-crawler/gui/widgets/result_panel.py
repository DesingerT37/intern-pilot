"""Bottom result summary panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from ..styles import COLORS, get_button_style


class ResultPanel(QFrame):
    open_file_requested = Signal()
    open_dir_requested = Signal()
    view_log_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_primary']}; border: 1px solid {COLORS['border']}; border-radius: 8px;}}"
        )

        self.total_value = QLabel("0")
        self.unique_value = QLabel("0")
        self.duration_value = QLabel("0.0 秒")
        self.path_value = QLabel("-")

        for label in (self.total_value, self.unique_value, self.duration_value):
            label.setStyleSheet(f"font-weight: 600; color: {COLORS['primary']};")
        self.path_value.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        layout.addWidget(self._create_stat_label("总数"))
        layout.addWidget(self.total_value)
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_stat_label("去重后"))
        layout.addWidget(self.unique_value)
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_stat_label("耗时"))
        layout.addWidget(self.duration_value)
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_stat_label("输出文件"))
        layout.addWidget(self.path_value, 1)

        self.open_file_button = QPushButton("打开文件")
        self.open_dir_button = QPushButton("打开目录")
        self.view_log_button = QPushButton("查看日志")
        self.open_file_button.setStyleSheet(get_button_style("primary"))
        self.open_dir_button.setStyleSheet(get_button_style("neutral"))
        self.view_log_button.setStyleSheet(get_button_style("neutral"))
        self.open_file_button.clicked.connect(self.open_file_requested.emit)
        self.open_dir_button.clicked.connect(self.open_dir_requested.emit)
        self.view_log_button.clicked.connect(self.view_log_requested.emit)
        layout.addWidget(self.open_file_button)
        layout.addWidget(self.open_dir_button)
        layout.addWidget(self.view_log_button)
        self.reset()

    def _create_stat_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        return label

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-width: 1px;")
        return line

    def update_result(self, total: int, unique: int, duration: float, output_path: str) -> None:
        self.total_value.setText(str(total))
        self.unique_value.setText(str(unique))
        self.duration_value.setText(f"{duration:.1f} 秒")
        self.set_output_path(output_path)

    def set_output_path(self, path: str) -> None:
        self.path_value.setText(path or "-")
        self.open_file_button.setEnabled(bool(path))

    def set_log_file(self, path: str) -> None:
        self.view_log_button.setToolTip(path)

    def set_busy(self, busy: bool) -> None:
        self.open_file_button.setEnabled(not busy and self.path_value.text() not in {"", "-"})
        self.open_dir_button.setEnabled(not busy)
        self.view_log_button.setEnabled(True)

    def reset(self) -> None:
        self.update_result(0, 0, 0.0, "")
