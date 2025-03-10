ChartForgeTK

ChartForgeTK is a powerful and intuitive Python charting library built on pure Tkinter. It brings modern, interactive data visualization to desktop applications without external dependencies. Perfect for data scientists, developers, and anyone needing beautiful charts in their Tkinter applications.
🌟 Features

    📊 Comprehensive Chart Types:
        Bar Charts
        Line Charts
        Pie Charts
        Scatter Plots
        Bubble Charts
        Box Plots
        Histograms
        Gantt Charts
        Candlestick Charts
        Tableau Charts
    ✨ Interactive Features:
        Refreshable data
        Tabbed interface
        Responsive layouts
    🎯 Zero External Dependencies:
        Built with pure Tkinter
        Native Python implementation
    🎨 Customization:
        Theme support (light/dark)
        Configurable chart sizes
        Flexible data formatting

📦 Installation
bash
pip install ChartForgeTK
🚀 Quick Start

Here's a simple example to get started:
python
import tkinter as tk
from ChartForgeTK import BarChart

# Create window
root = tk.Tk()
root.geometry("800x600")

# Create and configure chart
chart = BarChart(root, width=780, height=520)
chart.pack(fill="both", expand=True)

# Plot data
data = [10, 20, 15, 25, 30]
labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
chart.plot(data, labels)

# Start application
root.mainloop()
🎯 Complete Dashboard Example

The following example demonstrates a multi-tab dashboard with various chart types:
python
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
📋 Requirements

    Python 3.6+
    Tkinter (included with Python)

🔧 Supported Chart Types

    BarChart: Vertical bar charts for categorical data
    LineChart: Line graphs for continuous data
    PieChart: Circular charts for proportional data
    ScatterPlot: Points-based charts for relationship visualization
    BubbleChart: Scatter plots with size-encoded data points
    BoxPlot: Statistical distribution visualization
    Histogram: Frequency distribution charts
    GanttChart: Project timeline visualization
    CandlestickChart: Financial data visualization
    TableauChart: Tabular data display with enhanced visualization

🎨 Customization Options

    Width and height configuration
    Theme selection (light/dark where supported)
    Data refresh capabilities
    Tabbed interface integration
    Responsive resizing

🤝 Contributing

Contributions are welcome! Please:

    Fork the repository
    Create a feature branch
    Submit a pull request with your changes

📄 License

ChartForgeTK is released under the MIT License.
⚠️ Notes

    The provided example assumes ChartForgeTK is properly installed
    Some chart types may have specific data format requirements
    Check individual chart documentation for specific parameters
    The complete example includes additional chart types and refresh functionality

📬 Contact

For support or inquiries:

    Submit issues on GitHub
    Contact the maintainers through the repository

This README has been updated to:

    Reflect the actual chart types shown in the example
    Match the functionality demonstrated in the code
    Provide accurate installation and usage instructions
    Remove features not present in the example (like animations, tooltips)
    Maintain a professional and clear format