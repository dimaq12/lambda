import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.ops import eval_rule, mirror_rule, phase_rule, convolve_rule, spawn_rule


def test_eval_op_parsing():
    assert eval_rule.match == "x"
    assert eval_rule.rewrite == "eval(x)"


def test_spawn_op_parsing():
    assert spawn_rule.rewrite == "spawned(x)"
    assert mirror_rule.rewrite == "x"
    assert phase_rule.rewrite == "phased(x)"
    assert convolve_rule.rewrite == "convolved(x)"
