import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from lambda_lib.examples.fixed_feature import run
from lambda_lib.metrics.accuracy import accuracy


def test_fixed_feature_pipeline():
    samples = [
        {"latency_ms": 100, "label": 0},
        {"latency_ms": 700, "label": 1},
        {"latency_ms": 400, "label": 0},
        {"latency_ms": 900, "label": 0},
    ]
    engine, graph, preds, labels = run.build_graph(samples, threshold=500)

    for _ in samples:
        scheduler = engine.execute(graph)
        assert scheduler.state == "ready"

    expected = accuracy(preds, labels)
    assert graph.nodes[-1].data == expected
    assert expected == 0.75
