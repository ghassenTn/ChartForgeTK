import tkinter as tk
from tkinter import ttk
import math
import sys
import os
import random

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chartlib.core import LineChart, BarChart, PieChart
from chartlib.advanced_charts import (
    ColumnChart, GroupedBarChart, ScatterPlot,
    BubbleChart, Heatmap, NetworkGraph
)

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Add the frame to the canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scroll area
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure canvas size on window resize
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Add mousewheel scrolling
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)
        
        # Pack everything
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def on_canvas_configure(self, event):
        # Update the scrollable region when the canvas is resized
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

class ChartDisplayDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Chart Gallery")
        self.root.geometry("1600x900")
        self.root.configure(bg="#F8FAFC")
        
        # Configure modern style
        style = ttk.Style()
        style.configure(".", font=("Inter", 11))
        style.configure("TFrame", background="#F8FAFC")
        style.configure("Card.TFrame", background="#FFFFFF")
        style.configure("TButton", 
                       padding=10,
                       font=("Inter", 11))
        style.configure("Selected.TButton",
                       background="#6366F1",
                       foreground="#FFFFFF")
        style.configure("TLabelframe", 
                       background="#F8FAFC",
                       padding=15)
        style.configure("TLabelframe.Label", 
                       font=("Inter", 14, "bold"),
                       foreground="#1E293B",
                       background="#F8FAFC")
        
        # Create main container with padding
        self.main_frame = ttk.Frame(root, style="TFrame", padding=20)
        self.main_frame.pack(fill='both', expand=True)
        
        # Title section
        title_frame = ttk.Frame(self.main_frame, style="TFrame")
        title_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(title_frame, 
                         text="Chart Gallery",
                         font=("Inter", 24, "bold"),
                         foreground="#1E293B",
                         background="#F8FAFC")
        title.pack(side='left')
        
        subtitle = ttk.Label(title_frame,
                           text="A showcase of different chart types and display modes",
                           font=("Inter", 14),
                           foreground="#64748B",
                           background="#F8FAFC")
        subtitle.pack(side='left', padx=(20, 0))
        
        # Display mode selection
        controls_frame = ttk.LabelFrame(self.main_frame, 
                                      text="Display Mode",
                                      style="TLabelframe")
        controls_frame.pack(fill='x', pady=(0, 20))
        
        self.display_mode = tk.StringVar(value='frame')
        
        ttk.Radiobutton(controls_frame,
                       text="Embedded",
                       value='frame',
                       variable=self.display_mode,
                       command=self.refresh_charts).pack(side='left', padx=5)
        
        ttk.Radiobutton(controls_frame,
                       text="Window",
                       value='window',
                       variable=self.display_mode,
                       command=self.refresh_charts).pack(side='left', padx=5)
        
        # Create scrollable frame for charts
        self.scroll_frame = ScrollableFrame(self.main_frame)
        self.scroll_frame.pack(fill='both', expand=True)
        
        # Configure grid for charts
        for i in range(3):
            self.scroll_frame.scrollable_frame.grid_columnconfigure(i, weight=1)
        
        self.create_charts()
    
    def create_charts(self):
        # Clear existing charts
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Sample data
        line_data = [math.sin(x/5) * 50 + 50 for x in range(5)]
        line_labels = [f"Day {i+1}" for i in range(5)]
        
        bar_data = [45, 62, 48, 58, 72]
        bar_labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        
        column_data = [120, 150, 180, 210, 160, 190]
        column_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        grouped_data = [
            [45, 62, 38, 51],  # Region 1
            [30, 45, 55, 41],  # Region 2
            [25, 35, 45, 40],  # Region 3
        ]
        grouped_categories = ["Q1", "Q2", "Q3", "Q4"]
        grouped_series = ["Region A", "Region B", "Region C"]
        
        scatter_x = [random.uniform(20, 80) for _ in range(10)]
        scatter_y = [x * 0.5 + random.uniform(-10, 10) + 10 for x in scatter_x]
        
        pie_data = [35, 25, 20, 15, 5]
        pie_labels = ["Product A", "Product B", "Product C", "Product D", "Others"]
        
        bubble_x = [1, 2, 3, 4, 5]
        bubble_y = [2, 4, 3, 5, 4]
        bubble_sizes = [10, 30, 20, 40, 15]
        bubble_labels = ["A", "B", "C", "D", "E"]
        
        heatmap_data = [
            [1.0, 0.8, 0.6, 0.4],
            [0.8, 1.0, 0.7, 0.5],
            [0.6, 0.7, 1.0, 0.8],
            [0.4, 0.5, 0.8, 1.0]
        ]
        heatmap_labels = ["A", "B", "C", "D"]
        
        nodes = ["A", "B", "C", "D", "E"]
        edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A"), ("B", "D")]
        node_values = [1.0, 2.0, 1.5, 2.5, 1.8]
        edge_values = [0.5, 1.0, 0.8, 1.2, 0.7, 1.5]
        
        # Create chart frames
        charts = [
            ("Line Chart", LineChart, line_data, line_labels),
            ("Bar Chart", BarChart, bar_data, bar_labels),
            ("Column Chart", ColumnChart, column_data, column_labels),
            ("Grouped Bar Chart", GroupedBarChart, grouped_data, (grouped_categories, grouped_series)),
            ("Scatter Plot", ScatterPlot, (scatter_x, scatter_y), None),
            ("Pie Chart", PieChart, pie_data, pie_labels),
            ("Bubble Chart", BubbleChart, (bubble_x, bubble_y, bubble_sizes), bubble_labels),
            ("Heatmap", Heatmap, heatmap_data, heatmap_labels),
            ("Network Graph", NetworkGraph, (nodes, edges, node_values, edge_values), None)
        ]
        
        for i, (title, chart_class, data, labels) in enumerate(charts):
            # Create frame for chart
            frame = ttk.Frame(self.scroll_frame.scrollable_frame, style="Card.TFrame", padding=15)
            frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            # Add title
            ttk.Label(frame,
                     text=title,
                     font=("Inter", 14, "bold"),
                     background="#FFFFFF",
                     foreground="#1E293B").pack(pady=(0, 10))
            
            # Create chart
            chart = chart_class(frame, width=450, height=300,
                              display_mode=self.display_mode.get())
            
            if self.display_mode.get() == 'frame':
                chart.pack(fill='both', expand=True)
            
            # Plot data based on chart type
            if isinstance(chart, GroupedBarChart):
                chart.plot(data, labels[0], labels[1])
            elif isinstance(chart, ScatterPlot):
                chart.plot(data[0], data[1], show_trend=True)
            elif isinstance(chart, BubbleChart):
                chart.plot(data[0], data[1], data[2], labels)
            elif isinstance(chart, Heatmap):
                chart.plot(data, labels, labels)
            elif isinstance(chart, NetworkGraph):
                chart.plot(data[0], data[1], data[2], data[3])
            elif isinstance(chart, PieChart):
                chart.plot(data, labels)
            elif isinstance(chart, LineChart):
                chart.plot(data, labels)
            else:
                chart.plot(data)
            
            # Store chart configuration for redraw
            chart.data = data
            if isinstance(chart, GroupedBarChart):
                chart.category_labels = labels[0]
                chart.series_labels = labels[1]
            elif isinstance(chart, ScatterPlot):
                chart.x_data = data[0]
                chart.y_data = data[1]
                chart.show_trend = True
            elif isinstance(chart, BubbleChart):
                chart.x_data = data[0]
                chart.y_data = data[1]
                chart.sizes = data[2]
                chart.labels = labels
            elif isinstance(chart, Heatmap):
                chart.row_labels = labels
                chart.col_labels = labels
            elif isinstance(chart, NetworkGraph):
                chart.nodes = data[0]
                chart.edges = data[1]
                chart.node_values = data[2]
                chart.edge_values = data[3]
            elif isinstance(chart, PieChart):
                chart.labels = labels
    
    def refresh_charts(self):
        self.create_charts()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChartDisplayDemo(root)
    root.mainloop()
