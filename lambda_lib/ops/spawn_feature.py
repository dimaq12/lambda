#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [spawn_feature]
#@  doc: Spawn a FeatureNode from a description node.
#@end
from __future__ import annotations

from ..core.node import LambdaNode
from .feature_discoverer import FeatureNode, _event_memory
import math


def spawn_feature(node: LambdaNode) -> FeatureNode:
    """Return a new :class:`FeatureNode` using ``node.data`` as expression.

    When no expression is supplied, derive one using statistics from
    ``_event_memory`` (mean/std/delta).
    """
    expr = None
    if isinstance(node.data, dict):
        expr = node.data.get("expr")
    else:
        expr = node.data

    if expr is None or isinstance(expr, str) and expr.isidentifier():
        events = _event_memory.as_list()
        xs = [float(e.get("x", 0.0)) for e in events if isinstance(e, dict)]
        if len(xs) >= 2:
            avg = sum(xs) / len(xs)
            var = sum((v - avg) ** 2 for v in xs) / len(xs)
            std = math.sqrt(var)
            threshold = avg + 3 * std
            expr = f"x > {threshold} or abs(dx) > {3 * std}"
        else:
            expr = "x > 0"

    feature = FeatureNode(str(expr))
    feature.data = {"expr": expr}
    return feature
