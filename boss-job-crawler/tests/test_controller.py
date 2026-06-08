from boss_crawler import CrawlerConfig, CrawlerController, LoginStatus


class _FakeBrowser:
    def __init__(self):
        self.urls = []

    def get_page(self):
        return object()

    def open_url(self, url: str) -> None:
        self.urls.append(url)

    def wait(self, seconds: float) -> None:
        return None


class _FakeLoginManager:
    def __init__(self, logged_in: bool = True):
        self.logged_in = logged_in

    def check_login_status(self):
        return LoginStatus(is_logged_in=self.logged_in, message="ok" if self.logged_in else "not logged in")

    def open_login_page(self):
        return None


class _FakeListener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.bound_page = None
        self.started_pattern = None
        self.stopped = False

    def bind_page(self, page):
        self.bound_page = page

    def start(self, pattern: str):
        self.started_pattern = pattern

    def get_job_response(self, timeout):
        return self.responses.pop(0)

    def stop(self):
        self.stopped = True


def test_controller_chains_crawl_parse_store_export(tmp_path):
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.retry.page_delay_seconds = 0
    config.retry.request_timeout_seconds = 1
    config.validate()

    listener = _FakeListener(
        [
            {
                "zpData": {
                    "jobList": [
                        {"jobName": "Python实习", "brandName": "A公司", "cityName": "北京", "encryptJobId": "1"},
                        {"jobName": "Python实习", "brandName": "A公司", "cityName": "北京", "encryptJobId": "1"},
                    ]
                }
            },
            {
                "zpData": {
                    "jobList": [
                        {"jobName": "数据分析实习", "brandName": "B公司", "cityName": "上海", "encryptJobId": "2"}
                    ]
                }
            },
        ]
    )

    controller = CrawlerController(
        config=config,
        browser=_FakeBrowser(),
        login_manager=_FakeLoginManager(logged_in=True),
        listener=listener,
    )

    result = controller.start(keyword="python", max_pages=2)

    assert result.success is True
    assert result.total_jobs == 3
    assert result.unique_jobs == 2
    assert result.pages_crawled == 2
    assert result.output_file is not None


def test_controller_returns_failure_when_not_logged_in(tmp_path):
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"
    config.validate()

    controller = CrawlerController(
        config=config,
        browser=_FakeBrowser(),
        login_manager=_FakeLoginManager(logged_in=False),
        listener=_FakeListener([]),
    )

    result = controller.start(keyword="python", max_pages=1)

    assert result.success is False
    assert result.error_message is not None


def test_controller_uses_current_jobs_page_url():
    controller = CrawlerController(
        config=CrawlerConfig(),
        browser=_FakeBrowser(),
        login_manager=_FakeLoginManager(logged_in=True),
        listener=_FakeListener([{"zpData": {"jobList": []}}]),
    )

    url = controller._build_search_url(keyword="python", page=2)

    assert "/web/geek/jobs?" in url
    assert "page=2" in url


def test_runtime_config_matches_current_job_api_pattern():
    """验证配置中的 API 模式匹配当前 BOSS 直聘的职位列表接口。"""
    config = CrawlerConfig()

    pattern = config.runtime.api_url_pattern

    assert r"zhipin\.com/web/geek/job" in pattern
