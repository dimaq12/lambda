#@module:
#@  version: "0.3"
#@  layer: sensors
#@  exposes: [http_stream, HTTPStreamResult]
#@  doc: Simple HTTP stream reader.
#@end

from dataclasses import dataclass
from urllib.request import urlopen
from urllib.error import URLError


@dataclass
class HTTPStreamResult:
    """Result of an HTTP stream fetch."""

    new_data: str


#@contract:
#@  pre: url.startswith("http")
#@  post: result.new_data is not None
#@  assigns: []
#@end
def http_stream(url: str) -> HTTPStreamResult:
    """Fetch data from ``url``. Returns empty string on failure."""
    assert url.startswith("http")
    try:
        with urlopen(url) as resp:
            data = resp.read().decode("utf-8")
    except Exception:
        data = ""
    result = HTTPStreamResult(new_data=data)
    assert result.new_data is not None
    return result
