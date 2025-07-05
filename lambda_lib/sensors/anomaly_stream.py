#@module:
#@  version: "0.3"
#@  layer: sensors
#@  exposes: [AnomalyEvent, anomaly_stream]
#@  doc: Numeric stream generator with periodic spikes.
#@end
from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class AnomalyEvent:
    """Numeric event with ground truth label."""

    value: float
    label: int
    step: int


#@contract:
#@  pre: t >= 0
#@  post: isinstance(result, AnomalyEvent)
#@  assigns: []
#@end
def anomaly_stream(t: int) -> AnomalyEvent:
    """Return value drawn from N(100,3) normally or N(200,5) during spikes."""
    assert t >= 0
    if t % 80 > 60:
        val = random.gauss(200, 5)
        label = 1
    else:
        val = random.gauss(100, 3)
        label = 0
    event = AnomalyEvent(value=val, label=label, step=t)
    assert isinstance(event, AnomalyEvent)
    return event
