"""配置模型与初始化逻辑。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .exceptions import ConfigError


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass
class PathConfig:
    """项目路径配置。"""

    project_root: Path = field(default_factory=_project_root)
    output_dir: Path = field(default_factory=lambda: _project_root() / "output")
    log_dir: Path = field(default_factory=lambda: _project_root() / "logs")
    session_dir: Path = field(default_factory=lambda: _project_root() / "sessions")

    def ensure_directories(self) -> None:
        for path in (self.output_dir, self.log_dir, self.session_dir):
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class RetryConfig:
    """重试相关配置。"""

    max_retries: int = 3
    page_delay_seconds: int = 3
    request_timeout_seconds: int = 10
    browser_timeout_seconds: int = 30

    def validate(self) -> None:
        if self.max_retries < 0:
            raise ConfigError("max_retries 不能小于 0")
        if self.page_delay_seconds < 0:
            raise ConfigError("page_delay_seconds 不能小于 0")
        if self.request_timeout_seconds <= 0:
            raise ConfigError("request_timeout_seconds 必须大于 0")
        if self.browser_timeout_seconds <= 0:
            raise ConfigError("browser_timeout_seconds 必须大于 0")


@dataclass
class RuntimeConfig:
    """运行时配置。"""

    headless: bool = False
    city_code: str = "100010000"
    enable_deduplication: bool = True
    log_level: str = "INFO"
    api_url_pattern: str = r"https://www\.zhipin\.com/web/geek/job"
    browser_name: str = "chrome"

    def validate(self) -> None:
        if not self.city_code.strip():
            raise ConfigError("city_code 不能为空")
        if not self.api_url_pattern.strip():
            raise ConfigError("api_url_pattern 不能为空")
        if self.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigError("log_level 不合法")


@dataclass
class CrawlerConfig:
    """总配置对象。"""

    paths: PathConfig = field(default_factory=PathConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    def validate(self) -> None:
        self.paths.ensure_directories()
        self.retry.validate()
        self.runtime.validate()

    @property
    def log_file(self) -> Path:
        return self.paths.log_dir / "boss_crawler.log"
