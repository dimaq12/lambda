#@module:
#@  version: "0.3"
#@  layer: graph
#@  exposes: [render_svg]
#@  doc: Simple graph visualisation helpers.
#@end
from typing import Dict, Tuple

from . import Graph


#@contract:
#@  pre: graph is not None
#@  post: result.startswith("<svg")
#@  assigns: []
#@end
def render_svg(graph: Graph) -> str:
    """Return a minimal SVG representation of ``graph``."""
    assert graph is not None

    width = 120
    height = 40 * max(len(graph.nodes), 1)
    positions: Dict[object, Tuple[int, int]] = {}
    for idx, node in enumerate(graph.nodes):
        positions[node] = (width // 2, 20 + idx * 40)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
    ]

    # draw edges
    for node in graph.nodes:
        x1, y1 = positions[node]
        for link in getattr(node, "links", []):
            if link in positions:
                x2, y2 = positions[link]
                parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black"/>')

    # draw nodes
    for node in graph.nodes:
        x, y = positions[node]
        parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="lightgray" stroke="black"/>')
        parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" dy="4" font-size="10">{node.label}</text>')

    parts.append("</svg>")
    result = "\n".join(parts)
    assert result.startswith("<svg")
    return result
