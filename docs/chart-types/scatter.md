# Scatter Plot

X-Y coordinate plotting for correlation analysis.

```python
from ChartForgeTK import ScatterPlot

chart = ScatterPlot(parent, width=600, height=400)
chart.plot([(1, 10), (2, 15), (3, 13), (4, 18), (5, 16)])
```

## Parameters

### `ScatterPlot.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[tuple]` or DataFrame | List of `(x, y)` pairs |
| `x_column` | `str`, optional | Column name for DataFrame x-values |
| `y_column` | `str`, optional | Column name for DataFrame y-values |

## Pandas Integration

```python
import pandas as pd
from ChartForgeTK import ScatterPlot

df = pd.DataFrame({
    'height': [160, 165, 170, 175, 180],
    'weight': [55, 60, 65, 70, 75]
})

chart = ScatterPlot(parent, width=600, height=400)
chart.plot(df, x_column='height', y_column='weight')
```
