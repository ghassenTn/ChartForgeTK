import tkinter as tk
import random
from ChartForgeTK import HeatMap

def create_correlation_data(size=10):
    """Create sample correlation matrix data."""
    variables = [f'Var{i+1}' for i in range(size)]
    data = []
    
    # Create symmetric correlation matrix
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(1.0)  # Perfect correlation on diagonal
            elif j < i:
                row.append(data[j][i])  # Mirror values for symmetry
            else:
                row.append(round(random.uniform(-1, 1), 2))  # Random correlation
        data.append(row)
    
    return data, variables

def create_heatmap_demo():
    root = tk.Tk()
    root.title("HeatMap Demo - Correlation Matrix")
    root.geometry("1000x800")
    
    # Create data
    data, labels = create_correlation_data(10)
    
    # Create heatmap
    heatmap = HeatMap(root)
    heatmap.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Plot correlation matrix
    heatmap.plot(
        data,
        row_labels=labels,
        col_labels=labels,
        title="Correlation Matrix"
    )
    
    return root

if __name__ == "__main__":
    root = create_heatmap_demo()
    root.mainloop()
