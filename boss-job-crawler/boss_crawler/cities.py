"""Built-in BOSS city options used by the desktop form.

The initial list follows BOSS直聘's public hot-city selector:
全国、北京、上海、广州、深圳、杭州、天津、西安、苏州、武汉、厦门、长沙、成都、郑州、重庆。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CityOption:
    name: str
    code: str


HOT_CITY_OPTIONS: tuple[CityOption, ...] = (
    CityOption("全国", "100010000"),
    CityOption("北京", "101010100"),
    CityOption("上海", "101020100"),
    CityOption("广州", "101280100"),
    CityOption("深圳", "101280600"),
    CityOption("杭州", "101210100"),
    CityOption("天津", "101030100"),
    CityOption("西安", "101110100"),
    CityOption("苏州", "101190400"),
    CityOption("武汉", "101200100"),
    CityOption("厦门", "101230200"),
    CityOption("长沙", "101250100"),
    CityOption("成都", "101270100"),
    CityOption("郑州", "101180100"),
    CityOption("重庆", "101040100"),
)

HOT_CITY_NAMES: tuple[str, ...] = tuple(option.name for option in HOT_CITY_OPTIONS)
HOT_CITY_CODE_BY_NAME: dict[str, str] = {option.name: option.code for option in HOT_CITY_OPTIONS}


def get_city_code(city_name: str) -> str | None:
    return HOT_CITY_CODE_BY_NAME.get(city_name.strip())
