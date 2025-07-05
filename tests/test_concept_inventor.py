import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lambda_lib.core.node import LambdaNode, ConceptNode
from lambda_lib.graph import Graph
from lambda_lib.ops.concept_inventor import _best_corr
from lambda_lib.ops.meta_spawn import RuleNode
from lambda_lib.ops.feature_discoverer import FeatureNode


def test_concept_spawn_creates_nodes_and_rules():
    _best_corr.clear()
    graph = Graph([])
    metric = LambdaNode("Metric", data={"foo": 0.95})
    graph.add(metric)
    concepts = [n for n in graph.nodes if isinstance(n, ConceptNode)]
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    assert any(c.label == "Concept:foo" for c in concepts)
    assert any(r.label == "Rule:foo" for r in rules)


def test_feature_to_concept_to_rule_chain():
    _best_corr.clear()
    graph = Graph([])
    feature = FeatureNode("foo", data={"foo": 0.95})
    graph.add(feature)
    concepts = [n for n in graph.nodes if isinstance(n, ConceptNode)]
    rules = [n for n in graph.nodes if isinstance(n, RuleNode)]
    assert any(c.label == "Concept:foo" for c in concepts)
    assert len([r for r in rules if r.label == "Rule:foo"]) >= 2


def test_concept_node_improves_metric():
    _best_corr.clear()
    graph = Graph([])

    graph.add(LambdaNode("Metric", data={"foo": 0.5}))
    baseline = _best_corr.get("foo", 0.0)

    graph.add(LambdaNode("Metric", data={"foo": 0.95}))
    concepts = [n for n in graph.nodes if isinstance(n, ConceptNode)]

    assert len(concepts) >= 1
    assert _best_corr.get("foo", 0.0) > baseline

