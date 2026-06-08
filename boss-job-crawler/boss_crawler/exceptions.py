"""项目基础异常定义。"""


class BossCrawlerError(Exception):
    """项目基础异常。"""


class ConfigError(BossCrawlerError):
    """配置相关异常。"""


class LoginError(BossCrawlerError):
    """登录相关异常。"""


class BrowserError(BossCrawlerError):
    """浏览器相关异常。"""


class ListenerError(BossCrawlerError):
    """接口监听相关异常。"""


class ParseError(BossCrawlerError):
    """数据解析相关异常。"""


class StorageError(BossCrawlerError):
    """数据存储相关异常。"""


class ExportError(BossCrawlerError):
    """数据导出相关异常。"""


class TaskStateError(BossCrawlerError):
    """任务状态异常。"""
