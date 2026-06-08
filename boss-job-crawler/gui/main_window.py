"""Main desktop window."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget

from boss_crawler import CrawlerConfig, CrawlerController, Event, EventType

from .login_dialog import LoginDialog
from .services.crawl_worker import CrawlWorker
from .styles import get_complete_stylesheet
from .task_complete_dialog import TaskCompleteDialog
from .widgets.log_panel import LogPanel
from .widgets.result_panel import ResultPanel
from .widgets.status_bar import StatusBarWidget
from .widgets.task_form import TaskFormWidget


class MainWindow(QMainWindow):
    """Main GUI surface for the crawler."""

    def __init__(self) -> None:
        super().__init__()
        self.default_config = CrawlerConfig()
        self.default_config.validate()
        self.config = CrawlerConfig()
        self.config.validate()
        self.controller = CrawlerController(config=self.config, event_handler=self._handle_backend_event)
        self.worker_thread: QThread | None = None
        self.worker: CrawlWorker | None = None
        self._last_output_file: str | None = None
        self._last_job: dict[str, object] = {}
        self.settings = None

        self.setWindowTitle("BOSS 直聘职位采集工具")
        self.resize(1100, 760)
        self.setMinimumSize(980, 680)
        self.setStyleSheet(get_complete_stylesheet())

        self.status_widget = StatusBarWidget()
        self.task_form = TaskFormWidget(self.config)
        self.log_panel = LogPanel()
        self.result_panel = ResultPanel()

        self._build_ui()
        self._connect_signals()
        self._create_menu()
        self._load_defaults()
        self._load_settings()
        self._append_startup_logs()

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(self.task_form)
        splitter.addWidget(self.log_panel)
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 700])

        root.addWidget(self.status_widget)
        root.addWidget(splitter, 1)
        root.addWidget(self.result_panel)
        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self.task_form.browse_output_requested.connect(self._choose_output_dir)
        self.task_form.open_login_requested.connect(self._open_login_page)
        self.task_form.check_login_requested.connect(self._check_login_status)
        self.task_form.clear_login_requested.connect(self._clear_login_state)
        self.task_form.relogin_requested.connect(self._relogin)
        self.task_form.reset_requested.connect(self._reset_form_defaults)
        self.task_form.start_requested.connect(self._start_crawl)
        self.task_form.stop_requested.connect(self._stop_crawl)
        self.task_form.clear_requested.connect(self._clear_runtime_view)

        self.result_panel.open_file_requested.connect(self._open_output_file)
        self.result_panel.open_dir_requested.connect(self._open_output_dir)
        self.result_panel.view_log_requested.connect(self._open_log_file)

    def _create_menu(self) -> None:
        refresh_action = QAction("刷新登录状态", self)
        refresh_action.triggered.connect(self._check_login_status)
        login_guide_action = QAction("登录引导", self)
        login_guide_action.triggered.connect(self._show_login_guide)
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)

        tools_menu = self.menuBar().addMenu("工具")
        tools_menu.addAction(refresh_action)
        tools_menu.addAction(login_guide_action)
        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction(about_action)

    def _load_defaults(self) -> None:
        from PySide6.QtCore import QSettings

        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(self.config.paths.project_root))
        self.settings = QSettings("InternPilot", "BossJobCrawler")
        self.task_form.apply_defaults(self.default_config, str(self.config.paths.output_dir), "职位结果.xlsx")
        self.result_panel.set_log_file(str(self.config.log_file))
        self.result_panel.set_output_path("")
        self._set_login_state(False, "未检查")
        self.status_widget.set_browser_status("就绪")
        self.status_widget.set_disclaimer_status("已确认")

    def _append_startup_logs(self) -> None:
        self.log_panel.append_log("程序已启动，开始爬取前请先检查登录状态。", EventType.INFO)
        self.log_panel.append_log(f"默认输出目录：{self.config.paths.output_dir}", EventType.INFO)

    def _load_settings(self) -> None:
        if self.settings is None:
            return
        geometry = self.settings.value("window/geometry")
        state = self.settings.value("form/state")
        if geometry:
            self.restoreGeometry(geometry)
        if isinstance(state, dict):
            self.task_form.set_form_state(state)

    def _save_settings(self) -> None:
        if self.settings is None:
            return
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("form/state", self.task_form.build_job_config())
        self.settings.sync()

    def _handle_backend_event(self, event: Event) -> None:
        self.log_panel.append_log(event.message, event.type, event.created_at)
        if event.type == EventType.LOGIN_STATUS:
            is_logged_in = bool(event.payload.get("is_logged_in", False))
            self._set_login_state(is_logged_in, event.message)
        elif event.type == EventType.TASK_STATUS:
            # 更新任务状态文本
            status_text = event.message
            self.log_panel.set_task_status(status_text)
        elif event.type == EventType.PROGRESS:
            # 更新进度信息（页数、职位数等）
            page = int(event.payload.get("page", 0))
            max_pages = int(event.payload.get("max_pages", 0))
            total_jobs = int(event.payload.get("total_jobs", 0))
            unique_jobs = int(event.payload.get("unique_jobs", 0))
            completed_jobs = int(event.payload.get("completed_jobs", 0))
            self.log_panel.update_progress(page, max_pages, total_jobs, unique_jobs, completed_jobs)
            # 同时更新任务状态为"运行中"
            if page > 0:
                self.log_panel.set_task_status(f"运行中 (第 {page}/{max_pages} 页)")
        elif event.type == EventType.INFO:
            # 处理特殊的 INFO 事件（如职位详情抓取进度）
            message = event.message
            if "获取职位详情" in message or "正在获取第" in message:
                # 提取进度信息并更新任务状态
                self.log_panel.set_task_status(f"运行中 - {message}")
            elif "正在加载第" in message:
                # 页面加载状态
                self.log_panel.set_task_status(f"运行中 - {message}")

    def _choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", self.task_form.output_dir())
        if directory:
            self.task_form.set_output_dir(directory)

    def _open_login_page(self) -> None:
        """打开登录页，不会因为异常而崩溃。"""
        if LoginDialog(self).exec() == LoginDialog.Rejected:
            return
        try:
            self.status_widget.set_browser_status("启动中")
            self.log_panel.append_log("正在启动浏览器...", EventType.INFO)
            
            self.controller.open_login_page()
            
            self.status_widget.set_browser_status("运行中")
            self.log_panel.append_log("✓ 浏览器已启动", EventType.INFO)
            self.log_panel.append_log("  BOSS 直聘登录页已打开", EventType.INFO)
            self.log_panel.append_log("  请在浏览器中完成登录（扫码或验证码）", EventType.INFO)
            self.log_panel.append_log("  登录完成后，点击'检查状态'按钮验证", EventType.INFO)
            
        except Exception as exc:
            error_msg = str(exc)
            
            # 检查是否是用户关闭浏览器
            if (
                "已关闭" in error_msg
                or "连接已断开" in error_msg
                or "not defined" in error_msg.lower()
                or "browser is not" in error_msg.lower()
            ):
                self.status_widget.set_browser_status("已关闭")
                self.log_panel.append_log("ℹ 浏览器窗口已关闭", EventType.INFO)
                self.log_panel.append_log("  如需登录，请重新点击'打开登录页'", EventType.INFO)
                # 不显示错误弹窗，这是正常的用户操作
            else:
                # 真正的错误
                self.status_widget.set_browser_status("异常")
                error_msg_display = f"✗ 打开登录页失败：{exc}"
                self.log_panel.append_log(error_msg_display, EventType.ERROR)
                self._show_error("打开登录页失败", str(exc))

    def _check_login_status(self) -> None:
        """检查登录状态，不会因为异常而崩溃。"""
        try:
            self.status_widget.set_login_status("检查中", False)
            self.log_panel.append_log("正在检查登录状态...", EventType.INFO)
            
            status = self.controller.login_manager.check_login_status()
            is_logged_in = status.is_logged_in
            
            if is_logged_in:
                # 已登录，显示成功信息
                self.log_panel.append_log("✓ 登录状态检查完成：已登录", EventType.INFO)
                self.log_panel.append_log(f"  {status.message}", EventType.INFO)
                
                # 如果浏览器在运行，保存会话
                if self.controller.login_manager.browser.page is not None:
                    try:
                        self.controller.login_manager.save_session()
                        self.log_panel.append_log("  登录状态已保存到本地", EventType.INFO)
                    except Exception as save_exc:
                        self.log_panel.append_log(f"  保存会话失败：{save_exc}", EventType.WARNING)
            else:
                # 未登录，显示提示信息
                self.log_panel.append_log("✗ 登录状态检查完成：未登录", EventType.WARNING)
                self.log_panel.append_log(f"  {status.message}", EventType.WARNING)
                self.log_panel.append_log("  提示：请先点击'打开登录页'完成登录", EventType.INFO)
            
            self._set_login_state(is_logged_in, "已登录" if is_logged_in else "未登录")
            
        except Exception as exc:
            error_msg = str(exc)
            
            # 检查是否是浏览器关闭导致的
            if (
                "已关闭" in error_msg
                or "连接已断开" in error_msg
                or "not defined" in error_msg.lower()
                or "browser is not" in error_msg.lower()
            ):
                self.controller.login_manager.browser.release()
                self._set_login_state(False, "浏览器已关闭")
                self.log_panel.append_log("ℹ 浏览器窗口已关闭", EventType.INFO)
                self.log_panel.append_log("  可点击「检查状态」读取本地登录 cookie", EventType.INFO)
                self.status_widget.set_login_status("浏览器已关闭", False)
                self.status_widget.set_browser_status("已关闭")
            else:
                # 真正的错误
                self._set_login_state(False, "检查失败")
                error_msg_display = f"✗ 检查登录失败：{exc}"
                self.log_panel.append_log(error_msg_display, EventType.ERROR)
                self.status_widget.set_login_status("检查失败", False)

    def _clear_login_state(self) -> None:
        """清除登录状态，不会因为异常而崩溃。"""
        try:
            self.log_panel.append_log("正在清除登录状态...", EventType.INFO)
            self.controller.login_manager.clear_session()
            self._set_login_state(False, "登录状态已清除")
            self.status_widget.set_browser_status("就绪")
            self.log_panel.append_log("✓ 登录状态已清除", EventType.INFO)
            self.log_panel.append_log("  浏览器会话已关闭", EventType.INFO)
            self.log_panel.append_log("  本地登录记录已删除", EventType.INFO)
        except Exception as exc:
            error_msg = f"✗ 清除登录失败：{exc}"
            self.log_panel.append_log(error_msg, EventType.ERROR)
            self._show_error("清除登录失败", str(exc))

    def _reset_form_defaults(self) -> None:
        self.task_form.apply_defaults(self.default_config, str(self.config.paths.output_dir), "职位结果.xlsx")
        self.log_panel.append_log("参数配置已恢复为默认值。", EventType.INFO)

    def _relogin(self) -> None:
        self._clear_login_state()
        self._open_login_page()

    def _start_crawl(self) -> None:
        if self.worker_thread is not None:
            return
        if not self.task_form.validate_inputs(self):
            return

        job = self.task_form.build_job_config()
        self._last_job = dict(job)
        self._apply_form_config(job)
        self._save_settings()
        self._clear_runtime_view(clear_logs=False)
        self.log_panel.set_task_status("准备任务")
        self.log_panel.append_log(f"开始执行任务，关键词：{job['keyword']}。", EventType.INFO)
        self.task_form.set_running(True)
        self.result_panel.set_busy(True)

        self.worker_thread = QThread(self)
        self.worker = CrawlWorker(
            self.controller, 
            str(job["keyword"]), 
            int(job["max_pages"]),
            bool(job.get("fetch_details", True)),  # 传递 fetch_details 参数
            str(job.get("file_template", ""))  # 传递文件名模板
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.event_received.connect(self._handle_backend_event)
        # 注意：不再直接连接 progress_changed，因为 event_received 已经处理了进度更新
        # self.worker.progress_changed.connect(self.log_panel.update_progress)
        self.worker.finished.connect(self._handle_crawl_finished)
        self.worker.failed.connect(self._handle_crawl_failed)
        self.worker.stopped.connect(self._handle_crawl_stopped)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker.stopped.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._cleanup_worker)
        self.worker_thread.start()

    def _stop_crawl(self) -> None:
        if self.worker is None:
            return
        self.task_form.set_stopping()
        self.log_panel.append_log("已请求停止任务。", EventType.WARNING)
        self.worker.stop()

    def _clear_runtime_view(self, clear_logs: bool = True) -> None:
        if clear_logs:
            self.log_panel.clear_logs()
        self.log_panel.update_progress(0, 0, 0, 0)
        self.log_panel.set_task_status("空闲")
        self.result_panel.reset()

    def _apply_form_config(self, job: dict[str, object]) -> None:
        self.config.retry.page_delay_seconds = int(job["page_delay_seconds"])
        self.config.retry.request_timeout_seconds = int(job["request_timeout_seconds"])
        self.config.retry.max_retries = int(job["max_retries"])
        self.config.runtime.headless = bool(job["headless"])
        self.config.runtime.enable_deduplication = bool(job["enable_deduplication"])
        self.config.runtime.city_code = str(job["city_code"])
        self.config.paths.output_dir = Path(str(job["output_dir"]))
        self.config.validate()

    def _handle_crawl_finished(self, result: object) -> None:
        total_jobs = int(getattr(result, "total_jobs", 0))
        unique_jobs = int(getattr(result, "unique_jobs", 0))
        pages = int(getattr(result, "pages_crawled", 0))
        output_file = getattr(result, "output_file", None)
        error_message = getattr(result, "error_message", None)
        duration = float(getattr(result, "crawl_duration", 0.0))

        self.task_form.set_running(False)
        self.result_panel.set_busy(False)
        self.log_panel.update_progress(
            pages,
            self.task_form.max_pages(),
            total_jobs,
            unique_jobs,
            completed_jobs=unique_jobs,
        )
        self.result_panel.update_result(total_jobs, unique_jobs, duration, output_file or "")
        self._last_output_file = output_file

        if error_message:
            self.log_panel.set_task_status("已完成，带提示")
            self.log_panel.append_log(str(error_message), EventType.WARNING)
            self._show_info("任务已完成，但有提示", str(error_message))
        else:
            self.log_panel.set_task_status("已完成")
            self.log_panel.append_log("任务已完成。", EventType.RESULT)
            self._show_completion_dialog(total_jobs, unique_jobs, output_file or "")

    def _handle_crawl_failed(self, message: str) -> None:
        self.task_form.set_running(False)
        self.result_panel.set_busy(False)
        self.log_panel.set_task_status("失败")
        self.log_panel.append_log(message, EventType.ERROR)
        self._show_error("爬取失败", message)

    def _handle_crawl_stopped(self) -> None:
        self.task_form.set_running(False)
        self.result_panel.set_busy(False)
        self.log_panel.set_task_status("已停止")
        self.log_panel.append_log("任务已停止。", EventType.WARNING)

    def _cleanup_worker(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
        self.worker = None
        self.worker_thread = None

    def _set_login_state(self, is_logged_in: bool, message: str) -> None:
        status_text = "已登录" if is_logged_in else "未登录"
        self.status_widget.set_login_status(status_text, is_logged_in)
        self.task_form.set_login_state(is_logged_in, message)

    def _open_output_file(self) -> None:
        if not self._last_output_file:
            self._show_info("暂无文件", "当前还没有可打开的导出文件。")
            return
        self._open_path(self._last_output_file)

    def _open_output_dir(self) -> None:
        self._open_path(self.task_form.output_dir())

    def _open_log_file(self) -> None:
        self._open_path(str(self.config.log_file))

    def _open_path(self, path: str) -> None:
        if not path:
            self._show_info("无可打开内容", "目标路径为空。")
            return

        target = Path(path)
        if not target.exists():
            self._show_error("路径不存在", str(target))
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(target))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(target)], check=False)
            else:
                subprocess.run(["xdg-open", str(target)], check=False)
        except Exception as exc:
            self._show_error("打开路径失败", str(exc))

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def _show_info(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def _show_login_guide(self) -> None:
        LoginDialog(self).exec()

    def _show_about(self) -> None:
        self._show_info("关于", "BOSS 直聘职位采集工具\n\n提供登录引导、任务控制、实时日志和结果查看。")

    def _show_completion_dialog(self, total_jobs: int, unique_jobs: int, output_path: str) -> None:
        dialog = TaskCompleteDialog(
            keyword=str(self._last_job.get("keyword", "")),
            city=str(self._last_job.get("city", "")),
            pages=int(self._last_job.get("max_pages", self.task_form.max_pages())),
            total_jobs=total_jobs,
            unique_jobs=unique_jobs,
            output_path=output_path,
            parent=self,
        )
        if dialog.open_file_button is not None:
            dialog.open_file_button.clicked.connect(self._open_output_file)
        if dialog.open_dir_button is not None:
            dialog.open_dir_button.clicked.connect(self._open_output_dir)
        dialog.exec()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.worker_thread is not None:
            answer = QMessageBox.question(
                self,
                "任务仍在运行",
                "当前仍有爬取任务在运行，是否停止任务并关闭程序？",
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
            self._stop_crawl()
            if self.worker_thread is not None:
                self.worker_thread.quit()
                self.worker_thread.wait(3000)
        self._save_settings()
        super().closeEvent(event)
