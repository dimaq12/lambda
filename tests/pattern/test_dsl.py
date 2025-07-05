import os
import sys

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from lambda_lib.patterns.dsl import parse_pattern, builtin_patterns
from lambda_lib.core.pattern import Pattern as NodePattern
from lambda_lib.core.node import LambdaNode


def test_parse_pattern():
    pat = parse_pattern("a -> b")
    assert pat.match == "a"
    assert pat.rewrite == "b"


def test_builtin_patterns_loaded():
    # builtin_patterns should contain at least the eval pattern
    assert "eval" in builtin_patterns
    assert builtin_patterns["eval"].rewrite == "eval(x)"


def test_node_pattern_match():
    pattern = NodePattern("foo")
    node_good = LambdaNode("foo")
    node_bad = LambdaNode("bar")
    result_good = pattern.match(node_good)
    result_bad = pattern.match(node_bad)
    assert result_good.succeeded()
    assert result_good.matches == [node_good]
    assert not result_bad.succeeded()
    assert result_bad.matches == []
