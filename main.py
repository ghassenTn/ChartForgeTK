import chartlib as cl
import math

def demo_line_chart():
    # Create smooth sine wave data
    data = [math.sin(x/10) * math.exp(-x/50) for x in range(100)]
    
    chart = cl.LineChart(data)
    chart.title = "Damped Sine Wave"
    chart.x_label = "Time"
    chart.y_label = "Amplitude"
    chart.plot()
    chart.show()

def demo_bar_chart():
    # Monthly sales data
    data = [45000, 52000, 48000, 58000, 56000, 66000, 
            71000, 63000, 60000, 66000, 71000, 75000]
    
    chart = cl.BarChart(data)
    chart.title = "Monthly Sales Performance"
    chart.x_label = "Month"
    chart.y_label = "Sales ($)"
    chart.plot()
    chart.show()

def demo_pie_chart():
    # Market share data
    values = [38, 27, 18, 12, 5]
    labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Others']
    
    chart = cl.PieChart(values, labels)
    chart.title = "Market Share Distribution"
    chart.plot()
    chart.show()

if __name__ == "__main__":
    # Run all demos
    demo_line_chart()
    demo_bar_chart()
    demo_pie_chart()