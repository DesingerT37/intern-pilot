from boss_crawler import DataStorage, JobInfo


def test_存储器会按职位id去重():
    storage = DataStorage(enable_deduplication=True)
    first = JobInfo(job_name="Python", company_name="A", location="Shanghai", job_id="1")
    second = JobInfo(job_name="Python", company_name="A", location="Shanghai", job_id="1")

    assert storage.add_job(first) is True
    assert storage.add_job(second) is False
    assert storage.get_job_count() == 1


def test_关闭去重后允许重复职位():
    storage = DataStorage(enable_deduplication=False)
    job = JobInfo(job_name="Python", company_name="A", location="Shanghai", job_id="1")

    storage.add_job(job)
    storage.add_job(job)

    assert storage.get_job_count() == 2
