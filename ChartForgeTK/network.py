from typing import List, Tuple, Optional
import math
import tkinter as tk
from tkinter import ttk
import random
from .core import Chart

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
        self.pinned_tooltips = {}
        self._drag_data = None
        self.title = ""

    def plot(self, nodes: List[str], edges: List[Tuple[str, str]], 
             node_values: Optional[List[float]] = None,
             edge_values: Optional[List[float]] = None,
             title: str = "", animate: bool = True, show_edge_labels: bool = False):
        """Plot a network graph with nodes and edges."""
        self.nodes = nodes
        self.edges = edges
        self.node_values = node_values if node_values else [1.0] * len(nodes)
        self.edge_values = edge_values if edge_values else [1.0] * len(edges)
        self.title = title
        self.show_edge_labels = show_edge_labels
        
        # Normalize node values logarithmically for better scaling
        max_val = max(self.node_values, default=1)
        self.scaled_node_values = [math.log1p(v) / math.log1p(max_val) + 0.5 for v in self.node_values] if max_val > 1 else self.node_values
        
        self._initialize_layout()
        if animate:
            self._animate_layout(0)
        else:
            self._calculate_layout(iterations=50)
            self.redraw_chart()
            self._add_interactivity()

    def _initialize_layout(self):
        """Initialize random node positions."""
        padding = self.padding + self.node_radius
        width = self.width - 2 * padding
        height = self.height - 2 * padding
        self.node_positions = {node: [padding + random.random() * width, padding + random.random() * height] for node in self.nodes}

    def _calculate_layout(self, iterations: int = 1):
        """Perform force-directed layout for one or more iterations."""
        k = math.sqrt((self.width * self.height) / len(self.nodes))
        forces = {node: [0, 0] for node in self.nodes}
        
        for _ in range(iterations):
            for i, node1 in enumerate(self.nodes):
                pos1 = self.node_positions[node1]
                for node2 in self.nodes[i+1:]:
                    pos2 = self.node_positions[node2]
                    dx, dy = pos1[0] - pos2[0], pos1[1] - pos2[1]
                    dist = max(math.sqrt(dx*dx + dy*dy), 0.01)
                    force = k * k / dist
                    fx, fy = force * dx / dist, force * dy / dist
                    forces[node1][0] += fx
                    forces[node1][1] += fy
                    forces[node2][0] -= fx
                    forces[node2][1] -= fy

            for edge in self.edges:
                pos1, pos2 = self.node_positions[edge[0]], self.node_positions[edge[1]]
                dx, dy = pos1[0] - pos2[0], pos1[1] - pos2[1]
                dist = max(math.sqrt(dx*dx + dy*dy), 0.01)
                force = dist * dist / k
                fx, fy = force * dx / dist, force * dy / dist
                forces[edge[0]][0] -= fx
                forces[edge[0]][1] -= fy
                forces[edge[1]][0] += fx
                forces[edge[1]][1] += fy

            padding = self.padding + self.node_radius
            for node in self.nodes:
                fx, fy = forces[node]
                mag = math.sqrt(fx*fx + fy*fy)
                if mag > k:
                    fx, fy = fx * k / mag, fy * k / mag
                self.node_positions[node][0] = max(padding, min(self.width - padding, self.node_positions[node][0] + fx))
                self.node_positions[node][1] = max(padding, min(self.height - padding, self.node_positions[node][1] + fy))

    def _animate_layout(self, step: int):
        """Animate the force-directed layout."""
        max_steps = 50
        if step >= max_steps:
            self.redraw_chart()
            self._add_interactivity()
            return
        
        self._calculate_layout(iterations=1)
        self.redraw_chart()
        self.after(20, lambda: self._animate_layout(step + 1))

    def redraw_chart(self):
        """Redraw the network graph efficiently."""
        self.canvas.delete("all")
        self._draw_title()
        
        for i, (source, target) in enumerate(self.edges):
            start, end = self.node_positions[source], self.node_positions[target]
            width = self.edge_width * self.edge_values[i]
            edge_id = self.canvas.create_line(start[0], start[1], end[0], end[1],
                                             width=width, fill=self.edge_color,
                                             tags=('edge', f'edge_{i}'))
            self.interactive_elements[f"edge_{i}"] = edge_id
            
            if self.show_edge_labels:
                mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
                self.canvas.create_text(mid_x, mid_y, text=f"{self.edge_values[i]:.2f}",
                                       font=self.font, fill=self.style.TEXT, tags=('edge_label', f'elabel_{i}'))

        for i, node in enumerate(self.nodes):
            x, y = self.node_positions[node]
            radius = self.node_radius * self.scaled_node_values[i]
            color = self.style.get_gradient_color(i, len(self.nodes))
            
            for r in range(int(radius), 0, -1):
                alpha = r / radius
                gradient_color = self.style.create_rgba_from_hex(color, alpha * 0.8)
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=gradient_color, outline="", tags=('node', f'node_{i}'))
            
            node_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                             fill="", outline=self.style.PRIMARY, width=2,
                                             tags=('node', f'node_{i}', node))
            self.canvas.create_text(x, y, text=node, font=self.font, fill=self.style.BACKGROUND,
                                   tags=('label', f'label_{i}', node))
            self.interactive_elements[node] = node_id

    def _draw_title(self):
        """Draw the chart title."""
        if self.title:
            self.canvas.create_text(self.width / 2, self.padding / 2, text=self.title,
                                   font=self.style.TITLE_FONT, fill=self.style.TEXT, anchor='center')

    def _add_interactivity(self):
        """Add hover effects, tooltips, and dragging."""
        tooltip = tk.Toplevel(self.canvas)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)
        tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)

        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND)

        current_highlight = None

        def on_enter(event):
            nonlocal current_highlight
            item = self.canvas.find_closest(event.x, event.y)[0]
            tags = self.canvas.gettags(item)
            if not tags:  # No tags, ignore
                return

            if current_highlight:
                for h in current_highlight:
                    self.canvas.delete(h)
                current_highlight = None

            if 'node' in tags and len(tags) >= 3:  # Ensure node tag has label
                node = tags[2]
                idx = self.nodes.index(node)
                x, y = self.node_positions[node]
                radius = self.node_radius * self.scaled_node_values[idx]
                highlight_items = []
                for i in range(3):
                    offset = i * 2
                    alpha = 0.3 - i * 0.1
                    glow_color = self.style.create_rgba_from_hex(self.style.SECONDARY, alpha)
                    glow = self.canvas.create_oval(x - radius - offset, y - radius - offset,
                                                  x + radius + offset, y + radius + offset,
                                                  outline=glow_color, width=2, tags='highlight')
                    highlight_items.append(glow)
                current_highlight = highlight_items
                tooltip_text = f"Node: {node}\nValue: {self.node_values[idx]:.2f}"
                label.config(text=tooltip_text)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 30}")
                tooltip.deiconify()
                tooltip.lift()

            elif 'edge' in tags and len(tags) >= 2:  # Ensure edge tag has index
                edge_idx = int(tags[1].split('_')[1])
                source, target = self.edges[edge_idx]
                self.canvas.itemconfig(item, fill=self.style.PRIMARY, width=self.edge_width * 2)
                tooltip_text = f"Edge: {source} -> {target}\nValue: {self.edge_values[edge_idx]:.2f}"
                label.config(text=tooltip_text)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 30}")
                tooltip.deiconify()
                tooltip.lift()

        def on_leave(event):
            nonlocal current_highlight
            if not self._drag_data:
                item = self.canvas.find_closest(event.x, event.y)[0]
                tags = self.canvas.gettags(item)
                if current_highlight:
                    for h in current_highlight:
                        self.canvas.delete(h)
                    current_highlight = None
                if 'edge' in tags:
                    self.canvas.itemconfig(item, fill=self.edge_color, width=self.edge_width)
                if item not in self.pinned_tooltips:
                    tooltip.withdraw()

        def on_drag_start(event):
            item = self.canvas.find_closest(event.x, event.y)[0]
            tags = self.canvas.gettags(item)
            if 'node' in tags and len(tags) >= 3:
                self._drag_data = {'node': tags[2], 'x': event.x, 'y': event.y, 'item': item}

        def on_drag(event):
            if self._drag_data:
                dx, dy = event.x - self._drag_data['x'], event.y - self._drag_data['y']
                node = self._drag_data['node']
                self.node_positions[node][0] += dx
                self.node_positions[node][1] += dy
                padding = self.padding + self.node_radius
                self.node_positions[node][0] = max(padding, min(self.width - padding, self.node_positions[node][0]))
                self.node_positions[node][1] = max(padding, min(self.height - padding, self.node_positions[node][1]))
                self._update_node_and_edges(node)
                self._drag_data['x'], self._drag_data['y'] = event.x, event.y

        def on_drag_stop(event):
            self._drag_data = None

        def on_click(event):
            item = self.canvas.find_closest(event.x, event.y)[0]
            tags = self.canvas.gettags(item)
            if ('node' in tags and len(tags) >= 3) or ('edge' in tags and len(tags) >= 2):
                if item in self.pinned_tooltips:
                    self.pinned_tooltips.pop(item).withdraw()
                else:
                    pinned = tk.Toplevel(self.canvas)
                    pinned.overrideredirect(True)
                    pinned.attributes('-topmost', True)
                    frame = ttk.Frame(pinned, style='Tooltip.TFrame')
                    frame.pack(fill='both', expand=True)
                    if 'node' in tags:
                        node = tags[2]
                        idx = self.nodes.index(node)
                        text = f"Node: {node}\nValue: {self.node_values[idx]:.2f}"
                    else:
                        edge_idx = int(tags[1].split('_')[1])
                        source, target = self.edges[edge_idx]
                        text = f"Edge: {source} -> {target}\nValue: {self.edge_values[edge_idx]:.2f}"
                    lbl = ttk.Label(frame, text=text, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
                    lbl.pack(padx=8, pady=4)
                    pinned.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 30}")
                    self.pinned_tooltips[item] = pinned

        self.canvas.bind('<Motion>', on_enter)
        self.canvas.bind('<Leave>', on_leave)
        self.canvas.bind('<ButtonPress-1>', on_drag_start)
        self.canvas.bind('<B1-Motion>', on_drag)
        self.canvas.bind('<ButtonRelease-1>', on_drag_stop)
        self.canvas.bind('<Button-1>', on_click)

    def _update_node_and_edges(self, node: str):
        """Update the position of a dragged node and its connected edges."""
        x, y = self.node_positions[node]
        radius = self.node_radius * self.scaled_node_values[self.nodes.index(node)]
        self.canvas.coords(f'node_{self.nodes.index(node)}', x - radius, y - radius, x + radius, y + radius)
        self.canvas.coords(f'label_{self.nodes.index(node)}', x, y)
        
        for i, (source, target) in enumerate(self.edges):
            if source == node or target == node:
                start = self.node_positions[source]
                end = self.node_positions[target]
                self.canvas.coords(f'edge_{i}', start[0], start[1], end[0], end[1])
                if self.show_edge_labels:
                    self.canvas.coords(f'elabel_{i}', (start[0] + end[0]) / 2, (start[1] + end[1]) / 2)