import tkinter as tk
from tkinter import ttk
import sys
import os
import math

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartlib import LineChart, BarChart, PieChart

class ChartDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Chart Dashboard Example")
        self.geometry("1200x800")
        
        # Create main container
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create grid layout
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        # Create charts
        self.create_line_chart(container, 0, 0)
        self.create_bar_chart(container, 0, 1)
        self.create_pie_chart(container, 1, 0)
        self.create_controls(container, 1, 1)
        
    def create_line_chart(self, parent, row, col):
        # Create damped sine wave data
        data = [math.sin(x/10) * math.exp(-x/50) for x in range(100)]
        
        chart = LineChart(parent, width=500, height=300)
        chart.title = "Damped Sine Wave"
        chart.x_label = "Time"
        chart.y_label = "Amplitude"
        chart.plot(data)
        chart.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
    def create_bar_chart(self, parent, row, col):
        # Monthly sales data
        data = [45000, 52000, 48000, 58000, 56000, 66000, 
                71000, 63000, 60000, 66000, 71000, 75000]
        
        chart = BarChart(parent, width=500, height=300)
        chart.title = "Monthly Sales Performance"
        chart.x_label = "Month"
        chart.y_label = "Sales ($)"
        chart.plot(data)
        chart.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
    def create_pie_chart(self, parent, row, col):
        # Market share data
        values = [38, 27, 18, 12, 5]
        labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Others']
        
        chart = PieChart(parent, width=500, height=300)
        chart.title = "Market Share Distribution"
        chart.plot(values, labels)
        chart.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
    def create_controls(self, parent, row, col):
        # Create a frame for controls
        control_frame = ttk.LabelFrame(parent, text="Controls")
        control_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Add some example controls
        ttk.Label(control_frame, text="Chart Controls").pack(pady=10)
        ttk.Button(control_frame, text="Refresh Data").pack(pady=5)
        ttk.Button(control_frame, text="Export Charts").pack(pady=5)

if __name__ == "__main__":
    app = ChartDashboard()
    app.mainloop()
