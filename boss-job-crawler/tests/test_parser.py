from boss_crawler import DataParser
from boss_crawler.exceptions import ParseError


def test_解析职位列表为结构化对象():
    payload = {
        "zpData": {
            "jobList": [
                {
                    "jobName": "Python开发实习生",
                    "brandName": "测试公司",
                    "cityName": "上海",
                    "areaDistrict": "浦东新区",
                    "businessDistrict": "张江",
                    "jobDegree": "本科",
                    "jobExperience": "在校生",
                    "salaryDesc": "150-200元/天",
                    "jobLabels": ["Python", "数据分析"],
                    "postDescription": "负责数据处理",
                    "bossName": "王经理",
                    "bossTitle": "技术负责人",
                    "brandIndustry": "互联网",
                    "brandScaleName": "100-499人",
                    "encryptJobId": "job-001",
                }
            ]
        }
    }

    jobs = DataParser().parse_job_list(payload)

    assert len(jobs) == 1
    job = jobs[0]
    assert job.job_name == "Python开发实习生"
    assert job.company_name == "测试公司"
    assert job.location == "上海 / 浦东新区 / 张江"
    assert job.job_tags == ["Python", "数据分析"]
    assert job.job_id == "job-001"


def test_缺少关键字段的职位会被过滤():
    payload = {
        "data": {
            "jobList": [
                {"jobName": "Python开发", "brandName": "A公司", "cityName": "北京"},
                {"jobName": "", "brandName": "B公司", "cityName": "北京"},
                {"jobName": "测试", "brandName": "", "cityName": "北京"},
            ]
        }
    }

    jobs = DataParser().parse_job_list(payload)

    assert len(jobs) == 1
    assert jobs[0].company_name == "A公司"


def test_缺少职位列表时抛出解析异常():
    parser = DataParser()

    try:
        parser.parse_job_list({"unexpected": []})
    except ParseError as exc:
        assert "job list not found" in str(exc)
    else:
        raise AssertionError("expected ParseError")
