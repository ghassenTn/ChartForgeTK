# Copyright (c) Ghassen Saidi (2024-2025) - ChartForgeTK
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# GitHub: https://github.com/ghassenTn



import tkinter as tk
from tkinter import ttk
from ChartForgeTK import (
    LineChart,
    BarChart,
    PieChart, 
    NetworkGraph,
    BubbleChart, 
    HeatMap,
    ScatterPlot,
    BoxPlot,
    Histogram,
    CandlestickChart,
    TableauChart,
    GanttChart 
)
import random
import math
from typing import List, Tuple
from datetime import datetime
class ChartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChartForgeTK Dashboard")
        self.geometry("800x600")
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        # Bar Chart Tab 
        bar_frame = ttk.Frame(notebook)
        notebook.add(bar_frame, text="Bar Chart")
        bar_chart = BarChart(bar_frame, width=780, height=520)
        bar_chart.pack(fill='both', expand=True)
        self.bar_chart = bar_chart
        bar_data = [10, 20, 15, 25,30]
        bar_labels = ["Q1", "Q2", "Q3", "Q4","Q5"]
        bar_chart.plot(bar_data, bar_labels)
        ttk.Button(bar_frame, text="Refresh Data", command=self.refresh_bar_data).pack(pady=5)
        # Line Chart Tab 
        line_frame = ttk.Frame(notebook)
        notebook.add(line_frame, text="Line Chart")
        line_chart = LineChart(line_frame, width=780, height=520)
        line_chart.pack(fill='both', expand=True)
        self.line_chart = line_chart
        line_chart.plot([
            {'data': [10, 15, 13, 18, 16, 20], 'color': '#FF0000', 'shape': 'circle', 'label': 'Red Circles'},
            {'data': [5, 8, 7, 12, 10, 15], 'color': '#00FF00', 'shape': 'square', 'label': 'Green Squares'},
            {'data': [15, 12, 14, 10, 13, 11], 'color': '#0000FF', 'shape': 'triangle', 'label': 'Blue Triangles'}
        ])
        ttk.Button(line_frame, text="Refresh Data", command=self.refresh_line_data).pack(pady=5)
        # Pie Chart Tab
        pie_frame = ttk.Frame(notebook)
        notebook.add(pie_frame, text="Pie Chart")
        pie_chart = PieChart(pie_frame, width=780, height=520)
        pie_chart.pack(fill='both', expand=True)
        self.pie_chart = pie_chart
        pie_data = [30, 20, 15, 35,44,34,34]
        pie_labels = ["A", "B", "C", "D","R","E","L"]
        pie_chart.plot(pie_data, pie_labels)
        ttk.Button(pie_frame, text="Refresh Data", command=self.refresh_pie_data).pack(pady=5)
        
        # Scatter Plot Tab
        scatter_frame = ttk.Frame(notebook)
        notebook.add(scatter_frame, text="Scatter Plot")
        scatter_chart = ScatterPlot(scatter_frame, width=780, height=520)
        scatter_chart.pack(fill='both', expand=True)
        self.scatter_chart = scatter_chart
        scatter_data = [(1, 10), (2, 15), (3, 13), (4, 18), (5, 16)]
        scatter_chart.plot(scatter_data)
        ttk.Button(scatter_frame, text="Refresh Data", command=self.refresh_scatter_data).pack(pady=5)
        
        # Bubble Chart Tab 
        bubble_frame = ttk.Frame(notebook)
        notebook.add(bubble_frame, text="Bubble Chart")
        bubble_chart = BubbleChart(bubble_frame, width=780, height=520)
        bubble_chart.pack(fill='both', expand=True)
        self.bubble_chart = bubble_chart
        bubble_data = [(1, 10, 5), (2, 15, 10), (3, 13, 15), (4, 18, 20), (5, 16, 25)]
        bubble_chart.plot(bubble_data)
        ttk.Button(bubble_frame, text="Refresh Data", command=self.refresh_bubble_data).pack(pady=5)
        
        # Box Plot Tab
        box_frame = ttk.Frame(notebook)
        notebook.add(box_frame, text="Box Plot")
        box_chart = BoxPlot(box_frame, width=780, height=520)
        box_chart.pack(fill='both', expand=True)
        self.box_chart = box_chart
        box_data = [[1, 2, 3, 4, 5, 6, 7], [2, 4, 6, 8, 10, 12, 14],
                   [1, 3, 5, 7, 9, 11, 20], [5, 10, 15, 20, 25, 30, 35]]
        box_labels = ["A", "B", "C", "D"]
        box_chart.plot(box_data, box_labels)
        ttk.Button(box_frame, text="Refresh Data", command=self.refresh_box_data).pack(pady=5)
        
        # Histogram Tab 
        hist_frame = ttk.Frame(notebook)
        notebook.add(hist_frame, text="Histogram")
        hist_chart = Histogram(hist_frame, width=780, height=520)
        hist_chart.pack(fill='both', expand=True)
        self.hist_chart = hist_chart
        hist_data = [1, 1.5, 2, 2, 2.5, 3, 3, 3.5, 4, 4.5, 5, 5, 5.5, 6, 6.5]
        hist_chart.plot(hist_data, bins=5)
        ttk.Button(hist_frame, text="Refresh Data", command=self.refresh_hist_data).pack(pady=5)
        # Tableau Chart Tab
        tableau_frame = ttk.Frame(notebook,width=1200,height=500)
        notebook.add(tableau_frame, text="Tableau Chart")
        tableau_chart = TableauChart(tableau_frame, width=1200, height=520,theme='light')
        tableau_chart.pack(fill='both', expand=True)
        self.tableau_chart = tableau_chart
        tableau_data = [

            {"Name": "Alice", "Age": 25, "Score": 95.5, "City": "New York", "Gender": "Female", "Occupation": "Engineer", "Email": "alice@example.com"},
            {"Name": "Bob", "Age": 30, "Score": 87.0, "City": "London", "Gender": "Male", "Occupation": "Doctor", "Email": "bob@example.com"},
            {"Name": "Charlie", "Age": 22, "Score": 91.2, "City": "Paris", "Gender": "Male", "Occupation": "Artist", "Email": "charlie@example.com"},
            {"Name": "David", "Age": 35, "Score": 78.9, "City": "Tokyo", "Gender": "Male", "Occupation": "Teacher", "Email": "david@example.com"},
            {"Name": "Eve", "Age": 28, "Score": 99.1, "City": "Sydney", "Gender": "Female", "Occupation": "Scientist", "Email": "eve@example.com"}
        ]

        tableau_chart.plot(tableau_data)
        ttk.Button(tableau_frame, text="Refresh Data", command=self.refresh_tableau_data).pack(pady=5)

        # Line Chart Label Options Tab
        line_label_options_frame = ttk.Frame(notebook)
        notebook.add(line_label_options_frame, text="Line Chart Labels")

        # Prepare large dataset
        large_data_points = [math.sin(i / 10) * 100 + (i / 2) for i in range(200)]
        datasets_large = [
            {
                'data': large_data_points,
                'color': '#FF5733',
                'label': 'Large Dataset (Sine Wave)'
            }
        ]

        # Chart 1: Default labels (decimated)
        label1 = ttk.Label(line_label_options_frame, text="Default Labels (Decimated for large datasets):")
        label1.pack(pady=(10,2))
        line_chart_default_labels = LineChart(line_label_options_frame, width=780, height=180, use_container_width_height=False) # Fixed height for visibility
        line_chart_default_labels.pack(fill='x', expand=False)
        line_chart_default_labels.plot(datasets_large)

        # Chart 2: Labels explicitly off
        label2 = ttk.Label(line_label_options_frame, text="Labels Explicitly Off (show_point_labels=False):")
        label2.pack(pady=(10,2))
        line_chart_labels_off = LineChart(line_label_options_frame, width=780, height=180, show_point_labels=False, use_container_width_height=False) # Fixed height
        line_chart_labels_off.pack(fill='x', expand=False)
        line_chart_labels_off.plot(datasets_large)

        # Chart 3: Labels explicitly on (decimated)
        label3 = ttk.Label(line_label_options_frame, text="Labels Explicitly On (show_point_labels=True, Decimated):")
        label3.pack(pady=(10,2))
        line_chart_labels_on = LineChart(line_label_options_frame, width=780, height=180, show_point_labels=True, use_container_width_height=False) # Fixed height
        line_chart_labels_on.pack(fill='x', expand=False)
        line_chart_labels_on.plot(datasets_large)

    def refresh_bar_data(self):
        new_data = [random.randint(5, 30) for _ in range(4)]
        new_labels = ["Q1", "Q2", "Q3", "Q4"]
        self.bar_chart.plot(new_data, new_labels)

    def refresh_line_data(self):
        shapes = ['circle', 'square', 'triangle']
        colors = ['#FF0000', '#00FF00', '#0000FF']  # Red, Green, Blue        
        line_data = [
            {
                'data': [random.randint(5, 30) for _ in range(7)],
                'color': colors[0],
                'shape': shapes[0],
                'label': 'Red Circles'
            },
            {
                'data': [random.randint(5, 30) for _ in range(7)],
                'color': colors[1],
                'shape': shapes[1],
                'label': 'Green Squares'
            },
            {
                'data': [random.randint(5, 30) for _ in range(7)],
                'color': colors[2],
                'shape': shapes[2],
                'label': 'Blue Triangles'
            }
        ]
        
        self.line_chart.plot(line_data)

    def refresh_pie_data(self):
        new_data = [random.randint(10, 40) for _ in range(4)]
        new_labels = ["A", "B", "C", "D"]
        self.pie_chart.plot(new_data, new_labels)

    def refresh_scatter_data(self):
        new_data = [(random.uniform(0, 5), random.uniform(5, 20)) for _ in range(5)]
        self.scatter_chart.plot(new_data)

    def refresh_bubble_data(self):
        new_data = [(random.uniform(0, 5), random.uniform(5, 20), random.uniform(5, 30)) 
                   for _ in range(5)]
        self.bubble_chart.plot(new_data)

    def refresh_box_data(self):
        new_data = [
            sorted([random.uniform(0, 10) for _ in range(random.randint(5, 10))]),
            sorted([random.uniform(5, 15) for _ in range(random.randint(5, 10))]),
            sorted([random.uniform(10, 20) for _ in range(random.randint(5, 10))]),
            sorted([random.uniform(15, 35) for _ in range(random.randint(5, 10))])
        ]
        new_labels = ["A", "B", "C", "D"]
        self.box_chart.plot(new_data, new_labels)

    def refresh_hist_data(self):
        new_data = [random.uniform(0, 20) for _ in range(50)]
        self.hist_chart.plot(new_data, bins=10)

    def refresh_candle_data(self):
        new_data = []
        last_close = 100.0
        for i in range(5):
            open_price = last_close + random.uniform(-1, 1)
            high = open_price + random.uniform(0.5, 2.5)
            low = open_price - random.uniform(0.5, 2.5)
            close_price = open_price + random.uniform(-1.5, 1.5)
            high = max(high, open_price, close_price)
            low = min(low, open_price, close_price)
            new_data.append((i + 1, round(open_price, 2), round(high, 2), round(low, 2), round(close_price, 2)))
            last_close = close_price
        self.candle_chart.plot(new_data)

    def refresh_tableau_data(self):
        """Generate new random data for Tableau Chart"""
        names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
        cities = ["New York", "London", "Paris", "Tokyo", "Sydney", "Berlin", "Moscow"]
        new_data = [
            {
                "Name": random.choice(names),
                "Age": random.randint(20, 40),
                "Score": round(random.uniform(70, 100), 1),
                "City": random.choice(cities)
            } for _ in range(random.randint(5, 10))
        ]
        self.tableau_chart.plot(new_data)

if __name__ == "__main__":
    app = ChartApp()
    app.mainloop()
