<<<<<<< HEAD
# ChartForgeTK
=======
# ChartForgeTK

A modern, smooth, and dynamic charting library for Python using pure Tkinter. Create beautiful, interactive charts with minimal code.

## Features

- 🎨 Modern and clean design
- 📊 Multiple chart types:
  - Line Charts
  - Bar Charts
  - Pie Charts
  - Column Charts
  - Grouped Bar Charts
  - Scatter Plots
  - Bubble Charts
  - Heatmaps
  - Network Graphs
- ✨ Interactive features:
  - Tooltips
  - Hover effects
  - Click handlers
- 🎯 Pure Tkinter - no external dependencies
- 🌈 Customizable themes and styles
- 📱 Responsive and resizable
- 🚀 Easy to use API

## Installation

```bash
pip install ChartForgeTK
```

## Quick Start

```python
from ChartForgeTK import LineChart
import tkinter as tk

# Create window
root = tk.Tk()
root.geometry("800x600")

# Create and configure chart
chart = LineChart(root)
chart.pack(fill="both", expand=True)

# Plot data
data = [10, 45, 30, 60, 25, 85, 40]
chart.plot(data)

# Start application
root.mainloop()
```

## Examples

### Line Chart with Custom Labels
```python
from ChartForgeTK import LineChart
import tkinter as tk

root = tk.Tk()
chart = LineChart(root)
chart.pack(fill="both", expand=True)

data = [10, 45, 30, 60, 25]
labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
chart.plot(data, labels)

root.mainloop()
```

### Interactive Bubble Chart
```python
from ChartForgeTK import BubbleChart
import tkinter as tk

root = tk.Tk()
chart = BubbleChart(root)
chart.pack(fill="both", expand=True)

x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 3, 5, 4]
sizes = [10, 30, 20, 40, 15]
labels = ["A", "B", "C", "D", "E"]

chart.plot(x_data, y_data, sizes, labels)
root.mainloop()
```

### Network Graph
```python
from ChartForgeTK import NetworkGraph
import tkinter as tk

root = tk.Tk()
chart = NetworkGraph(root)
chart.pack(fill="both", expand=True)

nodes = ["A", "B", "C", "D", "E"]
edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")]
node_values = [1.0, 2.0, 1.5, 2.5, 1.8]
edge_values = [0.5, 1.0, 0.8, 1.2]

chart.plot(nodes, edges, node_values, edge_values)
root.mainloop()
```

## Documentation

For more examples and detailed documentation, visit our [GitHub repository](https://github.com/ghassenTn/ChartForgeTK).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
>>>>>>> 4cd24e2 ( * first commit *)
