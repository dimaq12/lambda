#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [FeatureNode, discover_features, discover]
#@  doc: Discover new features from node data when accuracy improves.
#@end
from __future__ import annotations

from typing import Dict, List
from statistics import pvariance, mean, pstdev
import math

from ..memory import SequenceMemory

from ..core.node import LambdaNode


class FeatureNode(LambdaNode):
    """Specialised LambdaNode representing a discovered feature."""

    def __init__(self, name: str, data: object | None = None):
        super().__init__(f"Feature:{name}", data, [])


# track best accuracy values seen so far
_best_accuracy: Dict[str, float] = {}

_event_memory = SequenceMemory(capacity=10)


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


def _point_biserial(values: List[float], labels: List[int]) -> float:
    if len(values) != len(labels):
        return 0.0
    n = len(values)
    n1 = sum(1 for l in labels if l == 1)
    n0 = n - n1
    if n0 == 0 or n1 == 0:
        return 0.0
    m1 = mean(v for v, lbl in zip(values, labels) if lbl == 1)
    m0 = mean(v for v, lbl in zip(values, labels) if lbl == 0)
    s = pstdev(values)
    if s == 0:
        return 0.0
    return (m1 - m0) / s * math.sqrt(n1 * n0 / (n * n))


def discover(node_batch: List[LambdaNode]) -> List[str]:
    """Return feature expression candidates discovered from ``node_batch``."""
    candidates: List[str] = []
    if not node_batch:
        return candidates

    for node in node_batch:
        if isinstance(node.data, dict) and "label" in node.data:
            _event_memory.push(node.data)

    events = _event_memory.as_list()
    if len(events) < 2:
        return candidates

    labels = [int(e["label"]) for e in events if "label" in e]
    if len(labels) != len(events) or len(set(labels)) < 2:
        return candidates

    keys = [k for k in events[0].keys() if k != "label"]
    for key in keys:
        try:
            vals = [float(e[key]) for e in events]
        except Exception:
            continue
        var = pvariance(vals)
        corr = _point_biserial(vals, labels)
        if var > 0 and abs(corr) > 0:
            candidates.append(str(key))

    return candidates
