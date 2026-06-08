"""Shared UI styles for the desktop app."""

from __future__ import annotations

from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent / "assets"


def _asset_url(name: str) -> str:
    return (ASSET_DIR / name).as_posix()

COLORS = {
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_pressed": "#1e40af",
    "primary_light": "#dbeafe",
    "success": "#10b981",
    "success_hover": "#059669",
    "success_light": "#d1fae5",
    "warning": "#f59e0b",
    "warning_hover": "#d97706",
    "warning_light": "#fef3c7",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "danger_light": "#fee2e2",
    "neutral": "#6b7280",
    "neutral_hover": "#4b5563",
    "neutral_light": "#f3f4f6",
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8fafc",
    "bg_tertiary": "#f1f5f9",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_tertiary": "#94a3b8",
    "border": "#e2e8f0",
    "border_focus": "#60a5fa",
}


def get_main_window_style() -> str:
    return f"""
        QMainWindow {{
            background-color: {COLORS['bg_secondary']};
        }}

        QWidget {{
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 13px;
            color: {COLORS['text_primary']};
        }}

        QMenuBar {{
            background-color: {COLORS['bg_primary']};
            border-bottom: 1px solid {COLORS['border']};
            padding: 4px 8px;
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: 6px;
        }}

        QMenuBar::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary']};
        }}

        QMenu {{
            background-color: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 6px;
        }}

        QMenu::item {{
            padding: 8px 24px;
            border-radius: 6px;
        }}

        QMenu::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary']};
        }}
    """


def get_group_box_style() -> str:
    return f"""
        QGroupBox {{
            background-color: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            font-size: 14px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 6px;
            color: {COLORS['text_primary']};
        }}
    """


def get_button_style(color_type: str = "primary") -> str:
    palette = {
        "primary": (COLORS["primary"], COLORS["primary_hover"], COLORS["primary_pressed"], "#ffffff"),
        "success": (COLORS["success"], COLORS["success_hover"], COLORS["success"], "#ffffff"),
        "warning": (COLORS["warning"], COLORS["warning_hover"], COLORS["warning"], "#ffffff"),
        "danger": (COLORS["danger"], COLORS["danger_hover"], COLORS["danger"], "#ffffff"),
        "neutral": (COLORS["bg_primary"], COLORS["bg_tertiary"], COLORS["bg_tertiary"], COLORS["text_primary"]),
    }
    base, hover, pressed, fg = palette.get(color_type, palette["primary"])

    border = COLORS["border"] if color_type == "neutral" else "transparent"
    return f"""
        QPushButton {{
            background-color: {base};
            color: {fg};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 18px;
        }}

        QPushButton:hover {{
            background-color: {hover};
        }}

        QPushButton:pressed {{
            background-color: {pressed};
        }}

        QPushButton:disabled {{
            background-color: {COLORS['neutral_light']};
            color: {COLORS['text_tertiary']};
            border-color: {COLORS['border']};
        }}
    """


def get_input_style() -> str:
    combo_arrow = _asset_url("combo_arrow_down.svg")
    spin_up_arrow = _asset_url("spin_arrow_up.svg")
    spin_down_arrow = _asset_url("spin_arrow_down.svg")
    return f"""
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {COLORS['text_primary']};
        }}

        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 2px solid {COLORS['border_focus']};
            padding: 7px 11px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border: none;
            border-left: 1px solid {COLORS['border']};
            background-color: {COLORS['bg_tertiary']};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}

        QComboBox::down-arrow {{
            image: url({combo_arrow});
            width: 12px;
            height: 12px;
        }}

        QSpinBox::up-button, QSpinBox::down-button {{
            subcontrol-origin: border;
            width: 24px;
            border: none;
            background-color: {COLORS['bg_tertiary']};
        }}

        QSpinBox::up-button {{
            border-left: 1px solid {COLORS['border']};
            border-top-right-radius: 6px;
        }}

        QSpinBox::down-button {{
            border-left: 1px solid {COLORS['border']};
            border-top: 1px solid {COLORS['border']};
            border-bottom-right-radius: 6px;
        }}

        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QComboBox::drop-down:hover {{
            background-color: {COLORS['primary_light']};
        }}

        QSpinBox::up-arrow {{
            image: url({spin_up_arrow});
            width: 12px;
            height: 12px;
        }}

        QSpinBox::down-arrow {{
            image: url({spin_down_arrow});
            width: 12px;
            height: 12px;
        }}
    """


def get_checkbox_style() -> str:
    return f"""
        QCheckBox {{
            spacing: 8px;
            color: {COLORS['text_primary']};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {COLORS['border']};
            border-radius: 4px;
            background-color: {COLORS['bg_primary']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
    """


def get_progress_bar_style() -> str:
    return f"""
        QProgressBar {{
            background-color: {COLORS['bg_tertiary']};
            border: none;
            border-radius: 6px;
            height: 10px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {COLORS['primary']},
                stop: 1 #60a5fa
            );
            border-radius: 6px;
        }}
    """


def get_text_edit_style() -> str:
    return f"""
        QPlainTextEdit {{
            background-color: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 12px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 12px;
            color: {COLORS['text_primary']};
        }}
    """


def get_scroll_area_style() -> str:
    return f"""
        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollBar:vertical {{
            background: {COLORS['bg_tertiary']};
            width: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: {COLORS['neutral']};
            border-radius: 5px;
            min-height: 28px;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
    """


def get_label_style() -> str:
    return f"""
        QLabel {{
            color: {COLORS['text_primary']};
        }}

        QFormLayout QLabel {{
            color: {COLORS['text_secondary']};
            font-weight: 500;
        }}
    """


def get_dialog_style() -> str:
    return f"""
        QDialog {{
            background-color: {COLORS['bg_primary']};
        }}

        QDialogButtonBox QPushButton {{
            min-width: 88px;
        }}
    """


def get_splitter_style() -> str:
    return f"""
        QSplitter::handle {{
            background-color: {COLORS['border']};
            width: 1px;
        }}

        QSplitter::handle:hover {{
            background-color: {COLORS['primary']};
        }}
    """


def get_complete_stylesheet() -> str:
    return "\n".join(
        [
            get_main_window_style(),
            get_group_box_style(),
            get_button_style("primary"),
            get_input_style(),
            get_checkbox_style(),
            get_progress_bar_style(),
            get_text_edit_style(),
            get_scroll_area_style(),
            get_label_style(),
            get_dialog_style(),
            get_splitter_style(),
        ]
    )
