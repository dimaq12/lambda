#@module:
#@  version: "0.3"
#@  layer: core
#@  exposes: [LambdaNode]
#@  doc: Fundamental λ entity representing a unit of meaning.
#@end
#@contract:
#@  inv:
#@    - self.label is not None
#@    - isinstance(self.links, list)
#@    - forall n in self.links: isinstance(n, LambdaNode)
#@  assigns: [self.data, self.links]
#@end
class LambdaNode:
    """Basic node in a λ graph."""

    def __init__(self, label: str, data: object | None = None, links: list | None = None) -> None:
        self.label = label
        self.data = data
        self.links = list(links) if links is not None else []
        self._check_invariants()

    # simple alias used by some operations
    @property
    def name(self) -> str:
        return self.label

    def add_link(self, node: "LambdaNode") -> None:
        self.links.append(node)
        self._check_invariants()

    #@contract:
    #@  inv:
    #@    - self.label is not None
    #@    - isinstance(self.links, list)
    #@    - forall n in self.links: isinstance(n, LambdaNode)
    #@  assigns: [self.data, self.links]
    #@end
    def share(self) -> "LambdaNode":
        """Return a shallow copy of this node."""
        self._check_invariants()
        clone = LambdaNode(self.label, self.data, self.links)
        clone._check_invariants()
        return clone

    #@contract:
    #@  inv:
    #@    - self.label is not None
    #@    - isinstance(self.links, list)
    #@    - forall n in self.links: isinstance(n, LambdaNode)
    #@  assigns: [self.data, self.links]
    #@end
    def clone(self, phase: str) -> "LambdaNode":
        """Return a copy tagged with ``phase``."""
        self._check_invariants()
        new_label = f"{self.label}@{phase}"
        clone = LambdaNode(new_label, self.data, self.links)
        clone._check_invariants()
        return clone

    #@contract:
    #@  inv:
    #@    - self.label is not None
    #@    - isinstance(self.links, list)
    #@    - forall n in self.links: isinstance(n, LambdaNode)
    #@  assigns: [self.data, self.links]
    #@end
    def mirror(self) -> "LambdaNode":
        """Return a node with links in reversed order."""
        self._check_invariants()
        clone = LambdaNode(self.label, self.data, list(reversed(self.links)))
        clone._check_invariants()
        return clone

    def _check_invariants(self) -> None:
        assert self.label is not None
        assert isinstance(self.links, list)
        assert all(isinstance(n, LambdaNode) for n in self.links)
