# Network Graph

Node-edge visualization for relationships and graph data.

```python
from ChartForgeTK import NetworkGraph

nodes = ["A", "B", "C", "D"]
edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")]

chart = NetworkGraph(parent, width=600, height=400)
chart.plot(nodes, edges)
```

## Parameters

### `NetworkGraph.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `nodes` | `list[str]` | Node labels |
| `edges` | `list[tuple]` | List of `(source, target)` connections |

Nodes are positioned using a force-directed layout algorithm. Each node
is draggable, and edges are drawn as connecting lines between linked nodes.
