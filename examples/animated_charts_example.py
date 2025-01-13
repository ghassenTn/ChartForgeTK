import tkinter as tk
from tkinter import ttk
import sys
import os
import random
import math
import time
import threading
from time import sleep

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartlib.advanced_charts import ColumnChart, GroupedBarChart, ScatterPlot
from chartlib.core import LineChart

class AnimatedChartsDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated Charts Demo")
        self.root.geometry("1600x900")
        self.root.configure(bg="#F8FAFC")
        
        # Configure modern style
        style = ttk.Style()
        style.configure(".", font=("Inter", 11))
        style.configure("TFrame", background="#F8FAFC")
        style.configure("Title.TLabel", 
                       font=("Inter", 24, "bold"),
                       background="#F8FAFC",
                       foreground="#1E293B")
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(self.main_frame, 
                         text="Real-time Chart Gallery",
                         style="Title.TLabel")
        title.pack(pady=(0, 20))
        
        # Create frames for charts
        self.create_chart_frames()
        
        # Initialize data
        self.init_data()
        
        # Create and display charts
        self.create_charts()
        
        # Initial plots
        self.update_all_charts()
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def create_chart_frames(self):
        # Create a frame for each row
        self.row1_frame = ttk.Frame(self.main_frame)
        self.row1_frame.pack(fill='x', expand=True, pady=(0, 20))
        
        self.row2_frame = ttk.Frame(self.main_frame)
        self.row2_frame.pack(fill='x', expand=True)
        
        # Create frames for each chart
        self.line_frame = ttk.Frame(self.row1_frame)
        self.line_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.column_frame = ttk.Frame(self.row1_frame)
        self.column_frame.pack(side='right', fill='both', expand=True)
        
        self.grouped_frame = ttk.Frame(self.row2_frame)
        self.grouped_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.scatter_frame = ttk.Frame(self.row2_frame)
        self.scatter_frame.pack(side='right', fill='both', expand=True)
    
    def init_data(self):
        # Line chart data (time series)
        self.line_data = [50] * 20
        
        # Column chart data (monthly values)
        self.column_data = [random.randint(50, 150) for _ in range(6)]
        self.column_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        # Grouped bar chart data (product sales by region)
        self.grouped_data = [
            [random.randint(30, 60) for _ in range(4)],  # Region 1
            [random.randint(30, 60) for _ in range(4)],  # Region 2
            [random.randint(30, 60) for _ in range(4)],  # Region 3
        ]
        self.grouped_categories = ["Q1", "Q2", "Q3", "Q4"]
        self.grouped_series = ["Region A", "Region B", "Region C"]
        
        # Scatter plot data
        self.scatter_x = [random.uniform(0, 100) for _ in range(30)]
        self.scatter_y = [x * 0.5 + random.uniform(-10, 10) for x in self.scatter_x]
    
    def create_charts(self):
        # Create charts with titles
        self.line_chart = self.create_chart_with_title(
            LineChart, self.line_frame, "Sensor Data", 700, 350)
        
        self.column_chart = self.create_chart_with_title(
            ColumnChart, self.column_frame, "Monthly Performance", 700, 350)
        
        self.grouped_chart = self.create_chart_with_title(
            GroupedBarChart, self.grouped_frame, "Regional Sales", 700, 350)
        
        self.scatter_chart = self.create_chart_with_title(
            ScatterPlot, self.scatter_frame, "Correlation Analysis", 700, 350)
    
    def create_chart_with_title(self, chart_class, parent, title, width, height):
        # Create title label
        title_label = ttk.Label(parent, 
                              text=title,
                              font=("Inter", 16, "bold"),
                              background="#F8FAFC",
                              foreground="#1E293B")
        title_label.pack(pady=(0, 10))
        
        # Create chart
        chart = chart_class(parent, width=width, height=height)
        chart.pack(fill='both', expand=True)
        return chart
    
    def update_all_charts(self):
        try:
            # Update line chart
            self.line_chart.plot(self.line_data)
            
            # Update column chart
            self.column_chart.plot(self.column_data, self.column_labels)
            
            # Update grouped bar chart
            self.grouped_chart.plot(
                self.grouped_data,
                self.grouped_categories,
                self.grouped_series
            )
            
            # Update scatter plot
            self.scatter_chart.plot(
                self.scatter_x,
                self.scatter_y,
                show_trend=True
            )
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def update_data(self):
        while self.running:
            try:
                # Update line chart with sine wave
                new_value = 50 + 30 * math.sin(time.time()) + random.randint(-5, 5)
                self.line_data = self.line_data[1:] + [new_value]
                
                # Update column chart with random changes
                self.column_data = [
                    max(50, min(150, x + random.randint(-5, 5)))
                    for x in self.column_data
                ]
                
                # Update grouped bar chart
                for series in self.grouped_data:
                    for i in range(len(series)):
                        series[i] = max(30, min(60, series[i] + random.randint(-2, 2)))
                
                # Update scatter plot with moving cluster
                center_x = 50 + 30 * math.cos(time.time() * 0.5)
                center_y = 50 + 30 * math.sin(time.time() * 0.5)
                self.scatter_x = [
                    center_x + random.uniform(-20, 20)
                    for _ in range(30)
                ]
                self.scatter_y = [
                    center_y + random.uniform(-20, 20)
                    for _ in range(30)
                ]
                
                # Update all charts
                self.update_all_charts()
                
                # Sleep between updates
                sleep(0.1)
                
            except tk.TclError:
                # Window was closed
                break
            except Exception as e:
                print(f"Error in update thread: {e}")
                break
    
    def on_closing(self):
        self.running = False
        sleep(0.2)  # Give time for the thread to close
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimatedChartsDemo(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
