# Tableau Chart

Enhanced data table for tabular display with row striping.

```python
from ChartForgeTK import TableauChart

data = [
    {"Name": "Alice", "Age": 25, "Score": 95.5, "City": "New York"},
    {"Name": "Bob", "Age": 30, "Score": 87.0, "City": "London"},
    {"Name": "Charlie", "Age": 22, "Score": 91.2, "City": "Paris"}
]

chart = TableauChart(parent, width=600, height=400)
chart.plot(data)
```

## Parameters

### `TableauChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[dict]` | List of dictionaries with uniform keys |

Column headers are automatically derived from dictionary keys. Each row
represents one dictionary entry. Values are displayed as strings.
