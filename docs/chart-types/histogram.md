# Histogram

Frequency distribution chart for data distribution analysis.

```python
from ChartForgeTK import Histogram

data = [1, 1.5, 2, 2, 2.5, 3, 3, 3.5, 4, 4.5, 5]
chart = Histogram(parent, width=600, height=400)
chart.plot(data, bins=5)
```

## Parameters

### `Histogram.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[float]` or Series | Numeric values to bin |
| `bins` | int, optional | Number of bins (default: auto-calculated) |
