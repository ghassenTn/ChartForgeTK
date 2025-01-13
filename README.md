# ChartForgeTK

A modern, smooth, and dynamic charting library for Python using pure Tkinter. Create beautiful, interactive charts with minimal code.

## 🌟 Features

- 🎨 Modern and clean design with smooth animations
- 📊 Comprehensive Chart Types:
  - Line Charts with smooth transitions
  - Bar Charts with customizable styles
  - Pie Charts with interactive segments
  - Column Charts with grouping options
  - Scatter Plots with custom markers
  - Bubble Charts with size encoding
  - Heatmaps with customizable color schemes
  - Network Graphs with force-directed layouts
  - Area Charts with gradient fills
- ✨ Rich Interactive Features:
  - Dynamic tooltips with customizable content
  - Smooth hover effects and animations
  - Click handlers for data point interaction
  - Zoom and pan capabilities
  - Legend interaction
- 🎯 Zero External Dependencies:
  - Built with pure Tkinter
  - Native Python implementation
  - Lightweight and fast
- 🎨 Extensive Customization:
  - Multiple built-in themes
  - Custom color palettes
  - Configurable animations
  - Flexible styling options
- 📱 Responsive Design:
  - Auto-resizing charts
  - Adaptive layouts
  - Dynamic data updates
- 🚀 Developer-Friendly:
  - Intuitive API design
  - Comprehensive documentation
  - Type hints for better IDE support
  - Example-rich documentation

## 📦 Installation

```bash
pip install ChartForgeTK
```

## 🚀 Quick Start

```python
from ChartForgeTK import LineChart
import tkinter as tk

# Create window
root = tk.Tk()
root.geometry("800x600")

# Create and configure chart
chart = LineChart(root)
chart.pack(fill="both", expand=True)

# Plot data with custom styling
data = [10, 45, 30, 60, 25, 85, 40]
labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
chart.plot(
    data,
    labels=labels,
    title="Weekly Performance",
    theme="modern",
    animate=True
)

# Start application
root.mainloop()
```

## 📚 Documentation

Visit our [documentation](https://chartforgetk.readthedocs.io/) for:
- Detailed API reference
- Advanced usage examples
- Theming guide
- Best practices
- Troubleshooting

## 🎯 Examples

### Interactive Line Chart
```python
from ChartForgeTK import LineChart
import tkinter as tk

root = tk.Tk()
chart = LineChart(root)
chart.pack(fill="both", expand=True)

# Add interactive features
def on_point_click(point_index):
    print(f"Clicked point {point_index}")

data = [10, 45, 30, 60, 25]
labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
chart.plot(
    data,
    labels=labels,
    title="Interactive Demo",
    on_click=on_point_click,
    show_tooltip=True
)

root.mainloop()
```

### Animated Bubble Chart
```python
from ChartForgeTK import BubbleChart
import tkinter as tk

root = tk.Tk()
chart = BubbleChart(root)
chart.pack(fill="both", expand=True)

# Create animated bubble chart
x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 3, 5, 4]
sizes = [10, 30, 20, 40, 15]
labels = ["A", "B", "C", "D", "E"]

chart.plot(
    x_data,
    y_data,
    sizes,
    labels,
    animate=True,
    animation_duration=1000
)

root.mainloop()
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Code style
- Development setup
- Testing
- Pull request process

## 📄 License

ChartForgeTK is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If you find ChartForgeTK helpful, please consider:
- Giving it a star on GitHub
- Sharing it with others
- Contributing to its development

## 📬 Contact

- Report issues on our [GitHub Issues](https://github.com/yourusername/ChartForgeTK/issues)
- Join our [Discord community](https://discord.gg/chartforgetk)
- Follow updates on [Twitter](https://twitter.com/ChartForgeTK)
