from boss_crawler import APIListener
from boss_crawler.exceptions import ListenerError


class _FakeResponse:
    def __init__(self, body):
        self.body = body


class _FakeBackendListener:
    def __init__(self):
        self.started_with = None
        self.stopped = False
        self.payloads = []

    def start(self, pattern):
        self.started_with = pattern

    def wait(self, timeout=0.1):
        if self.payloads:
            return self.payloads.pop(0)
        return None

    def stop(self):
        self.stopped = True


class _FakePage:
    def __init__(self):
        self.listen = _FakeBackendListener()


def test_监听器可启动并从后端监听对象读取响应():
    page = _FakePage()
    page.listen.payloads.append(_FakeResponse('{"zpData": {"jobList": []}}'))

    listener = APIListener(page=page)
    listener.start(r"https://www\\.zhipin\\.com/web/geek/job")
    response = listener.get_job_response(timeout=1)

    assert page.listen.started_with == r"https://www\\.zhipin\\.com/web/geek/job"
    assert response["zpData"]["jobList"] == []


def test_监听器支持手动注入响应():
    listener = APIListener()
    listener.start(r"job")
    listener.push_response({"data": {"jobList": [{"jobName": "Python"}]}})

    response = listener.get_job_response(timeout=1)

    assert response["data"]["jobList"][0]["jobName"] == "Python"


def test_监听器超时会抛出异常():
    listener = APIListener()
    listener.start(r"job")

    try:
        listener.get_job_response(timeout=0.2)
    except ListenerError as exc:
        assert "timed out" in str(exc)
    else:
        raise AssertionError("expected ListenerError")
