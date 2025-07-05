#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [FeatureNode, discover_features]
#@  doc: Discover new features from node data when accuracy improves.
#@end
from __future__ import annotations

from typing import Dict, List

from ..core.node import LambdaNode


class FeatureNode(LambdaNode):
    """Specialised LambdaNode representing a discovered feature."""

    def __init__(self, name: str, data: object | None = None):
        super().__init__(f"Feature:{name}", data, [])


# track best accuracy values seen so far
_best_accuracy: Dict[str, float] = {}


#@contract:
#@  post: isinstance(result, list)
#@  assigns: [_best_accuracy]
#@end
def discover_features(node: LambdaNode) -> List[FeatureNode]:
    """Return new :class:`FeatureNode` objects if ``node.data`` contains
    improved accuracy entries.
    """
    features: List[FeatureNode] = []
    if isinstance(node.data, dict):
        for name, value in node.data.items():
            try:
                acc = float(value)
            except Exception:
                continue
            prev = _best_accuracy.get(name, 0.0)
            if acc > prev:
                _best_accuracy[name] = acc
                features.append(FeatureNode(name, acc))
    return features
