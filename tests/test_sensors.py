import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.sensors.file_tail import tail_file
from lambda_lib.sensors.http_stream import http_stream


def test_tail_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello\n")
    res1 = tail_file(str(path))
    assert res1.new_data == "hello\n"
    assert res1.position > 0
    res2 = tail_file(str(path), start=res1.position)
    assert res2.new_data == ""
    assert res2.position == res1.position


def test_http_stream(monkeypatch):
    class FakeResp:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass
        def read(self):
            return b"data"

    def fake_urlopen(url):
        return FakeResp()

    monkeypatch.setattr("lambda_lib.sensors.http_stream.urlopen", fake_urlopen)
    res = http_stream("http://example.com")
    assert res.new_data == "data"

    def raising(url):
        raise Exception("fail")

    monkeypatch.setattr("lambda_lib.sensors.http_stream.urlopen", raising)
    res2 = http_stream("http://example.com")
    assert res2.new_data == ""
