#@module:
#@  version: "0.3"
#@  layer: app
#@  exposes: [main]
#@  doc: Command line interface to run seed λ graphs.
#@end
from __future__ import annotations

import sys
from typing import Sequence

from .core.engine import LambdaEngine
from .core.node import LambdaNode
from .core.operation import LambdaOperation
from .graph import Graph


#@contract:
#@  pre: len(argv) >= 2
#@  post: result in [0, 1]
#@end
def main(argv: Sequence[str]) -> int:
    """Run the seed graph specified in ``argv``."""
    if len(argv) < 2:
        return 1

    seed = argv[1]

    if seed == "noop":
        node = LambdaNode("noop")
        graph = Graph([node])

        def noop_op(n: LambdaNode) -> LambdaNode:
            return LambdaNode("noop", data=n.data, links=n.links)

        op = LambdaOperation("noop", noop_op)

        engine = LambdaEngine()
        engine.register(op)

        executor = engine.execute(graph)
        return 0 if executor.state == "ready" else 1

    return 1


if __name__ == "__main__":  # pragma: no cover - manual invocation
    sys.exit(main(sys.argv))
