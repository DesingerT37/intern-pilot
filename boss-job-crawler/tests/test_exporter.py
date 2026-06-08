from boss_crawler import ExcelExporter, JobInfo


def test_excel导出器会写出xlsx文件(tmp_path):
    exporter = ExcelExporter()
    output = tmp_path / "jobs.xlsx"
    jobs = [
        JobInfo(job_name="Python", company_name="A公司", location="北京"),
        JobInfo(job_name="测试", company_name="B公司", location="上海"),
    ]

    result = exporter.export(jobs, output)

    assert result.exists()
    assert result.suffix == ".xlsx"
