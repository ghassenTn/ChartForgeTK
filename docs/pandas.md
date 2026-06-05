# Pandas Integration

ChartForgeTK seamlessly integrates with pandas DataFrames and Series.
This is an **optional** feature — all charts work with plain Python lists
when pandas is not installed.

## BarChart with DataFrame

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

## PieChart with Series

```python
import pandas as pd
from ChartForgeTK import PieChart

series = pd.Series(
    [30, 25, 20, 15, 10],
    index=['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
)

chart = PieChart(parent, width=600, height=400)
chart.plot(series)  # Index becomes labels automatically
```

## Multi-Series LineChart from DataFrame

```python
import pandas as pd
from ChartForgeTK import LineChart

df = pd.DataFrame({
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'revenue': [100, 120, 115, 130, 145],
    'expenses': [80, 85, 90, 95, 100],
    'profit': [20, 35, 25, 35, 45]
})

chart = LineChart(parent, width=600, height=400)
chart.plot(df, y_columns=['revenue', 'expenses', 'profit'], label_column='month')
```

## ScatterPlot from DataFrame

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

## Histogram with Series

```python
import pandas as pd
from ChartForgeTK import Histogram

series = pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5])

chart = Histogram(parent, width=600, height=400)
chart.plot(series, bins=5)
```
