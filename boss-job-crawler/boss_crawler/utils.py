"""通用工具函数。"""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

from .config import CrawlerConfig


def setup_logging(config: CrawlerConfig) -> Logger:
    """初始化项目日志。"""
    config.validate()

    logger = logging.getLogger("boss_crawler")
    logger.setLevel(getattr(logging, config.runtime.log_level.upper()))
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def ensure_runtime_directories(config: CrawlerConfig) -> None:
    """确保运行目录存在。"""
    config.paths.ensure_directories()


def build_output_file_path(output_dir: Path, keyword: str) -> Path:
    """构造默认输出文件路径。"""
    safe_keyword = keyword.strip().replace(" ", "_") or "jobs"
    return output_dir / f"boss_{safe_keyword}.xlsx"
