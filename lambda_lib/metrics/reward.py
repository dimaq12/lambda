#@module:
#@  version: "0.3"
#@  layer: metrics
#@  exposes: [reward, RewardMetric]
#@  doc: Normalized reward metric and helper node.
#@end

from ..core.node import LambdaNode
from collections import deque

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
    """Lambda node storing a normalized reward value with history."""

    def __init__(self, value: float = 0.0, scale: float = 1.0, history: int = 1):
        super().__init__("RewardMetric", data=reward(value, scale), links=[])
        self.scale = scale
        self.history = deque([self.data], maxlen=history)

    def update(self, value: float) -> None:
        """Update node data with new normalized reward value and history."""
        self.data = reward(value, self.scale)
        self.history.append(self.data)

    def history_list(self) -> list:
        """Return list of stored reward values, oldest first."""
        return list(self.history)
