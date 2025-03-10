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