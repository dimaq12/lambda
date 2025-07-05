#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [vote, merge_models, convolve]
#@  doc: Cooperative operations for model ensembles.
#@end
from __future__ import annotations

from statistics import mean
from typing import Iterable, Sequence

from ..models.classifier import RuleBasedClassifier


#@contract:
#@  pre: all(p in (0, 1) for p in preds)
#@  post: result in (0, 1)
#@  assigns: []
#@end
def vote(preds: Iterable[int]) -> int:
    """Return majority class from ``preds``."""
    vals = list(preds)
    assert len(vals) > 0
    ones = sum(1 for p in vals if p == 1)
    return int(ones >= len(vals) / 2)


#@contract:
#@  pre: len(list(models)) > 0
#@  post: isinstance(result, RuleBasedClassifier)
#@  assigns: []
#@end
def merge_models(models: Iterable[RuleBasedClassifier]) -> RuleBasedClassifier:
    """Return a new classifier averaging model thresholds."""
    mlist = list(models)
    assert len(mlist) > 0
    thr = int(round(mean(m.threshold for m in mlist)))
    return RuleBasedClassifier(threshold=thr)


#@contract:
#@  pre: len(values) > 0
#@  post: result is not None
#@  assigns: []
#@end
def convolve(values: Sequence[float], weight: float = 0.5) -> float:
    """Blend last value with previous mean using ``weight``."""
    assert len(values) > 0
    if len(values) == 1:
        return values[0]
    prev_mean = mean(values[:-1])
    return weight * values[-1] + (1 - weight) * prev_mean
