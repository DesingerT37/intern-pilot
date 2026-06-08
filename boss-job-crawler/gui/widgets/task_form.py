"""Left-side task form widget."""

from __future__ import annotations

from pathlib import Path

from boss_crawler import CrawlerConfig, HOT_CITY_NAMES, get_city_code
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class NoWheelComboBox(QComboBox):
    """Keep mouse-wheel scrolling on the parent form instead of changing selection."""

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()


class NoWheelSpinBox(QSpinBox):
    """Keep mouse-wheel scrolling on the parent form instead of changing values."""

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()


class TaskFormWidget(QScrollArea):
    browse_output_requested = Signal()
    open_login_requested = Signal()
    check_login_requested = Signal()
    clear_login_requested = Signal()
    relogin_requested = Signal()
    start_requested = Signal()
    stop_requested = Signal()
    clear_requested = Signal()
    reset_requested = Signal()

    def __init__(self, config: CrawlerConfig) -> None:
        super().__init__()
        self._logged_in = False

        container = QWidget()
        self.setWidget(container)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("例如：Python 实习生")

        self.city_input = NoWheelComboBox()
        self.city_input.setEditable(True)
        self.city_input.addItems(HOT_CITY_NAMES)
        self.city_input.setInsertPolicy(QComboBox.NoInsert)

        self.city_hint_label = QLabel("请从下拉列表中选择城市。目前内置的是 BOSS 直聘热门城市，避免无效地区导致请求失败。")
        self.city_hint_label.setWordWrap(True)

        self.max_pages_input = NoWheelSpinBox()
        self.max_pages_input.setRange(1, 20)

        layout.addWidget(self._build_search_group())
        layout.addWidget(self._build_runtime_group(config))
        layout.addWidget(self._build_export_group())
        layout.addWidget(self._build_login_group())
        layout.addWidget(self._build_action_group())
        layout.addStretch(1)

        self.apply_defaults(config, str(config.paths.output_dir), "职位结果.xlsx")

    def _build_search_group(self) -> QGroupBox:
        group = QGroupBox("搜索条件")
        form = QFormLayout(group)
        form.addRow("关键词", self.keyword_input)
        form.addRow("城市", self.city_input)
        form.addRow("页数", self.max_pages_input)
        form.addRow("", self.city_hint_label)
        return group

    def _build_runtime_group(self, config: CrawlerConfig) -> QGroupBox:
        group = QGroupBox("爬取设置")
        form = QFormLayout(group)

        self.page_delay_input = NoWheelSpinBox()
        self.page_delay_input.setRange(0, 60)
        self.page_delay_input.setValue(config.retry.page_delay_seconds)

        self.request_timeout_input = NoWheelSpinBox()
        self.request_timeout_input.setRange(1, 120)
        self.request_timeout_input.setValue(config.retry.request_timeout_seconds)

        self.max_retries_input = NoWheelSpinBox()
        self.max_retries_input.setRange(0, 10)
        self.max_retries_input.setValue(config.retry.max_retries)

        self.dedup_checkbox = QCheckBox("启用去重")
        self.headless_checkbox = QCheckBox("无头模式")
        
        # 新增：是否抓取职位描述
        self.fetch_details_checkbox = QCheckBox("抓取职位描述（推荐）")
        self.fetch_details_checkbox.setChecked(True)  # 默认开启
        self.fetch_details_checkbox.setToolTip(
            "勾选后会访问每个职位的详情页获取完整描述\n"
            "适用于简历优化分析，但会增加抓取时间\n"
            "预计时间：每页 30-60 秒（15 个职位）"
        )

        form.addRow("翻页等待", self.page_delay_input)
        form.addRow("请求超时", self.request_timeout_input)
        form.addRow("最大重试次数", self.max_retries_input)
        form.addRow("", self.dedup_checkbox)
        form.addRow("", self.headless_checkbox)
        form.addRow("", self.fetch_details_checkbox)
        return group

    def _build_export_group(self) -> QGroupBox:
        group = QGroupBox("导出设置")
        form = QFormLayout(group)

        self.output_dir_input = QLineEdit()
        self.file_template_input = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_output_requested.emit)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        row_layout.addWidget(self.output_dir_input, 1)
        row_layout.addWidget(browse_button)

        form.addRow("输出目录", row)
        form.addRow("文件名", self.file_template_input)
        return group

    def _build_login_group(self) -> QGroupBox:
        group = QGroupBox("登录")
        layout = QVBoxLayout(group)
        self.login_state_label = QLabel("当前状态：未检查")
        self.login_hint_label = QLabel("登录将在浏览器中完成，本程序不会保存明文密码。")
        self.login_hint_label.setWordWrap(True)

        row1 = QHBoxLayout()
        open_button = QPushButton("打开登录页")
        check_button = QPushButton("检查状态")
        open_button.clicked.connect(self.open_login_requested.emit)
        check_button.clicked.connect(self.check_login_requested.emit)
        row1.addWidget(open_button)
        row1.addWidget(check_button)

        row2 = QHBoxLayout()
        clear_button = QPushButton("清除登录")
        relogin_button = QPushButton("重新登录")
        clear_button.clicked.connect(self.clear_login_requested.emit)
        relogin_button.clicked.connect(self.relogin_requested.emit)
        row2.addWidget(clear_button)
        row2.addWidget(relogin_button)

        layout.addWidget(self.login_state_label)
        layout.addWidget(self.login_hint_label)
        layout.addLayout(row1)
        layout.addLayout(row2)
        return group

    def _build_action_group(self) -> QGroupBox:
        group = QGroupBox("操作")
        layout = QVBoxLayout(group)

        primary_row = QHBoxLayout()
        secondary_row = QHBoxLayout()

        self.start_button = QPushButton("开始爬取")
        self.stop_button = QPushButton("停止")
        self.clear_button = QPushButton("清空结果")
        self.reset_button = QPushButton("恢复默认配置")

        self.start_button.clicked.connect(self.start_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.clear_button.clicked.connect(self.clear_requested.emit)
        self.reset_button.clicked.connect(self.reset_requested.emit)
        self.stop_button.setEnabled(False)

        primary_row.addWidget(self.start_button)
        primary_row.addWidget(self.stop_button)
        primary_row.addWidget(self.clear_button)
        secondary_row.addWidget(self.reset_button)

        layout.addLayout(primary_row)
        layout.addLayout(secondary_row)
        return group

    def apply_defaults(self, config: CrawlerConfig, output_dir: str, file_template: str) -> None:
        self.keyword_input.clear()
        self.city_input.setCurrentText("北京")
        self.max_pages_input.setValue(3)
        self.page_delay_input.setValue(config.retry.page_delay_seconds)
        self.request_timeout_input.setValue(config.retry.request_timeout_seconds)
        self.max_retries_input.setValue(config.retry.max_retries)
        self.dedup_checkbox.setChecked(config.runtime.enable_deduplication)
        self.headless_checkbox.setChecked(config.runtime.headless)
        self.fetch_details_checkbox.setChecked(True)  # 默认开启职位详情抓取
        self.output_dir_input.setText(output_dir)
        self.file_template_input.setText(file_template)

    def set_runtime_config(self, config: CrawlerConfig) -> None:
        self.dedup_checkbox.setChecked(config.runtime.enable_deduplication)
        self.headless_checkbox.setChecked(config.runtime.headless)
        self.fetch_details_checkbox.setChecked(True)  # 默认开启
        self.stop_button.setEnabled(False)

    def set_output_dir(self, value: str) -> None:
        self.output_dir_input.setText(value)

    def output_dir(self) -> str:
        return self.output_dir_input.text().strip()

    def city(self) -> str:
        return self.city_input.currentText().strip()

    def set_file_template(self, value: str) -> None:
        self.file_template_input.setText(value)

    def file_template(self) -> str:
        return self.file_template_input.text().strip()

    def set_login_state(self, logged_in: bool, message: str) -> None:
        self._logged_in = logged_in
        self.login_state_label.setText(f"当前状态：{message}")
        self.start_button.setEnabled(logged_in and not self.stop_button.isEnabled())

    def set_running(self, running: bool) -> None:
        self.start_button.setEnabled(self._logged_in and not running)
        self.stop_button.setEnabled(running)
        self.reset_button.setEnabled(not running)
        for widget in (
            self.keyword_input,
            self.city_input,
            self.max_pages_input,
            self.page_delay_input,
            self.request_timeout_input,
            self.max_retries_input,
            self.dedup_checkbox,
            self.headless_checkbox,
            self.fetch_details_checkbox,
            self.output_dir_input,
            self.file_template_input,
        ):
            widget.setEnabled(not running)

    def set_stopping(self) -> None:
        self.stop_button.setEnabled(False)

    def build_job_config(self) -> dict[str, object]:
        city_name = self.city()
        return {
            "keyword": self.keyword_input.text().strip(),
            "city": city_name,
            "city_code": get_city_code(city_name) or "",
            "max_pages": self.max_pages_input.value(),
            "page_delay_seconds": self.page_delay_input.value(),
            "request_timeout_seconds": self.request_timeout_input.value(),
            "max_retries": self.max_retries_input.value(),
            "enable_deduplication": self.dedup_checkbox.isChecked(),
            "headless": self.headless_checkbox.isChecked(),
            "fetch_details": self.fetch_details_checkbox.isChecked(),
            "output_dir": self.output_dir(),
            "file_template": self.file_template_input.text().strip(),
        }

    def validate_inputs(self, parent: QWidget) -> bool:
        job = self.build_job_config()
        if not job["keyword"]:
            QMessageBox.warning(parent, "缺少关键词", "请输入搜索关键词。")
            return False
        if not job["city"]:
            QMessageBox.warning(parent, "缺少城市", "请选择城市。")
            return False
        if not job["city_code"]:
            QMessageBox.warning(parent, "城市无效", "请选择下拉列表中的热门城市。")
            return False
        if not job["output_dir"]:
            QMessageBox.warning(parent, "缺少输出目录", "请选择输出目录。")
            return False

        Path(str(job["output_dir"])).mkdir(parents=True, exist_ok=True)
        return True

    def max_pages(self) -> int:
        return self.max_pages_input.value()

    def set_form_state(self, state: dict[str, object]) -> None:
        self.keyword_input.setText(str(state.get("keyword", "")))
        city_name = str(state.get("city", "北京"))
        if city_name not in HOT_CITY_NAMES:
            city_name = "北京"
        self.city_input.setCurrentText(city_name)
        self.max_pages_input.setValue(int(state.get("max_pages", 3)))
        self.page_delay_input.setValue(int(state.get("page_delay_seconds", self.page_delay_input.value())))
        self.request_timeout_input.setValue(
            int(state.get("request_timeout_seconds", self.request_timeout_input.value()))
        )
        self.max_retries_input.setValue(int(state.get("max_retries", self.max_retries_input.value())))
        self.dedup_checkbox.setChecked(bool(state.get("enable_deduplication", self.dedup_checkbox.isChecked())))
        self.headless_checkbox.setChecked(bool(state.get("headless", self.headless_checkbox.isChecked())))
        self.fetch_details_checkbox.setChecked(bool(state.get("fetch_details", True)))  # 默认开启
        self.output_dir_input.setText(str(state.get("output_dir", self.output_dir_input.text())))
        self.file_template_input.setText(str(state.get("file_template", self.file_template_input.text())))
