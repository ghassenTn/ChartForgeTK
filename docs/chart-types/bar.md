# Bar Chart

Vertical bars with animations for categorical comparisons.

```python
from ChartForgeTK import BarChart

chart = BarChart(parent, width=600, height=400, theme='light')
chart.plot([10, 20, 15, 25], ["A", "B", "C", "D"])
```

## Parameters

### `BarChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[float]` or DataFrame | Numeric values (must be non-negative) |
| `labels` | `list[str]`, optional | Category labels |
| `value_column` | `str`, optional | Column name for DataFrame input |
| `label_column` | `str`, optional | Column name for DataFrame labels |

## Pandas Integration

```python
import pandas as pd
from ChartForgeTK import BarChart

df = pd.DataFrame({
    'category': ['Q1', 'Q2', 'Q3', 'Q4'],
    'sales': [150, 200, 175, 225]
})

chart = BarChart(parent, width=600, height=400)
chart.plot(df, value_column='sales', label_column='category')
```

## Edge Cases

- **Empty data**: raises `ValueError`
- **Negative values**: raises `ValueError` (bar charts require non-negative)
- **Mismatched labels**: raises `ValueError` if label count != data count
- **Single data point**: renders correctly with proper axis range
- **Identical values**: axis range automatically expands for readability
