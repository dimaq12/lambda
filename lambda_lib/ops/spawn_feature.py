#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [spawn_feature]
#@  doc: Spawn a FeatureNode from a description node.
#@end
from __future__ import annotations

from ..core.node import LambdaNode
from .feature_discoverer import FeatureNode


def spawn_feature(node: LambdaNode) -> FeatureNode:
    """Return a new :class:`FeatureNode` using ``node.data`` as expression."""
    expr = None
    if isinstance(node.data, dict):
        expr = node.data.get("expr")
    else:
        expr = node.data
    feature = FeatureNode(str(expr) if expr is not None else node.label)
    feature.data = {"expr": expr}
    return feature
