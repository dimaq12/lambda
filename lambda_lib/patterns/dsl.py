#@module:
#@  version: "0.3"
#@  layer: patterns
#@  exposes: [Pattern, parse_pattern, builtin_patterns]
#@  doc: Minimal pattern DSL utilities.
#@end
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Pattern:
    """Simple representation of a rewrite pattern."""

    match: str
    rewrite: str


#@contract:
#@  pre: "->" in text
#@  post:
#@    - isinstance(result, Pattern)
#@    - result.match is not None
#@  assigns: []
#@end
def parse_pattern(text: str) -> Pattern:
    """Parse a minimal 'match -> rewrite' pattern expression."""
    assert "->" in text
    left, right = text.split("->", 1)
    pattern = Pattern(match=left.strip(), rewrite=right.strip())
    assert pattern.match is not None
    return pattern


# Load builtin patterns from adjacent YAML file without requiring PyYAML
_builtin_path = Path(__file__).with_name("builtin_patterns.yaml")
_builtin_patterns_raw: dict[str, str] = {}
if _builtin_path.exists():
    for line in _builtin_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            _builtin_patterns_raw[key.strip()] = value.strip().strip('"')

builtin_patterns = {
    name: parse_pattern(spec) for name, spec in _builtin_patterns_raw.items()
}
