#@module:
#@  version: "0.3"
#@  layer: metrics
#@  exposes: [accuracy]
#@  doc: Accuracy metric computation.
#@end

#@contract:
#@  post: 0.0 <= result <= 1.0
#@  assigns: []
#@end
def accuracy(preds: list[int], labels: list[int]) -> float:
    """Return classification accuracy for the given predictions."""
    total = max(len(labels), 1)
    correct = sum(1 for p, l in zip(preds, labels) if p == l)
    result = correct / total
    assert 0.0 <= result <= 1.0
    return result
