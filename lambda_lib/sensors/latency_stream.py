#@module:
#@  version: "0.3"
#@  layer: sensors
#@  exposes: [LatencyEvent, latency_stream]
#@  doc: Generate fake latency events for testing.
#@end
from dataclasses import dataclass
import random


@dataclass
class LatencyEvent:
    """Simple latency event."""

    latency_ms: int


#@contract:
#@  post: isinstance(result, LatencyEvent)
#@  assigns: []
#@end
def latency_stream(low: int = 50, high: int = 1500) -> LatencyEvent:
    """Return a random latency event between ``low`` and ``high`` milliseconds."""
    value = random.randint(low, high)
    event = LatencyEvent(latency_ms=value)
    assert isinstance(event, LatencyEvent)
    return event
