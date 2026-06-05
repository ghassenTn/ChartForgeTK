# Bubble Chart

Scatter plot with size encoding for three-variable data.

```python
from ChartForgeTK import BubbleChart

chart = BubbleChart(parent, width=600, height=400)
chart.plot([(1, 10, 5), (2, 15, 10), (3, 13, 15)])
```

## Parameters

### `BubbleChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[tuple]` | List of `(x, y, size)` tuples |

Each tuple contains:
- `x` — horizontal position
- `y` — vertical position
- `size` — bubble radius scaling factor
