import tkinter as tk
from tkinter import ttk
import math
import random
import sys
import os
from time import sleep
import threading
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartlib.core import LineChart, BarChart, PieChart

class RealtimeChartsDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Realtime Charts Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg="#F8FAFC")
        
        # Configure modern style
        style = ttk.Style()
        style.configure(".", font=("Inter", 11))
        style.configure("TFrame", background="#F8FAFC")
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create charts
        self.setup_charts()
        
        # Initialize data
        self.line_data = [50] * 20  # Last 20 points
        self.bar_data = [random.randint(10, 90) for _ in range(5)]
        self.pie_data = [random.randint(10, 30) for _ in range(4)]
        self.pie_labels = ["A", "B", "C", "D"]  # Store labels
        
        # Initial plots
        self.line_chart.plot(self.line_data)
        self.bar_chart.plot(self.bar_data)
        self.pie_chart.plot(
            data=self.pie_data,
            labels=self.pie_labels
        )
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def setup_charts(self):
        # Create frames for each chart
        left_frame = ttk.Frame(self.main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Create charts
        self.line_chart = LineChart(left_frame, width=600, height=400)
        self.line_chart.pack(fill='both', expand=True, pady=(0, 10))
        
        self.bar_chart = BarChart(right_frame, width=400, height=200)
        self.bar_chart.pack(fill='both', expand=True, pady=(0, 10))
        
        self.pie_chart = PieChart(right_frame, width=400, height=200)
        self.pie_chart.pack(fill='both', expand=True)
    
    def update_data(self):
        while self.running:
            try:
                # Update line chart with simulated sensor data
                new_value = 50 + 30 * math.sin(time.time()) + random.randint(-5, 5)
                self.line_data = self.line_data[1:] + [new_value]
                self.line_chart.plot(self.line_data)
                
                # Update bar chart with random changes
                self.bar_data = [max(10, min(90, x + random.randint(-5, 5))) 
                               for x in self.bar_data]
                self.bar_chart.plot(self.bar_data)
                
                # Update pie chart occasionally
                if random.random() < 0.1:  # 10% chance to update
                    self.pie_data = [max(10, min(30, x + random.randint(-2, 2))) 
                                   for x in self.pie_data]
                    self.pie_chart.plot(
                        data=self.pie_data,
                        labels=self.pie_labels
                    )
                
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
    app = RealtimeChartsDemo(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
