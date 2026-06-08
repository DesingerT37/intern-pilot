from boss_crawler import HOT_CITY_NAMES, get_city_code


def test_热门城市列表包含全国和北京():
    assert "全国" in HOT_CITY_NAMES
    assert "北京" in HOT_CITY_NAMES


def test_城市名称能映射到城市编码():
    assert get_city_code("北京") == "101010100"
    assert get_city_code("深圳") == "101280600"
    assert get_city_code("不存在的城市") is None
