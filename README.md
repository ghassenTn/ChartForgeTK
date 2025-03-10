ChartForgeTK

ChartForgeTK is a powerful and intuitive Python charting library built on pure Tkinter. It brings modern, interactive data visualization to desktop applications without external dependencies. Perfect for data scientists, developers, and anyone needing beautiful charts in their Tkinter applications.

The library combines the reliability of Tkinter with contemporary design principles to offer:

    Smooth, animated visualizations

    Interactive charts with tooltips and click events

    Multiple chart types from basic to advanced

    Zero external dependencies

    Modern, customizable themes

A modern, smooth, and dynamic charting library for Python using pure Tkinter. Create beautiful, interactive charts with minimal code.
🌟 Features
🎨 Modern and Clean Design

    Smooth animations for transitions and interactions

    Sleek, professional-looking charts

📊 Comprehensive Chart Types

    Line Charts: Smooth transitions and customizable styles

    Bar Charts: Grouped, stacked, and horizontal bars

    Pie Charts: Interactive segments with hover effects

    Scatter Plots: Custom markers and dynamic scaling

    Bubble Charts: Size encoding for additional data dimensions

    Heatmaps: Customizable color schemes and gradients

    Network Graphs: Force-directed layouts for complex relationships

    Area Charts: Gradient fills and multi-series support

    Box Plots: Statistical data visualization

    Histograms: Binned data with interactive tooltips

    Candlestick Charts: Financial data visualization

    Gantt Charts: Task scheduling and timeline visualization

    Tableau Charts: Tabular data with rich formatting

✨ Rich Interactive Features

    Dynamic tooltips with customizable content

    Smooth hover effects and animations

    Click handlers for data point interaction

    Zoom and pan capabilities

    Legend interaction and dynamic updates

🎯 Zero External Dependencies

    Built with pure Tkinter

    Native Python implementation

    Lightweight and fast

🎨 Extensive Customization

    Multiple built-in themes (light, dark, modern)

    Custom color palettes

    Configurable animations

    Flexible styling options for fonts, colors, and layouts

📱 Responsive Design

    Auto-resizing charts

    Adaptive layouts for different screen sizes

    Dynamic data updates without redrawing

🚀 Developer-Friendly

    Intuitive API design

    Comprehensive documentation with examples

    Type hints for better IDE support

    Easy integration into existing Tkinter applications

📦 Installation
bash
Copy

pip install ChartForgeTK

🚀 Quick Start
Basic Line Chart
python
Copy

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

🎯 Examples
Interactive Line Chart
python
Copy

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

Animated Bubble Chart
python
Copy

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

Area Chart with Multiple Series
python
Copy

from ChartForgeTK import AreaChart
import tkinter as tk

root = tk.Tk()
chart = AreaChart(root)
chart.pack(fill="both", expand=True)

# Create sample data for multiple series
series1 = [10, 25, 15, 30, 20, 35, 25]
series2 = [5, 15, 10, 20, 15, 25, 20]
labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
series_names = ["Revenue", "Costs"]

# Plot with gradient colors and hover effect
def on_hover(series_idx, point_idx):
    print(f"Series {series_names[series_idx]}: {labels[point_idx]}")

chart.plot(
    data=[series1, series2],
    labels=labels,
    series_names=series_names,
    title="Weekly Financial Overview",
    animate=True,
    animation_duration=1000,
    on_hover=on_hover
)

root.mainloop()

🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details on:

    Code style

    Development setup

    Testing

    Pull request process

📄 License

ChartForgeTK is released under the MIT License. See the LICENSE file for details.
🌟 Show Your Support

If you find ChartForgeTK helpful, please consider:

    Giving it a star on GitHub

    Sharing it with others

    Contributing to its development

📬 Contact

    Report issues on our GitHub Issues

    Join our Discord community

    Follow updates on Twitter