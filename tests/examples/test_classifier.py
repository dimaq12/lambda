import os
import sys
from pathlib import Path

# Ensure project root on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from lambda_lib.examples.classifier import run
from lambda_lib.core.engine import LambdaEngine
from lambda_lib.core.node import LambdaNode
from lambda_lib.core.operation import LambdaOperation


def test_classifier_example_runs():
    seed_file = Path(run.__file__).with_name("seed.yaml")
    graph = run.load_graph(str(seed_file))

    engine = LambdaEngine()

    def data_stream(node: LambdaNode) -> LambdaNode:
        value = (node.data or 0) + 1
        return LambdaNode("DataStream", data=value, links=node.links)

    def feature_maker(node: LambdaNode) -> LambdaNode:
        return LambdaNode("FeatureMaker", data=node.data, links=node.links)

    def classifier(node: LambdaNode) -> LambdaNode:
        return LambdaNode("Classifier", data="NORMAL", links=node.links)

    def statistics(node: LambdaNode) -> LambdaNode:
        return LambdaNode("Statistics", data=node.data, links=node.links)

    engine.register(LambdaOperation("DataStream", data_stream))
    engine.register(LambdaOperation("FeatureMaker", feature_maker))
    engine.register(LambdaOperation("Classifier", classifier))
    engine.register(LambdaOperation("Statistics", statistics))

    scheduler = engine.execute(graph)
    assert scheduler.state == "ready"
    # DataStream node should have incremented value
    assert graph.nodes[0].data == 1
    # FeatureMaker should bypass processing and carry raw data
    assert graph.nodes[1].data == 1
    # Classifier node should have produced NORMAL output
    assert graph.nodes[2].data == "NORMAL"
