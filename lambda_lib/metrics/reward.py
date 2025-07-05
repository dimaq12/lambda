#@module:
#@  version: "0.3"
#@  layer: metrics
#@  exposes: [reward, RewardMetric]
#@  doc: Normalized reward metric and helper node.
#@end

from ..core.node import LambdaNode

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


class RewardMetric(LambdaNode):
    """Lambda node storing a normalized reward value."""

    def __init__(self, value: float = 0.0, scale: float = 1.0):
        super().__init__("RewardMetric", data=reward(value, scale), links=[])
        self.scale = scale

    def update(self, value: float) -> None:
        """Update node data with new normalized reward value."""
        self.data = reward(value, self.scale)
