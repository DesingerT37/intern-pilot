"""BOSS直聘爬虫后端基础包。"""

from .config import CrawlerConfig, PathConfig, RetryConfig, RuntimeConfig
from .controller import CrawlerController
from .cities import HOT_CITY_NAMES, HOT_CITY_OPTIONS, get_city_code
from .events import Event, EventType, TaskStatus
from .exceptions import (
    BossCrawlerError,
    BrowserError,
    ConfigError,
    ExportError,
    ListenerError,
    LoginError,
    ParseError,
    StorageError,
    TaskStateError,
)
from .listener import APIListener
from .login import LoginManager
from .models import CrawlResult, JobInfo, LoginStatus
from .parser import DataParser
from .storage import DataStorage
from .exporter import ExcelExporter

__all__ = [
    "APIListener",
    "BossCrawlerError",
    "BrowserError",
    "ConfigError",
    "CrawlerConfig",
    "CrawlerController",
    "CrawlResult",
    "DataParser",
    "DataStorage",
    "Event",
    "EventType",
    "ExcelExporter",
    "ExportError",
    "HOT_CITY_NAMES",
    "HOT_CITY_OPTIONS",
    "JobInfo",
    "ListenerError",
    "LoginManager",
    "LoginStatus",
    "LoginError",
    "ParseError",
    "PathConfig",
    "RetryConfig",
    "RuntimeConfig",
    "StorageError",
    "TaskStateError",
    "TaskStatus",
    "get_city_code",
]
