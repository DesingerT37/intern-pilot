from boss_crawler import CrawlerConfig, CrawlerController, JobInfo


def test_配置初始化时创建运行目录(tmp_path):
    config = CrawlerConfig()
    config.paths.project_root = tmp_path
    config.paths.output_dir = tmp_path / "output"
    config.paths.log_dir = tmp_path / "logs"
    config.paths.session_dir = tmp_path / "sessions"

    config.validate()

    assert config.paths.output_dir.exists()
    assert config.paths.log_dir.exists()
    assert config.paths.session_dir.exists()


def test_职位模型可生成导出字典():
    job = JobInfo(job_name="Python开发", company_name="测试公司", location="北京")

    result = job.to_dict()

    assert result["岗位名称"] == "Python开发"
    assert result["公司名称"] == "测试公司"
    assert result["工作地点"] == "北京"


def test_控制器默认不是运行中():
    controller = CrawlerController(config=CrawlerConfig())
    assert controller.is_running() is False
