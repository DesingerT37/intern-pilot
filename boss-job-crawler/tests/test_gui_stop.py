"""测试 GUI 停止功能的集成测试。"""

import time
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from boss_crawler import CrawlerConfig, LoginStatus


def test_gui_stop_button_integration(tmp_path, qtbot):
    """测试 GUI 停止按钮的集成功能。"""
    # 延迟导入以避免在没有 Qt 环境时失败
    from boss_job_crawler.gui.main_window import MainWindow
    from boss_job_crawler.gui.services.crawl_worker import CrawlWorker

    # 创建临时配置
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.retry.page_delay_seconds = 0
    config.retry.request_timeout_seconds = 1
    config.validate()

    # 创建主窗口
    window = MainWindow()
    window.config = config
    qtbot.addWidget(window)

    # Mock 登录状态
    class _FakeLoginManager:
        def check_login_status(self):
            return LoginStatus(is_logged_in=True, message="已登录")

        def save_session(self):
            pass

    window.controller.login_manager = _FakeLoginManager()

    # 设置表单
    window.task_form.keyword_input.setText("python")
    window.task_form.city_input.setCurrentText("北京")
    window.task_form.max_pages_input.setValue(5)
    window.task_form.set_login_state(True, "已登录")

    # 验证初始状态
    assert window.task_form.start_button.isEnabled()
    assert not window.task_form.stop_button.isEnabled()

    # 模拟点击开始按钮
    stopped_signal_received = []

    def on_stopped():
        stopped_signal_received.append(True)

    # 启动任务
    window._start_crawl()

    # 验证运行状态
    assert not window.task_form.start_button.isEnabled()
    assert window.task_form.stop_button.isEnabled()
    assert window.worker is not None

    # 连接停止信号
    if window.worker:
        window.worker.stopped.connect(on_stopped)

    # 等待一小段时间后点击停止
    QTimer.singleShot(100, window._stop_crawl)

    # 等待停止完成
    qtbot.waitUntil(lambda: len(stopped_signal_received) > 0 or window.worker is None, timeout=3000)

    # 验证停止后的状态
    assert window.task_form.start_button.isEnabled()
    assert not window.task_form.stop_button.isEnabled()


if __name__ == "__main__":
    import pytest
    import sys

    sys.exit(pytest.main([__file__, "-v", "-s"]))
