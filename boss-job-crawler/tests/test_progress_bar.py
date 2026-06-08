"""进度条应按去重总量与已完成条数计算。"""


def calculate_progress(completed_jobs: int, unique_jobs: int) -> int:
    if unique_jobs <= 0:
        return 0
    return min(100, int(completed_jobs / unique_jobs * 100))


def test_list_phase_does_not_jump_to_half():
    """列表阶段未完成详情时，进度应保持 0%。"""
    assert calculate_progress(completed_jobs=0, unique_jobs=15) == 0


def test_each_detail_increments_progress():
    """每完成一条详情，进度按 1/N 递增。"""
    unique = 30
    assert calculate_progress(1, unique) == 3
    assert calculate_progress(15, unique) == 50
    assert calculate_progress(30, unique) == 100


def test_two_pages_unique_total():
    """两页共 28 条去重数据，第 1 条详情约 3.6%。"""
    unique = 28
    assert calculate_progress(1, unique) == 3
