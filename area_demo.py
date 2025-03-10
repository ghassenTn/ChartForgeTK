import tkinter as tk
from ChartForgeTK import AreaChart
import math
import random

def create_demo_window():
    root = tk.Tk()
    root.title("Area Chart Demo - ChartForgeTK")
    root.geometry("800x600")
    
    # Create frame for controls
    control_frame = tk.Frame(root)
    control_frame.pack(fill="x", padx=10, pady=5)
    
    # Add animation toggle
    animate_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_frame, text="Animate", variable=animate_var).pack(side="left", padx=5)
    
    # Add points toggle
    points_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_frame, text="Show Points", variable=points_var).pack(side="left", padx=5)
    
    # Create the chart
    chart = AreaChart(root)
    chart.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Generate sample data
    days = 30
    base_temp = 20
    temp_range = 10
    
    def generate_data():
        # Temperature data with realistic patterns
        daily_high = [base_temp + temp_range * math.sin(i/5) + random.uniform(-2, 2) for i in range(days)]
        daily_low = [temp - random.uniform(5, 8) for temp in daily_high]
        
        # Precipitation probability
        precipitation = [random.uniform(0, 100) for _ in range(days)]
        
        return daily_high, daily_low, precipitation
    
    daily_high, daily_low, precipitation = generate_data()
    labels = [f"Day {i+1}" for i in range(days)]
    series_names = ["High Temp (°C)", "Low Temp (°C)", "Precipitation (%)"]
    
    def on_hover(series_idx, point_idx, value):
        series_name = series_names[series_idx]
        print(f"{series_name} on Day {point_idx + 1}: {value:.1f}")
    
    def update_chart():
        # Update data
        nonlocal daily_high, daily_low, precipitation
        daily_high, daily_low, precipitation = generate_data()
        
        # Update chart settings
        chart.show_points = points_var.get()
        
        # Plot the data
        chart.plot(
            data=[daily_high, daily_low, precipitation],
            labels=labels,
            series_names=series_names,
            title="30-Day Weather Forecast",
            animate=animate_var.get(),
            animation_duration=1000,
            on_hover=on_hover
        )
    
    # Add refresh button
    tk.Button(control_frame, text="Refresh Data", command=update_chart).pack(side="left", padx=5)
    
    # Initial plot
    update_chart()
    
    return root

if __name__ == "__main__":
    demo_window = create_demo_window()
    demo_window.mainloop()
