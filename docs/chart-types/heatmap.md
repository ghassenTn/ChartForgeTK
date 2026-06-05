# Heat Map

Color-coded matrix visualization for pattern recognition.

```python
from ChartForgeTK import HeatMap

# 2D matrix of values
data = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
chart = HeatMap(parent, width=600, height=400)
chart.plot(data)
```

## Parameters

### `HeatMap.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[list[float]]` | 2D numeric matrix |

Each cell is colored on a gradient from low (cool) to high (hot) values.
Row and column labels are automatically generated from the data dimensions.
