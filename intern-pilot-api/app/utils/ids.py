"""ID 类型转换工具（兼容 PostgreSQL UUID 列）"""
from uuid import UUID
from typing import Any, Optional


def as_str_id(value: Any) -> str:
    """将 UUID / str / None 统一转为字符串 ID"""
    if value is None:
        return ""
    if isinstance(value, UUID):
        return str(value)
    return str(value)
