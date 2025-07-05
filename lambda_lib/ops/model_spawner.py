#@module:
#@  version: "0.3"
#@  layer: ops
#@  exposes: [ModelNode, spawn_models]
#@  doc: Spawn model subgraphs when reward improves.
#@end
from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING

from ..core.node import LambdaNode
from ..core.operation import LambdaOperation
from ..models.classifier import RuleBasedClassifier

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from ..core.engine import LambdaEngine


class ModelNode(LambdaNode):
    """Lambda node wrapping a model subgraph and its engine."""

    def __init__(self, name: str, graph: "Graph", engine: "LambdaEngine") -> None:
        super().__init__(f"Model:{name}", data=graph, links=[])
        self.engine = engine


# track best reward values seen so far
_best_reward: Dict[str, float] = {}


#@contract:
#@  post: isinstance(result, list)
#@  assigns: [_best_reward]
#@end
def spawn_models(node: LambdaNode, reward_threshold: float = 0.0) -> List[ModelNode]:
    """Return new :class:`ModelNode` objects if ``node.data`` contains
    improved reward entries.
    
    ``node.data`` should map a parameter value (as string or int) to a
    numeric reward. Each entry spawns a simple rule based classifier
    using that parameter as threshold.
    """
    models: List[ModelNode] = []
    if isinstance(node.data, dict):
        for key, value in node.data.items():
            try:
                reward_val = float(value)
                param = int(key)
            except Exception:
                continue
            prev = _best_reward.get(key, float("-inf"))
            if reward_val > prev and reward_val >= reward_threshold:
                _best_reward[key] = reward_val
                from ..core.engine import LambdaEngine
                from ..graph import Graph
                engine = LambdaEngine()
                model = RuleBasedClassifier(param)

                def feature_op(n: LambdaNode) -> LambdaNode:
                    return LambdaNode("FeatureMaker", data=n.data, links=n.links)

                def model_op(n: LambdaNode, _model=model) -> LambdaNode:
                    feats = n.data if isinstance(n.data, dict) else {}
                    pred = _model.predict(feats)
                    return LambdaNode(f"Model#{param}", data=pred, links=n.links)

                engine.register(LambdaOperation("FeatureMaker", feature_op))
                engine.register(LambdaOperation(f"Model#{param}", model_op))

                g = Graph([
                    LambdaNode("FeatureMaker"),
                    LambdaNode(f"Model#{param}")
                ])
                models.append(ModelNode(f"Model#{param}", g, engine))
    return models
