from boss_crawler.login import LoginManager


def test_提取字典型_cookie_名称():
    cookies = {"bst": "x", "foo": "bar"}
    names = LoginManager._extract_cookie_names(cookies)
    assert names == {"bst", "foo"}


def test_提取列表型_cookie_名称():
    cookies = [{"name": "__zp_stoken__"}, {"name": "wt2"}, {"value": "x"}]
    names = LoginManager._extract_cookie_names(cookies)
    assert names == {"__zp_stoken__", "wt2"}
