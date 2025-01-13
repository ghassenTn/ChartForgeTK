import tkinter as tk
from ChartForgeTK import NetworkGraph

def create_network_demo():
    root = tk.Tk()
    root.title("Network Graph Demo")
    root.geometry("800x600")
    
    # Create a network graph
    graph = NetworkGraph(root)
    graph.pack(fill=tk.BOTH, expand=True)
    
    # Define nodes and edges
    nodes = ["A", "B", "C", "D", "E", "F"]
    edges = [
        ("A", "B"), ("B", "C"), ("C", "D"),
        ("D", "E"), ("E", "F"), ("F", "A"),
        ("A", "D"), ("B", "E"), ("C", "F")
    ]
    
    # Node values (affects node size)
    node_values = [1.5, 1.0, 2.0, 1.2, 1.8, 1.3]
    
    # Edge values (affects edge width)
    edge_values = [1.0, 1.5, 0.8, 1.2, 1.0, 0.9, 1.3, 1.1, 1.4]
    
    # Plot the network
    graph.plot(nodes, edges, node_values, edge_values)
    
    return root

if __name__ == "__main__":
    root = create_network_demo()
    root.mainloop()
