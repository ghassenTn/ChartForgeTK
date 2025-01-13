from ChartForgeTK import NetworkGraph
import tkinter as tk

root = tk.Tk()
chart = NetworkGraph(root)
chart.pack(fill="both", expand=True)

nodes = ["A", "B", "C", "D", "E"]
edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")]
node_values = [1.0, 2.0, 1.5, 2.5, 1.8]
edge_values = [0.5, 1.0, 0.8, 1.2]

chart.plot(nodes, edges, node_values, edge_values)
root.mainloop()