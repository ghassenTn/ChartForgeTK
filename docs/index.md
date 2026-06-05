# ChartForgeTK

A powerful and intuitive Python charting library built purely on Tkinter. ChartForgeTK brings
modern, interactive data visualization to desktop applications with **zero external dependencies**.

[![PyPI version](https://badge.fury.io/py/chartforgetk.svg)](https://pypi.org/project/chartforgetk/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tkinter](https://img.shields.io/badge/Framework-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

## Why ChartForgeTK?

| Feature | ChartForgeTK |
|---------|--------------|
| Dependencies | **Zero external dependencies** — pure Tkinter |
| Chart Types | 12+ chart types for any visualization need |
| Customization | Light/Dark themes, flexible sizing |
| Interactivity | Tooltips, hover effects, click events |
| Data Sources | Lists, pandas DataFrames, pandas Series |
| Performance | Lightweight, fast rendering with animations |
| Stability | Comprehensive input validation (v2.0) |

## Features

### Chart Types

| Chart | Description | Best For |
|-------|-------------|----------|
| Bar Chart | Vertical bars with animations | Categorical comparisons |
| Line Chart | Multi-series with markers | Trends, time-series |
| Pie Chart | 2D/3D with slice selection | Proportions |
| Scatter Plot | X-Y coordinate plotting | Correlations |
| Bubble Chart | Scatter with size encoding | 3-variable data |
| Box Plot | Statistical distribution | Outlier detection |
| Histogram | Frequency distribution | Data distribution |
| Gantt Chart | Timeline visualization | Project planning |
| Candlestick | OHLC financial data | Stock analysis |
| Heat Map | Color-coded matrices | Pattern recognition |
| Network Graph | Node-edge visualization | Relationships |
| Tableau Chart | Enhanced data tables | Tabular display |

### Interactive Features

- **Animated chart rendering** with smooth transitions
- **Hover tooltips** with detailed information
- **Click-to-select** functionality (pie charts)
- **Dynamic data refresh** without flickering
- **Responsive layouts** with auto-resize support

### Zero Dependencies

ChartForgeTK uses only Python's built-in `tkinter` module — no NumPy, no Matplotlib,
no external packages required. Optional pandas integration is available for DataFrame
support when pandas is installed.

## Quick Example

```python
import tkinter as tk
from ChartForgeTK import BarChart

root = tk.Tk()
root.title("My First Chart")
root.geometry("800x600")

chart = BarChart(root, width=780, height=520)
chart.pack(fill="both", expand=True)
chart.plot([10, 20, 15, 25, 30], ["Q1", "Q2", "Q3", "Q4", "Q5"])

root.mainloop()
```

## License

ChartForgeTK is open-source and released under the [Apache License 2.0](https://github.com/ghassenTn/ChartForgeTK/blob/main/LICENSE).
