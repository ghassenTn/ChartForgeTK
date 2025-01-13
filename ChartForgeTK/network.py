from typing import List, Tuple, Optional
import math
import tkinter as tk
from .core import Chart, ChartStyle

class NetworkGraph(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.node_radius = 20
        self.edge_width = 2
        self.node_color = self.style.PRIMARY
        self.edge_color = self.style.TEXT_SECONDARY
        self.font = self.style.LABEL_FONT
        self.nodes = []
        self.edges = []
        self.node_values = []
        self.edge_values = []
        self.node_positions = {}
        self.interactive_elements = {}
        self._drag_data = None

    def plot(self, nodes: List[str], edges: List[Tuple[str, str]], 
            node_values: Optional[List[float]] = None,
            edge_values: Optional[List[float]] = None):
        """Plot a network graph with nodes and edges.
        
        Args:
            nodes: List of node labels
            edges: List of tuples containing (source, target) node labels
            node_values: Optional list of values for nodes (affects node size)
            edge_values: Optional list of values for edges (affects edge width)
        """
        self.nodes = nodes
        self.edges = edges
        self.node_values = node_values if node_values else [1.0] * len(nodes)
        self.edge_values = edge_values if edge_values else [1.0] * len(edges)
        
        # Calculate node positions using force-directed layout
        self._calculate_layout()
        self.redraw_chart()
        self._add_interactivity()

    def _calculate_layout(self):
        """Calculate node positions using a force-directed layout algorithm."""
        # Initialize random positions
        import random
        padding = self.padding + self.node_radius
        width = self.width - 2 * padding
        height = self.height - 2 * padding
        
        self.node_positions = {
            node: [
                padding + random.random() * width,
                padding + random.random() * height
            ] for node in self.nodes
        }
        
        # Force-directed layout iterations
        iterations = 50
        k = math.sqrt((width * height) / len(self.nodes))  # Optimal distance
        
        for _ in range(iterations):
            # Calculate repulsive forces between all nodes
            forces = {node: [0, 0] for node in self.nodes}
            
            for i, node1 in enumerate(self.nodes):
                pos1 = self.node_positions[node1]
                
                # Repulsive forces between nodes
                for node2 in self.nodes[i+1:]:
                    pos2 = self.node_positions[node2]
                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 0.01: dist = 0.01
                    
                    # Repulsive force
                    force = k*k / dist
                    fx = force * dx/dist
                    fy = force * dy/dist
                    
                    forces[node1][0] += fx
                    forces[node1][1] += fy
                    forces[node2][0] -= fx
                    forces[node2][1] -= fy
                
                # Attractive forces along edges
                for edge in self.edges:
                    if node1 in edge:
                        other = edge[1] if edge[0] == node1 else edge[0]
                        pos2 = self.node_positions[other]
                        dx = pos1[0] - pos2[0]
                        dy = pos1[1] - pos2[1]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 0.01: dist = 0.01
                        
                        # Attractive force
                        force = dist*dist / k
                        fx = force * dx/dist
                        fy = force * dy/dist
                        
                        forces[node1][0] -= fx
                        forces[node1][1] -= fy
            
            # Apply forces
            for node in self.nodes:
                fx, fy = forces[node]
                # Limit maximum force
                mag = math.sqrt(fx*fx + fy*fy)
                if mag > k:
                    fx = fx * k/mag
                    fy = fy * k/mag
                
                # Update positions
                self.node_positions[node][0] += fx
                self.node_positions[node][1] += fy
                
                # Keep within bounds
                self.node_positions[node][0] = max(padding, min(self.width - padding, self.node_positions[node][0]))
                self.node_positions[node][1] = max(padding, min(self.height - padding, self.node_positions[node][1]))

    def redraw_chart(self):
        """Redraw the network graph."""
        self.clear()
        
        # Draw edges first
        for i, (source, target) in enumerate(self.edges):
            start = self.node_positions[source]
            end = self.node_positions[target]
            
            # Scale edge width based on value
            width = self.edge_width * self.edge_values[i]
            
            self.canvas.create_line(
                start[0], start[1], end[0], end[1],
                width=width,
                fill=self.edge_color,
                tags=('edge', f'edge_{i}')
            )
        
        # Draw nodes
        for i, node in enumerate(self.nodes):
            x, y = self.node_positions[node]
            
            # Scale node size based on value
            radius = self.node_radius * self.node_values[i]
            
            # Create node circle with its label as part of the tags
            node_id = self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=self.node_color,
                outline=self.style.PRIMARY,
                width=2,
                tags=('node', f'node_{i}', node)
            )
            
            # Add label
            self.canvas.create_text(
                x, y,
                text=node,
                font=self.font,
                fill=self.style.BACKGROUND,
                tags=('label', f'label_{i}', node)
            )
            
            # Store node id for interaction
            self.interactive_elements[node] = node_id

    def _add_interactivity(self):
        """Add hover effects and dragging functionality."""
        def on_enter(event):
            item = event.widget.find_closest(event.x, event.y)
            tags = self.canvas.gettags(item)
            
            if 'node' in tags:
                # Highlight node
                self.canvas.itemconfig(item, fill=self.style.SECONDARY)
            elif 'edge' in tags:
                # Highlight edge
                self.canvas.itemconfig(item, fill=self.style.PRIMARY, width=self.edge_width * 2)

        def on_leave(event):
            if not self._drag_data:  # Only reset if not dragging
                item = event.widget.find_closest(event.x, event.y)
                tags = self.canvas.gettags(item)
                
                if 'node' in tags:
                    # Reset node color
                    self.canvas.itemconfig(item, fill=self.node_color)
                elif 'edge' in tags:
                    # Reset edge style
                    self.canvas.itemconfig(item, fill=self.edge_color, width=self.edge_width)

        def on_drag_start(event):
            item = event.widget.find_closest(event.x, event.y)
            tags = self.canvas.gettags(item)
            
            if 'node' in tags:
                # Store the node label and current position
                node_label = tags[2]  # Node label is stored as the third tag
                self._drag_data = {
                    'node': node_label,
                    'x': event.x,
                    'y': event.y,
                    'item': item
                }

        def on_drag(event):
            if self._drag_data:
                dx = event.x - self._drag_data['x']
                dy = event.y - self._drag_data['y']
                
                # Get the node being dragged
                node = self._drag_data['node']
                
                # Update node position
                self.node_positions[node][0] += dx
                self.node_positions[node][1] += dy
                
                # Redraw the entire chart
                self.redraw_chart()
                
                # Update drag reference point
                self._drag_data['x'] = event.x
                self._drag_data['y'] = event.y

        def on_drag_stop(event):
            self._drag_data = None

        self.canvas.bind('<Enter>', on_enter)
        self.canvas.bind('<Leave>', on_leave)
        self.canvas.bind('<ButtonPress-1>', on_drag_start)
        self.canvas.bind('<B1-Motion>', on_drag)
        self.canvas.bind('<ButtonRelease-1>', on_drag_stop)
