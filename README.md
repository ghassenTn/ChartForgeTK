ChartForgeTK

ChartForgeTK is a powerful and intuitive Python charting library built purely on Tkinter. It brings modern, interactive data visualization to desktop applications with zero external dependencies. Designed for data scientists, developers, and enthusiasts, ChartForgeTK makes creating beautiful charts in Tkinter applications effortless.
![Screenshot From 2025-03-10 09-59-06](https://github.com/user-attachments/assets/f63687dc-d73a-49e6-920b-b1c293756c05)

🚀 Why Choose ChartForgeTK?

✅ Completely Standalone – No external dependencies, just pure Tkinter.
✅ Rich Charting Capabilities – Supports a wide variety of charts.
✅ Highly Customizable – Theming, flexible sizing, and adaptable layouts.
✅ Interactive & Dynamic – Easily refresh and update data.
✅ Lightweight & Fast – Ideal for small and large-scale Tkinter applications.

🌟 Features

📊 Comprehensive Chart Types

Bar Charts – Great for categorical comparisons.

Line Charts – Ideal for trends and time-series data.

Pie Charts – Perfect for proportion-based data visualization.

Scatter Plots – Analyze relationships between data points.

Bubble Charts – Scatter plots with size-encoded values.

Box Plots – Visualize data distribution and outliers.

Histograms – Display frequency distributions.

Gantt Charts – Plan projects and visualize timelines.

Candlestick Charts – Financial market trends at a glance.

Tableau Charts – Enhanced table-based visual representation.

✨ Interactive Features

Refreshable Data – Update charts dynamically.

Tabbed Interface – Organize multiple visualizations seamlessly.

Responsive Layouts – Adaptive resizing for different screen sizes.

🎯 Zero External Dependencies

Built entirely with Tkinter – No need for third-party libraries.

Lightweight and native Python implementation.

🎨 Customization Options

Theme Support – Light/Dark modes.

Configurable Sizes – Adjust chart dimensions easily.

Flexible Data Formatting – Adapt charts to specific needs.

📦 Installation

Install ChartForgeTK using pip:

```python
pip install ChartForgeTK
```
🚀 Quick Start

Here's a simple example to get you started:
```python
import tkinter as tk
from ChartForgeTK import BarChart
```
# Create window
```python
root = tk.Tk()
root.geometry("800x600")
```

# Create and configure chart
```python
chart = BarChart(root, width=780, height=520)
chart.pack(fill="both", expand=True)
```

# Plot data
```python
data = [10, 20, 15, 25, 30]
labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
chart.plot(data, labels)
```
# Start application
```python
root.mainloop()
```
🎯 Complete Dashboard Example

Here’s an advanced example demonstrating a multi-tab dashboard with various chart types:
```python
import tkinter as tk
from tkinter import ttk
from ChartForgeTK import (
    LineChart, BarChart, PieChart, BubbleChart,
    ScatterPlot, BoxPlot, Histogram, GanttChart,
    CandlestickChart, TableauChart
)
import random

class ChartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChartForgeTK Dashboard")
        self.geometry("800x600")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bar Chart Tab
        bar_frame = ttk.Frame(notebook)
        notebook.add(bar_frame, text="Bar Chart")
        self.bar_chart = BarChart(bar_frame, width=780, height=520)
        self.bar_chart.pack(fill='both', expand=True)
        bar_data = [10, 20, 15, 25, 30]
        bar_labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        self.bar_chart.plot(bar_data, bar_labels)
        ttk.Button(bar_frame, text="Refresh Data",
                  command=self.refresh_bar_data).pack(pady=5)

    def refresh_bar_data(self):
        new_data = [random.randint(5, 30) for _ in range(5)]
        new_labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        self.bar_chart.plot(new_data, new_labels)

if __name__ == "__main__":
    app = ChartApp()
    app.mainloop()
```
📋 Requirements

Python 3.6+

Tkinter (included with Python by default)

🎨 Customization Options

✅ Resizable Charts – Define custom dimensions.
✅ Light/Dark Themes – Adapt to user preferences.
✅ Live Data Updates – Dynamic refresh for real-time changes.
✅ Tabbed Interface – Organize charts effectively.
✅ Scalable for Large Datasets – Handles big data efficiently.

🔮 Roadmap

🔹 More Chart Types – Heatmaps, Radar Charts, Tree Maps.
🔹 Drag & Drop Support – Enhance interactivity.
🔹 Export Options – Save charts as images or CSV.
🔹 Extended Styling – More themes and customization.

🤝 Contributing

Contributions are always welcome! Here’s how you can help:

1️⃣ Fork the repository
2️⃣ Create a feature branch (git checkout -b feature-newchart)
3️⃣ Commit your changes (git commit -m "Added new chart type")
4️⃣ Push to your branch (git push origin feature-newchart)
5️⃣ Open a Pull Request 🚀

📄 License

ChartForgeTK is open-source and released under the MIT License.

📬 Contact & Support

💡 Found an issue? Have a suggestion? We’d love to hear from you!

Submit an Issue – Report bugs and feature requests on GitHub.

Reach Out to Maintainers – Connect through the repository.

🔥 Bring your Tkinter apps to life with ChartForgeTK! 🚀
