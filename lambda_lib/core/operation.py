#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaOperation]
#@  doc: Describes a transformation that can be applied to LambdaNode.
#@end
from typing import Callable

from .node import LambdaNode
#@contract:
#@  post: result.name == self.name
#@  assigns: []
#@end
class LambdaOperation:
    """Callable wrapper describing a transformation."""

    def __init__(self, name: str, func: Callable[[LambdaNode], LambdaNode]):
        self.name = name
        self.func = func

    def __call__(self, node: LambdaNode) -> LambdaNode:
        result = self.func(node)
        assert result.name == self.name
        return result
