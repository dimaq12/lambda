#@module:
#@  version: "0.3"
#@  layer: metrics
#@  exposes: [reward]
#@  doc: Normalized reward metric.
#@end

#@contract:
#@  post: -1.0 <= result <= 1.0
#@  assigns: []
#@end
def reward(value: float, scale: float = 1.0) -> float:
    """Return a scaled reward clamped to [-1, 1]."""
    if scale == 0:
        scaled = 0.0
    else:
        scaled = value / scale
    if scaled > 1.0:
        scaled = 1.0
    if scaled < -1.0:
        scaled = -1.0
    assert -1.0 <= scaled <= 1.0
    return scaled
