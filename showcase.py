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

"""
ChartForgeTK Dashboard Showcase

This showcase demonstrates all chart types and the new stability features
introduced in v2.0, including input validation, resource management,
and edge case handling.

Also demonstrates pandas DataFrame support for seamless data visualization
workflows with pandas data structures.
"""

import tkinter as tk
from tkinter import ttk, messagebox
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
    GanttChart,
    # New stability modules
    DataValidator,
    ResourceManager,
    CoordinateTransformer,
)
import random
import math
from typing import List, Tuple
from datetime import datetime

# Try to import pandas for DataFrame examples
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
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

        # Stability Demo Tab - New in v2.0
        stability_frame = ttk.Frame(notebook)
        notebook.add(stability_frame, text="Stability Demo")
        self.setup_stability_demo(stability_frame)

        # Pandas DataFrame Demo Tab
        if PANDAS_AVAILABLE:
            pandas_frame = ttk.Frame(notebook)
            notebook.add(pandas_frame, text="Pandas DataFrame")
            self.setup_pandas_demo(pandas_frame)

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

    def setup_stability_demo(self, parent):
        """Set up the stability demonstration tab."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title = ttk.Label(scrollable_frame, text="ChartForgeTK v2.0 Stability Features",
                         font=('Helvetica', 14, 'bold'))
        title.pack(pady=10)

        # Section 1: Input Validation Demo
        validation_frame = ttk.LabelFrame(scrollable_frame, text="Input Validation", padding=10)
        validation_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(validation_frame, text="Test input validation with various edge cases:").pack(anchor='w')

        btn_frame1 = ttk.Frame(validation_frame)
        btn_frame1.pack(fill='x', pady=5)

        ttk.Button(btn_frame1, text="Valid Data",
                  command=self.demo_valid_data).pack(side='left', padx=2)
        ttk.Button(btn_frame1, text="Empty Data (Error)",
                  command=self.demo_empty_data).pack(side='left', padx=2)
        ttk.Button(btn_frame1, text="Invalid Type (Error)",
                  command=self.demo_invalid_type).pack(side='left', padx=2)
        ttk.Button(btn_frame1, text="Mismatched Labels (Error)",
                  command=self.demo_mismatched_labels).pack(side='left', padx=2)

        # Section 2: Edge Case Handling Demo
        edge_frame = ttk.LabelFrame(scrollable_frame, text="Edge Case Handling", padding=10)
        edge_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(edge_frame, text="Charts handle edge cases gracefully:").pack(anchor='w')

        btn_frame2 = ttk.Frame(edge_frame)
        btn_frame2.pack(fill='x', pady=5)

        ttk.Button(btn_frame2, text="Single Data Point",
                  command=self.demo_single_point).pack(side='left', padx=2)
        ttk.Button(btn_frame2, text="Identical Values",
                  command=self.demo_identical_values).pack(side='left', padx=2)
        ttk.Button(btn_frame2, text="Zero Values",
                  command=self.demo_zero_values).pack(side='left', padx=2)
        ttk.Button(btn_frame2, text="Large Dataset",
                  command=self.demo_large_dataset).pack(side='left', padx=2)

        # Demo chart for stability tests
        self.stability_chart_frame = ttk.Frame(scrollable_frame)
        self.stability_chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.stability_chart = BarChart(self.stability_chart_frame, width=700, height=300)
        self.stability_chart.pack(fill='both', expand=True)
        self.stability_chart.plot([10, 20, 30, 40], ["A", "B", "C", "D"])

        # Status label
        self.stability_status = ttk.Label(scrollable_frame, text="Ready for demos",
                                         font=('Helvetica', 10))
        self.stability_status.pack(pady=5)

        # Section 3: Utility Classes Demo
        utility_frame = ttk.LabelFrame(scrollable_frame, text="Utility Classes", padding=10)
        utility_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(utility_frame, text="DataValidator, ResourceManager, CoordinateTransformer").pack(anchor='w')

        btn_frame3 = ttk.Frame(utility_frame)
        btn_frame3.pack(fill='x', pady=5)

        ttk.Button(btn_frame3, text="Validate Color",
                  command=self.demo_color_validation).pack(side='left', padx=2)
        ttk.Button(btn_frame3, text="Validate Dimensions",
                  command=self.demo_dimension_validation).pack(side='left', padx=2)
        ttk.Button(btn_frame3, text="Coordinate Transform",
                  command=self.demo_coordinate_transform).pack(side='left', padx=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_pandas_demo(self, parent):
        """Set up the pandas DataFrame demonstration tab."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title = ttk.Label(scrollable_frame, text="Pandas DataFrame Support",
                         font=('Helvetica', 14, 'bold'))
        title.pack(pady=10)

        description = ttk.Label(scrollable_frame, 
            text="ChartForgeTK accepts pandas DataFrames and Series directly.\n"
                 "No manual list conversion needed!",
            justify='center')
        description.pack(pady=5)

        # Section 1: BarChart with DataFrame
        bar_frame = ttk.LabelFrame(scrollable_frame, text="BarChart with DataFrame", padding=10)
        bar_frame.pack(fill='x', padx=10, pady=5)

        # Create sample DataFrame for BarChart
        bar_df = pd.DataFrame({
            'category': ['Q1', 'Q2', 'Q3', 'Q4'],
            'sales': [150, 200, 175, 225]
        })

        ttk.Label(bar_frame, text="DataFrame:\n" + bar_df.to_string(index=False),
                 font=('Courier', 9)).pack(anchor='w', pady=5)

        bar_chart = BarChart(bar_frame, width=700, height=200)
        bar_chart.pack(fill='x', pady=5)
        # Plot using DataFrame with column specification
        bar_chart.plot(bar_df, value_column='sales', label_column='category')
        self.pandas_bar_chart = bar_chart
        self.pandas_bar_df = bar_df

        ttk.Button(bar_frame, text="Refresh with Random Data",
                  command=self.refresh_pandas_bar).pack(pady=5)

        # Section 2: PieChart with Series
        pie_frame = ttk.LabelFrame(scrollable_frame, text="PieChart with Series", padding=10)
        pie_frame.pack(fill='x', padx=10, pady=5)

        # Create sample Series for PieChart
        pie_series = pd.Series([30, 25, 20, 15, 10], 
                               index=['Product A', 'Product B', 'Product C', 'Product D', 'Product E'])

        ttk.Label(pie_frame, text="Series:\n" + pie_series.to_string(),
                 font=('Courier', 9)).pack(anchor='w', pady=5)

        pie_chart = PieChart(pie_frame, width=700, height=250)
        pie_chart.pack(fill='x', pady=5)
        # Plot using Series directly (index becomes labels)
        pie_chart.plot(pie_series)
        self.pandas_pie_chart = pie_chart

        ttk.Button(pie_frame, text="Refresh with Random Data",
                  command=self.refresh_pandas_pie).pack(pady=5)

        # Section 3: LineChart with DataFrame (Multi-series)
        line_frame = ttk.LabelFrame(scrollable_frame, text="LineChart with DataFrame (Multi-series)", padding=10)
        line_frame.pack(fill='x', padx=10, pady=5)

        # Create sample DataFrame for LineChart
        line_df = pd.DataFrame({
            'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'revenue': [100, 120, 115, 130, 145, 160],
            'expenses': [80, 85, 90, 95, 100, 105],
            'profit': [20, 35, 25, 35, 45, 55]
        })

        ttk.Label(line_frame, text="DataFrame:\n" + line_df.to_string(index=False),
                 font=('Courier', 9)).pack(anchor='w', pady=5)

        line_chart = LineChart(line_frame, width=700, height=200)
        line_chart.pack(fill='x', pady=5)
        # Plot multiple columns as separate series
        line_chart.plot(line_df, y_columns=['revenue', 'expenses', 'profit'], label_column='month')
        self.pandas_line_chart = line_chart
        self.pandas_line_df = line_df

        ttk.Button(line_frame, text="Refresh with Random Data",
                  command=self.refresh_pandas_line).pack(pady=5)

        # Section 4: ScatterPlot with DataFrame
        scatter_frame = ttk.LabelFrame(scrollable_frame, text="ScatterPlot with DataFrame", padding=10)
        scatter_frame.pack(fill='x', padx=10, pady=5)

        # Create sample DataFrame for ScatterPlot
        scatter_df = pd.DataFrame({
            'height': [160, 165, 170, 175, 180, 185, 190],
            'weight': [55, 60, 65, 70, 75, 80, 85]
        })

        ttk.Label(scatter_frame, text="DataFrame:\n" + scatter_df.to_string(index=False),
                 font=('Courier', 9)).pack(anchor='w', pady=5)

        scatter_chart = ScatterPlot(scatter_frame, width=700, height=200)
        scatter_chart.pack(fill='x', pady=5)
        # Plot using x and y column specification
        scatter_chart.plot(scatter_df, x_column='height', y_column='weight')
        self.pandas_scatter_chart = scatter_chart

        ttk.Button(scatter_frame, text="Refresh with Random Data",
                  command=self.refresh_pandas_scatter).pack(pady=5)

        # Section 5: Histogram with Series
        hist_frame = ttk.LabelFrame(scrollable_frame, text="Histogram with Series", padding=10)
        hist_frame.pack(fill='x', padx=10, pady=5)

        # Create sample Series for Histogram
        hist_series = pd.Series([random.gauss(50, 15) for _ in range(100)])

        ttk.Label(hist_frame, text=f"Series: {len(hist_series)} random values (normal distribution)",
                 font=('Courier', 9)).pack(anchor='w', pady=5)

        hist_chart = Histogram(hist_frame, width=700, height=200)
        hist_chart.pack(fill='x', pady=5)
        # Plot using Series directly
        hist_chart.plot(hist_series, bins=10)
        self.pandas_hist_chart = hist_chart

        ttk.Button(hist_frame, text="Refresh with Random Data",
                  command=self.refresh_pandas_hist).pack(pady=5)

        # Status label
        self.pandas_status = ttk.Label(scrollable_frame, 
            text="All charts above are plotted directly from pandas DataFrames/Series",
            font=('Helvetica', 10))
        self.pandas_status.pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_pandas_bar(self):
        """Refresh BarChart with new random DataFrame data."""
        df = pd.DataFrame({
            'category': ['Q1', 'Q2', 'Q3', 'Q4'],
            'sales': [random.randint(100, 300) for _ in range(4)]
        })
        self.pandas_bar_chart.plot(df, value_column='sales', label_column='category')
        self.pandas_status.config(text="✓ BarChart refreshed with new DataFrame")

    def refresh_pandas_pie(self):
        """Refresh PieChart with new random Series data."""
        products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
        series = pd.Series([random.randint(10, 50) for _ in range(5)], index=products)
        self.pandas_pie_chart.plot(series)
        self.pandas_status.config(text="✓ PieChart refreshed with new Series")

    def refresh_pandas_line(self):
        """Refresh LineChart with new random DataFrame data."""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        base_revenue = random.randint(80, 120)
        df = pd.DataFrame({
            'month': months,
            'revenue': [base_revenue + i * random.randint(5, 15) for i in range(6)],
            'expenses': [base_revenue - 20 + i * random.randint(3, 8) for i in range(6)],
            'profit': [random.randint(15, 60) for _ in range(6)]
        })
        self.pandas_line_chart.plot(df, y_columns=['revenue', 'expenses', 'profit'], label_column='month')
        self.pandas_status.config(text="✓ LineChart refreshed with new DataFrame")

    def refresh_pandas_scatter(self):
        """Refresh ScatterPlot with new random DataFrame data."""
        df = pd.DataFrame({
            'height': [random.randint(155, 195) for _ in range(10)],
            'weight': [random.randint(50, 90) for _ in range(10)]
        })
        self.pandas_scatter_chart.plot(df, x_column='height', y_column='weight')
        self.pandas_status.config(text="✓ ScatterPlot refreshed with new DataFrame")

    def refresh_pandas_hist(self):
        """Refresh Histogram with new random Series data."""
        series = pd.Series([random.gauss(50, 15) for _ in range(100)])
        self.pandas_hist_chart.plot(series, bins=10)
        self.pandas_status.config(text="✓ Histogram refreshed with new Series")

    def demo_valid_data(self):
        """Demonstrate valid data handling."""
        try:
            data = DataValidator.validate_numeric_list([15, 25, 35, 45, 55])
            labels = DataValidator.validate_labels(["Q1", "Q2", "Q3", "Q4", "Q5"], len(data))
            self.stability_chart.plot(data, labels)
            self.stability_status.config(text="✓ Valid data plotted successfully")
        except Exception as e:
            self.stability_status.config(text=f"Error: {e}")

    def demo_empty_data(self):
        """Demonstrate empty data validation."""
        try:
            DataValidator.validate_numeric_list([])
            self.stability_status.config(text="Unexpected: No error raised")
        except ValueError as e:
            messagebox.showinfo("Input Validation", f"Empty data rejected:\n\n{e}")
            self.stability_status.config(text="✓ Empty data properly rejected")

    def demo_invalid_type(self):
        """Demonstrate invalid type validation."""
        try:
            DataValidator.validate_numeric_list(["a", "b", "c"])
            self.stability_status.config(text="Unexpected: No error raised")
        except TypeError as e:
            messagebox.showinfo("Input Validation", f"Invalid type rejected:\n\n{e}")
            self.stability_status.config(text="✓ Invalid type properly rejected")

    def demo_mismatched_labels(self):
        """Demonstrate mismatched labels validation."""
        try:
            DataValidator.validate_labels(["A", "B"], 5)  # 2 labels for 5 data points
            self.stability_status.config(text="Unexpected: No error raised")
        except ValueError as e:
            messagebox.showinfo("Input Validation", f"Mismatched labels rejected:\n\n{e}")
            self.stability_status.config(text="✓ Mismatched labels properly rejected")

    def demo_single_point(self):
        """Demonstrate single data point handling."""
        self.stability_chart.plot([42], ["Single"])
        self.stability_status.config(text="✓ Single data point rendered successfully")

    def demo_identical_values(self):
        """Demonstrate identical values handling."""
        self.stability_chart.plot([50, 50, 50, 50], ["A", "B", "C", "D"])
        self.stability_status.config(text="✓ Identical values rendered with proper axis range")

    def demo_zero_values(self):
        """Demonstrate zero values handling."""
        self.stability_chart.plot([0, 10, 0, 20, 0], ["A", "B", "C", "D", "E"])
        self.stability_status.config(text="✓ Zero values rendered as zero-height bars")

    def demo_large_dataset(self):
        """Demonstrate large dataset handling."""
        data = [random.randint(10, 100) for _ in range(50)]
        labels = [f"Item {i+1}" for i in range(50)]
        self.stability_chart.plot(data, labels)
        self.stability_status.config(text="✓ Large dataset (50 items) rendered successfully")

    def demo_color_validation(self):
        """Demonstrate color validation."""
        test_colors = ["#FF5733", "#abc", "red", "invalid_color"]
        results = []
        for color in test_colors:
            try:
                validated = DataValidator.validate_color(color)
                results.append(f"'{color}' → '{validated}' ✓")
            except ValueError as e:
                results.append(f"'{color}' → Error ✗")

        messagebox.showinfo("Color Validation", "\n".join(results))
        self.stability_status.config(text="✓ Color validation demo complete")

    def demo_dimension_validation(self):
        """Demonstrate dimension validation."""
        test_cases = [(800, 600), (50, 50), (100, 100)]
        results = []
        for w, h in test_cases:
            try:
                validated = DataValidator.validate_dimensions(w, h)
                results.append(f"({w}, {h}) → {validated} ✓")
            except ValueError as e:
                results.append(f"({w}, {h}) → Rejected (min 100x100)")

        messagebox.showinfo("Dimension Validation", "\n".join(results))
        self.stability_status.config(text="✓ Dimension validation demo complete")

    def demo_coordinate_transform(self):
        """Demonstrate coordinate transformation."""
        transformer = CoordinateTransformer(width=400, height=300, padding=40)
        x_min, x_max, y_min, y_max = transformer.calculate_ranges(0, 100, 0, 50)

        # Transform some points
        points = [(0, 0), (50, 25), (100, 50)]
        results = [f"Data Range: X[{x_min:.1f}, {x_max:.1f}], Y[{y_min:.1f}, {y_max:.1f}]\n"]

        for x, y in points:
            px = transformer.data_to_pixel_x(x)
            py = transformer.data_to_pixel_y(y)
            results.append(f"Data ({x}, {y}) → Pixel ({px:.1f}, {py:.1f})")

        messagebox.showinfo("Coordinate Transform", "\n".join(results))
        self.stability_status.config(text="✓ Coordinate transform demo complete")

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
