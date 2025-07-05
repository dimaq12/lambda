# Drift concepts

This short example shows how concept nodes emerge from new features.

```python
from lambda_lib.core.node import LambdaNode
from lambda_lib.graph import Graph
from lambda_lib.ops.spawn_feature import spawn_feature

# start with an empty graph
graph = Graph([])

# create a new feature description
fd = LambdaNode("FeatureDiscoverer", data={"expr": "latency_ms"})
feature = spawn_feature(fd)

# once the feature proves useful (e.g. high correlation)
feature.data = {"latency_ms": 0.92}

# adding the feature spawns a rule and a concept automatically
graph.add(feature)

for node in graph.nodes:
    print(node.label, node.data)
```

Running it prints a `Concept:latency_ms` node alongside a new rule
`Rule:latency_ms` completing the `spawn_feature → spawn_op → concept` chain.
