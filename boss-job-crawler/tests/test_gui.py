from PySide6.QtCore import QSettings

from boss_crawler import CrawlerConfig
from gui.main_window import MainWindow
from gui.widgets.log_panel import LogOutput
from gui.widgets.task_form import NoWheelComboBox, NoWheelSpinBox, TaskFormWidget


def test_task_form_login_state_controls_start(qtbot):
    form = TaskFormWidget(config=CrawlerConfig())
    qtbot.addWidget(form)

    form.set_login_state(False, "Not logged in")
    assert not form.start_button.isEnabled()

    form.set_login_state(True, "Logged in")
    assert form.start_button.isEnabled()


def test_main_window_saves_form_settings(qtbot, tmp_path, monkeypatch):
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.validate()
    monkeypatch.setattr("gui.main_window.CrawlerConfig", lambda: config)

    window = MainWindow()
    qtbot.addWidget(window)
    window.task_form.keyword_input.setText("python")
    window.task_form.city_input.setCurrentText("上海")
    window.task_form.output_dir_input.setText(str(tmp_path / "output"))
    window._save_settings()
    window.close()

    restored = MainWindow()
    qtbot.addWidget(restored)
    assert restored.task_form.keyword_input.text() == "python"
    assert restored.task_form.city_input.currentText() == "上海"
    assert restored.task_form.output_dir_input.text() == str(tmp_path / "output")


def test_result_panel_reset_after_clear(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.result_panel.update_result(10, 8, 2.5, "out.xlsx")
    window._clear_runtime_view()
    assert window.result_panel.total_value.text() == "0"
    assert window.result_panel.path_value.text() == "-"


def test_task_form_reset_defaults(qtbot):
    config = CrawlerConfig()
    form = TaskFormWidget(config=config)
    qtbot.addWidget(form)

    form.keyword_input.setText("golang")
    form.city_input.setCurrentText("深圳")
    form.max_pages_input.setValue(7)
    form.page_delay_input.setValue(12)
    form.request_timeout_input.setValue(18)
    form.max_retries_input.setValue(5)
    form.dedup_checkbox.setChecked(True)
    form.headless_checkbox.setChecked(True)
    form.output_dir_input.setText("D:/temp/output")
    form.file_template_input.setText("custom.xlsx")

    form.apply_defaults(config, str(config.paths.output_dir), "职位结果.xlsx")

    assert form.keyword_input.text() == ""
    assert form.city_input.currentText() == "北京"
    assert form.max_pages_input.value() == 3
    assert form.page_delay_input.value() == config.retry.page_delay_seconds
    assert form.request_timeout_input.value() == config.retry.request_timeout_seconds
    assert form.max_retries_input.value() == config.retry.max_retries
    assert form.dedup_checkbox.isChecked() == config.runtime.enable_deduplication
    assert form.headless_checkbox.isChecked() == config.runtime.headless
    assert form.output_dir_input.text() == str(config.paths.output_dir)
    assert form.file_template_input.text() == "职位结果.xlsx"


def test_task_form_uses_no_wheel_inputs(qtbot):
    form = TaskFormWidget(config=CrawlerConfig())
    qtbot.addWidget(form)

    assert isinstance(form.city_input, NoWheelComboBox)
    assert isinstance(form.max_pages_input, NoWheelSpinBox)
    assert isinstance(form.page_delay_input, NoWheelSpinBox)
    assert isinstance(form.request_timeout_input, NoWheelSpinBox)
    assert isinstance(form.max_retries_input, NoWheelSpinBox)


def test_log_panel_uses_custom_log_output(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert isinstance(window.log_panel.log_output, LogOutput)
