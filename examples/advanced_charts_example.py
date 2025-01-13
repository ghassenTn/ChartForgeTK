import tkinter as tk
from tkinter import ttk
import sys
import os
import random
import math

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartlib.advanced_charts import ColumnChart, GroupedBarChart, ScatterPlot

class AdvancedChartsDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Charts Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg="#F8FAFC")
        
        # Configure modern style
        style = ttk.Style()
        style.configure(".", font=("Inter", 11))
        style.configure("TFrame", background="#F8FAFC")
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create frames for each chart
        left_frame = ttk.Frame(self.main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Create and display charts
        self.create_column_chart(left_frame)
        self.create_grouped_bar_chart(right_frame)
        self.create_scatter_plot(left_frame)
    
    def create_column_chart(self, parent):
        # Sample data for monthly sales
        data = [120, 150, 180, 210, 160, 190]
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        chart = ColumnChart(parent, width=500, height=300)
        chart.pack(fill='both', expand=True, pady=(0, 10))
        chart.plot(data, labels)
    
    def create_grouped_bar_chart(self, parent):
        # Sample data for product sales by region
        data = [
            [45, 62, 38, 51],  # Region 1
            [30, 45, 55, 41],  # Region 2
            [25, 35, 45, 40],  # Region 3
        ]
        categories = ["Q1", "Q2", "Q3", "Q4"]
        series = ["Region A", "Region B", "Region C"]
        
        chart = GroupedBarChart(parent, width=500, height=300)
        chart.pack(fill='both', expand=True, pady=(0, 10))
        chart.plot(data, categories, series)
    
    def create_scatter_plot(self, parent):
        # Generate sample data with correlation
        n_points = 50
        x_data = [random.uniform(0, 100) for _ in range(n_points)]
        y_data = [x * 0.5 + random.uniform(-10, 10) for x in x_data]
        
        chart = ScatterPlot(parent, width=500, height=300)
        chart.pack(fill='both', expand=True)
        chart.plot(x_data, y_data, show_trend=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedChartsDemo(root)
    root.mainloop()
