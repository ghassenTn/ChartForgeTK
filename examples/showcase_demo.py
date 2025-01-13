import tkinter as tk
from tkinter import ttk
from ChartForgeTK import LineChart, BarChart, PieChart, NetworkGraph, BubbleChart
import random
import math

class ChartShowcase(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("ChartForgeTK Showcase")
        self.geometry("1200x800")
        
        # Create main container with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each chart type
        self.create_line_chart_tab()
        self.create_bar_chart_tab()
        self.create_pie_chart_tab()
        self.create_network_graph_tab()
        self.create_bubble_chart_tab()
        
        # Add control panel
        self.create_control_panel()
    
    def create_line_chart_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Line Chart")
        
        # Create frame for chart
        frame = ttk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create line chart
        self.line_chart = LineChart(frame, width=800, height=500)
        self.line_chart.pack(fill='both', expand=True)
        
        # Generate sine wave data
        x = list(range(50))
        y = [math.sin(i/5) * math.exp(-i/50) for i in x]
        
        self.line_chart.title = "Damped Sine Wave"
        self.line_chart.x_label = "Time"
        self.line_chart.y_label = "Amplitude"
        self.line_chart.plot(y, x_labels=[str(i) for i in x])
    
    def create_bar_chart_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Bar Chart")
        
        # Create frame for chart
        frame = ttk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create bar chart
        self.bar_chart = BarChart(frame, width=800, height=500)
        self.bar_chart.pack(fill='both', expand=True)
        
        # Sample data for monthly sales
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales = [random.randint(50, 100) for _ in range(6)]
        
        self.bar_chart.title = "Monthly Sales Performance"
        self.bar_chart.x_label = "Month"
        self.bar_chart.y_label = "Sales (K$)"
        self.bar_chart.plot(sales)
    
    def create_pie_chart_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Pie Chart")
        
        # Create frame for chart
        frame = ttk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create pie chart
        self.pie_chart = PieChart(frame, width=800, height=500)
        self.pie_chart.pack(fill='both', expand=True)
        
        # Market share data
        companies = ['Product A', 'Product B', 'Product C', 'Others']
        shares = [35, 25, 20, 20]
        
        self.pie_chart.title = "Market Share Distribution"
        self.pie_chart.plot(shares, companies)
    
    def create_network_graph_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Network Graph")
        
        # Create frame for chart
        frame = ttk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create network graph
        self.network_graph = NetworkGraph(frame, width=800, height=500)
        self.network_graph.pack(fill='both', expand=True)
        
        # Create network data
        nodes = ['A', 'B', 'C', 'D', 'E', 'F']
        edges = [
            ('A', 'B'), ('B', 'C'), ('C', 'D'),
            ('D', 'E'), ('E', 'F'), ('F', 'A'),
            ('A', 'D'), ('B', 'E'), ('C', 'F')
        ]
        node_values = [1.5, 1.0, 2.0, 1.2, 1.8, 1.3]
        edge_values = [1.0, 1.5, 0.8, 1.2, 1.0, 0.9, 1.3, 1.1, 1.4]
        
        self.network_graph.plot(nodes, edges, node_values, edge_values)
    
    def create_bubble_chart_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Bubble Chart")
        
        # Create frame for chart
        frame = ttk.Frame(tab)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create bubble chart
        self.bubble_chart = BubbleChart(frame, width=800, height=500)
        self.bubble_chart.pack(fill='both', expand=True)
        
        # Generate sample data for GDP vs Life Expectancy
        countries = ['USA', 'China', 'Japan', 'Germany', 'UK', 'India', 'Brazil', 'Russia']
        gdp = [random.uniform(20000, 65000) for _ in range(len(countries))]  # GDP per capita
        life_exp = [random.uniform(65, 85) for _ in range(len(countries))]   # Life expectancy
        population = [random.uniform(50, 1400) for _ in range(len(countries))]  # Population in millions
        
        self.bubble_chart.title = "GDP vs Life Expectancy"
        self.bubble_chart.x_label = "GDP per Capita ($)"
        self.bubble_chart.y_label = "Life Expectancy (years)"
        self.bubble_chart.plot(gdp, life_exp, population, labels=countries)

    def create_control_panel(self):
        # Create control panel at the bottom
        control_frame = ttk.LabelFrame(self, text="Controls")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Add buttons for each chart type
        ttk.Button(
            control_frame,
            text="Refresh Line Chart",
            command=self.refresh_line_chart
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Refresh Bar Chart",
            command=self.refresh_bar_chart
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Refresh Pie Chart",
            command=self.refresh_pie_chart
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Refresh Network",
            command=self.refresh_network
        ).pack(side='left', padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Refresh Bubble Chart",
            command=self.refresh_bubble_chart
        ).pack(side='left', padx=5, pady=5)
    
    def refresh_line_chart(self):
        # Generate new sine wave with noise
        x = list(range(50))
        y = [math.sin(i/5) * math.exp(-i/50) + random.uniform(-0.1, 0.1) for i in x]
        self.line_chart.plot(y, x_labels=[str(i) for i in x])
    
    def refresh_bar_chart(self):
        # Generate new random sales data
        sales = [random.randint(50, 100) for _ in range(6)]
        self.bar_chart.plot(sales)
    
    def refresh_pie_chart(self):
        # Generate new random market share data
        shares = [random.randint(15, 35) for _ in range(4)]
        total = sum(shares)
        shares = [s * 100 / total for s in shares]
        companies = ['Product A', 'Product B', 'Product C', 'Others']
        self.pie_chart.plot(shares, companies)
    
    def refresh_network(self):
        # Randomize node values and edge values
        node_values = [random.uniform(1.0, 2.0) for _ in range(6)]
        edge_values = [random.uniform(0.8, 1.5) for _ in range(9)]
        nodes = ['A', 'B', 'C', 'D', 'E', 'F']
        edges = [
            ('A', 'B'), ('B', 'C'), ('C', 'D'),
            ('D', 'E'), ('E', 'F'), ('F', 'A'),
            ('A', 'D'), ('B', 'E'), ('C', 'F')
        ]
        self.network_graph.plot(nodes, edges, node_values, edge_values)

    def refresh_bubble_chart(self):
        # Generate new random data
        countries = ['USA', 'China', 'Japan', 'Germany', 'UK', 'India', 'Brazil', 'Russia']
        gdp = [random.uniform(20000, 65000) for _ in range(len(countries))]
        life_exp = [random.uniform(65, 85) for _ in range(len(countries))]
        population = [random.uniform(50, 1400) for _ in range(len(countries))]
        self.bubble_chart.plot(gdp, life_exp, population, labels=countries)

if __name__ == "__main__":
    app = ChartShowcase()
    app.mainloop()
