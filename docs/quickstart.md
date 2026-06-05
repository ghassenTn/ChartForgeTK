# Quick Start

## Minimal Example

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

## Common Pattern

Every chart follows the same three-step pattern:

1. **Create** the chart with a parent widget and dimensions
2. **Pack/place** it in the layout
3. **Plot** data using the chart's `.plot()` method

```python
# 1. Create
chart = LineChart(parent, width=600, height=400)

# 2. Layout
chart.pack(fill="both", expand=True)

# 3. Plot
chart.plot([10, 15, 13, 18, 16, 20])
```

## Chart Types

| Chart | Import | `.plot()` Input |
|-------|--------|-----------------|
| BarChart | `from ChartForgeTK import BarChart` | `list[float]`, labels |
| LineChart | `from ChartForgeTK import LineChart` | `list[float]` or list of dicts |
| PieChart | `from ChartForgeTK import PieChart` | `list[float]`, labels |
| ScatterPlot | `from ChartForgeTK import ScatterPlot` | `list[tuple]` (x, y) |
| BubbleChart | `from ChartForgeTK import BubbleChart` | `list[tuple]` (x, y, size) |
| BoxPlot | `from ChartForgeTK import BoxPlot` | `list[list[float]]`, labels |
| Histogram | `from ChartForgeTK import Histogram` | `list[float]`, bins |
| CandlestickChart | `from ChartForgeTK import CandlestickChart` | `list[tuple]` (idx, O, H, L, C) |
| TableauChart | `from ChartForgeTK import TableauChart` | `list[dict]` |
| GanttChart | `from ChartForgeTK import GanttChart` | Task data |
| NetworkGraph | `from ChartForgeTK import NetworkGraph` | Nodes + edges |
| HeatMap | `from ChartForgeTK import HeatMap` | Matrix |

## Constructor Parameters

All chart constructors accept these common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parent` | Widget | `None` | Parent Tkinter widget |
| `width` | int | `800` | Chart width in pixels |
| `height` | int | `600` | Chart height in pixels |
| `theme` | str | `'light'` | Color theme |
| `display_mode` | str | `'frame'` | `'frame'` or `'window'` |
| `palette` | str | `'modern'` | Color palette |
