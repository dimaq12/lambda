#@module:
#@  version: "0.3"
#@  layer: sensors
#@  exposes: [tail_file, TailResult]
#@  doc: Simple file tailing utility.
#@end

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TailResult:
    """Result of a file tail operation."""

    new_data: str
    position: int


#@contract:
#@  pre: Path(path).exists()
#@  post: result.new_data is not None
#@  assigns: []
#@end
def tail_file(path: str, start: int = 0) -> TailResult:
    """Read file contents from ``start`` and return new data and new position."""
    assert Path(path).exists()
    with open(path, "r") as fh:
        fh.seek(start)
        data = fh.read()
        pos = fh.tell()
    result = TailResult(new_data=data, position=pos)
    assert result.new_data is not None
    return result
