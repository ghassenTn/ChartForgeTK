# Line Chart

Multi-series line chart with markers for trends and time-series data.

```python
from ChartForgeTK import LineChart

# Single series
chart = LineChart(parent, width=600, height=400)
chart.plot([10, 15, 13, 18, 16, 20])

# Multiple series
chart.plot([
    {'data': [10, 15, 13, 18], 'color': '#FF0000', 'label': 'Series A'},
    {'data': [5, 8, 12, 10], 'color': '#00FF00', 'label': 'Series B'}
])
```

## Parameters

### `LineChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[float]`, `list[dict]`, or DataFrame | Data to plot |
| `x_min`, `x_max` | float, optional | X-axis limits |
| `y_min`, `y_max` | float, optional | Y-axis limits |
| `y_columns` | `list[str]`, optional | Column names for multi-series from DataFrame |
| `label_column` | `str`, optional | Column name for x-axis labels |

## Multi-Series Format

Each series is a dictionary:

```python
{
    'data': [10, 15, 13, 18],      # Required: numeric values
    'color': '#FF5733',            # Optional: line color
    'shape': 'circle',             # Optional: circle, square, triangle, diamond
    'label': 'Series A'            # Optional: legend label
}
```

## Constructor Options

```python
chart = LineChart(
    parent,
    width=800,
    height=600,
    show_point_labels=True,           # Show/hide value labels
    use_container_width_height=True   # Auto-resize with parent
)
```
