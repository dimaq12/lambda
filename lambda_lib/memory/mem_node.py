#@module:
#@  version: "0.3"
#@  layer: memory
#@  exposes: [MemNode]
#@  doc: Simple memory node storing a list of items.
#@end

from dataclasses import dataclass, field


@dataclass
class MemNode:
    """In-memory data holder with length tracking."""

    store: list[object] = field(default_factory=list)
    store_len: int = 0

    #@contract:
    #@  post: self.store_len >= old_len
    #@  assigns: [self.store, self.store_len]
    #@end
    def add(self, item: object) -> int:
        """Append ``item`` and update ``store_len``."""
        old_len = self.store_len
        self.store.append(item)
        self.store_len = len(self.store)
        assert self.store_len >= old_len
        return self.store_len
