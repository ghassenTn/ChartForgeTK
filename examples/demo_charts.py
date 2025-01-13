import tkinter as tk
from ChartForgeTK import LineChart, BarChart, PieChart
import random

def create_demo_window():
    root = tk.Tk()
    root.title("ChartForgeTK Demo")
    root.geometry("1200x800")
    
    # Create frames for each chart
    line_frame = tk.Frame(root)
    line_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    bar_frame = tk.Frame(root)
    bar_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    pie_frame = tk.Frame(root)
    pie_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Line Chart - Monthly Sales Data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales = [random.randint(100, 1000) for _ in range(6)]
    
    line_chart = LineChart(line_frame, width=350, height=300)
    line_chart.pack(fill=tk.BOTH, expand=True)
    line_chart.title = "Monthly Sales 2024"
    line_chart.x_label = "Month"
    line_chart.y_label = "Sales ($)"
    line_chart.data = list(zip(months, sales))
    line_chart.line_color = "#2ecc71"  # Green color
    line_chart.point_radius = 5
    line_chart.animate = True
    line_chart.plot(sales, x_labels=months)  # Line chart takes optional x_labels
    
    # Bar Chart - Product Categories
    categories = ['Electronics', 'Clothing', 'Food', 'Books']
    revenues = [random.randint(500, 2000) for _ in range(4)]
    
    bar_chart = BarChart(bar_frame, width=350, height=300)
    bar_chart.pack(fill=tk.BOTH, expand=True)
    bar_chart.title = "Revenue by Category"
    bar_chart.x_label = "Category"
    bar_chart.y_label = "Revenue ($)"
    bar_chart.data = list(zip(categories, revenues))
    bar_chart.bar_colors = ["#3498db", "#e74c3c", "#f1c40f", "#9b59b6"]  # Different colors for each bar
    bar_chart.animate = True
    bar_chart.plot(revenues)  # Bar chart just takes values
    
    # Pie Chart - Market Share
    companies = ['Company A', 'Company B', 'Company C', 'Others']
    market_share = [random.randint(10, 30) for _ in range(4)]
    # Normalize to 100%
    total = sum(market_share)
    market_share = [x/total * 100 for x in market_share]
    
    pie_chart = PieChart(pie_frame, width=350, height=300)
    pie_chart.pack(fill=tk.BOTH, expand=True)
    pie_chart.title = "Market Share Distribution"
    pie_chart.data = list(zip(companies, market_share))
    pie_chart.colors = ["#1abc9c", "#3498db", "#9b59b6", "#95a5a6"]  # Different colors for each slice
    pie_chart.show_percentage = True
    pie_chart.animate = True
    pie_chart.plot(market_share, companies)  # Pie chart takes values and labels

    return root

if __name__ == "__main__":
    root = create_demo_window()
    root.mainloop()
