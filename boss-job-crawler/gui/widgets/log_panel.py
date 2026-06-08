"""Right-side runtime panel."""

from __future__ import annotations

from boss_crawler import EventType
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QPlainTextEdit, QProgressBar, QVBoxLayout, QWidget


class LogOutput(QPlainTextEdit):
    """Keep wheel scrolling behavior local to the log text area."""

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        scrollbar = self.verticalScrollBar()
        if scrollbar.maximum() <= 0:
            event.ignore()
            return
        super().wheelEvent(event)


class LogPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.status_group = QGroupBox("运行状态")
        status_form = QFormLayout(self.status_group)
        self.task_status_value = QLabel("空闲")
        self.page_value = QLabel("0 / 0")
        self.jobs_value = QLabel("0")
        self.unique_value = QLabel("0")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        status_form.addRow("任务状态", self.task_status_value)
        status_form.addRow("页数", self.page_value)
        status_form.addRow("职位总数", self.jobs_value)
        status_form.addRow("去重后职位数", self.unique_value)
        status_form.addRow("进度", self.progress_bar)

        self.log_group = QGroupBox("实时日志")
        log_layout = QVBoxLayout(self.log_group)
        self.log_output = LogOutput()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)

        layout.addWidget(self.status_group)
        layout.addWidget(self.log_group, 1)

    def append_log(self, message: str, event_type: EventType, created_at: str | None = None) -> None:
        prefix = created_at or "--:--:--"
        label_map = {
            EventType.INFO: "信息",
            EventType.WARNING: "警告",
            EventType.ERROR: "错误",
            EventType.PROGRESS: "进度",
            EventType.LOGIN_STATUS: "登录",
            EventType.TASK_STATUS: "任务",
            EventType.RESULT: "结果",
        }
        label = label_map.get(event_type, "日志")
        self.log_output.appendPlainText(f"[{prefix}] [{label}] {message}")
        scroll = self.log_output.verticalScrollBar()
        scroll.setValue(scroll.maximum())

    def update_progress(
        self,
        page: int,
        max_pages: int,
        total_jobs: int,
        unique_jobs: int,
        completed_jobs: int = 0,
    ) -> None:
        """更新进度信息。

        进度条基于去重后的总量（unique_jobs）与已完成条数（completed_jobs）：
        - 抓取详情模式：列表阶段 completed_jobs 为 0；每完成一条详情 +1
        - 快速模式：每页列表入库后按去重条数累计 completed_jobs
        """
        self.page_value.setText(f"{page} / {max_pages}")
        self.jobs_value.setText(str(total_jobs))
        self.unique_value.setText(str(unique_jobs))

        if unique_jobs <= 0:
            progress = 0
        else:
            progress = min(100, int(completed_jobs / unique_jobs * 100))

        self.progress_bar.setValue(progress)

    def set_task_status(self, value: str) -> None:
        self.task_status_value.setText(value)

    def clear_logs(self) -> None:
        self.log_output.clear()
