# Box Plot

Statistical distribution visualization with outlier detection.

```python
from ChartForgeTK import BoxPlot

data = [
    [1, 2, 3, 4, 5, 6, 7],
    [2, 4, 6, 8, 10, 12, 14],
    [1, 3, 5, 7, 9, 11, 20]
]
chart = BoxPlot(parent, width=600, height=400)
chart.plot(data, ["Group A", "Group B", "Group C"])
```

## Parameters

### `BoxPlot.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[list[float]]` | List of datasets (each is a list of values) |
| `labels` | `list[str]`, optional | Group labels for each dataset |

Each dataset is summarized as a box showing:
- **Median** (center line)
- **Q1 / Q3** (box edges / interquartile range)
- **Whiskers** (1.5× IQR)
- **Outliers** (points beyond whiskers)
