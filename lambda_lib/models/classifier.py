#@module:
#@  version: "0.3"
#@  layer: models
#@  exposes: [RuleBasedClassifier]
#@  doc: Simple rule-based classifier using a latency threshold.
#@end

class RuleBasedClassifier:
    """Return 1 if ``latency_ms`` >= threshold else 0."""

    def __init__(self, threshold: int = 1000) -> None:
        self.threshold = threshold

    def predict(self, features: dict) -> int:
        latency = int(features.get("latency_ms", 0))
        return int(latency >= self.threshold)
