#@module:
#@  version: "0.3"
#@  layer: metrics
#@  exposes: [gradient_norm]
#@  doc: Simple gradient norm metric.
#@end

#@contract:
#@  post: 0.0 <= result <= 1.0
#@  assigns: []
#@end
def gradient_norm(grads: list[float]) -> float:
    """Return L1 norm of gradients clamped to [0,1]."""
    norm = sum(abs(g) for g in grads)
    if norm > 1.0:
        norm = 1.0
    assert 0.0 <= norm <= 1.0
    return norm
