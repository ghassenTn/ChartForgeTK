# Pie Chart

2D/3D pie chart with slice selection for proportions.

```python
from ChartForgeTK import PieChart

# 2D Pie Chart
chart = PieChart(parent, width=600, height=400)
chart.plot([30, 20, 15, 35], ["A", "B", "C", "D"])

# 3D Pie Chart
chart_3d = PieChart(parent, width=600, height=400, is_3d=True)
chart_3d.plot([30, 20, 15, 35], ["A", "B", "C", "D"])
```

## Parameters

### `PieChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[float]`, Series, or DataFrame | Slice values |
| `labels` | `list[str]`, optional | Slice labels |
| `value_column` | `str`, optional | Column name for DataFrame |
| `label_column` | `str`, optional | Column name for DataFrame labels |

## Constructor

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_3d` | bool | `False` | Enable 3D perspective effect |
| `theme` | str | `'light'` | Color theme |

## Interactive Features

- **Click-to-select** slices (clicked slice detaches slightly)
- **Hover tooltips** with value and percentage
- **Animation** on initial render

## Edge Cases

- All-zero data is detected and handled gracefully
- Single slice renders as a full circle
