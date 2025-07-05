#@module:
#@  version: "0.3"
#@  layer: memory
#@  exposes: [SequenceMemory, convolve_context]
#@  doc: FIFO memory for storing recent events and simple context-aware update.
#@end

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from statistics import mean


@dataclass
class SequenceMemory:
    """Fixed-size queue tracking the most recent items."""

    capacity: int = 10
    events: deque = field(init=False)

    def __post_init__(self) -> None:
        self.events = deque(maxlen=self.capacity)

    #@contract:
    #@  post: len(self.events) <= self.capacity
    #@  assigns: [self.events]
    #@end
    def push(self, item: object) -> None:
        """Add ``item`` keeping at most ``capacity`` items."""
        self.events.append(item)
        assert len(self.events) <= self.capacity

    def __len__(self) -> int:
        return len(self.events)

    def as_list(self) -> list:
        """Return memory contents oldest first."""
        return list(self.events)


#@contract:
#@  pre: memory is not None
#@  post: result is not None
#@  assigns: []
#@end
def convolve_context(pred: float, memory: SequenceMemory, weight: float = 0.5) -> float:
    """Blend ``pred`` with the mean of ``memory`` using ``weight``."""
    assert memory is not None
    if len(memory) == 0:
        return pred
    ctx = mean(memory.as_list())
    result = weight * pred + (1 - weight) * ctx
    assert result is not None
    return result
