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


from typing import List, Tuple, Optional
import math
import tkinter as tk
from tkinter import ttk
import random
import logging
from .core import Chart
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class NetworkGraph(Chart):
    """
    Network graph implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
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
        self._tooltip = None  # Tooltip window reference

    def plot(self, nodes: List[str], edges: List[Tuple[str, str]], 
             node_values: Optional[List[float]] = None,
             edge_values: Optional[List[float]] = None,
             title: str = "", animate: bool = True, show_edge_labels: bool = False):
        """Plot a network graph with nodes and edges.
        
        Args:
            nodes: List of node names
            edges: List of (source, target) tuples
            node_values: Optional list of values for each node
            edge_values: Optional list of values for each edge
            title: Optional chart title
            animate: Whether to animate the layout
            show_edge_labels: Whether to show edge labels
            
        Raises:
            TypeError: If nodes or edges are None or have invalid types
            ValueError: If nodes is empty or edges reference non-existent nodes
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.6, 9.1, 9.2, 9.3, 9.4
        """
        # Validate nodes is not None (Requirements: 1.1)
        if nodes is None:
            raise TypeError(
                "[ChartForgeTK] Error: nodes cannot be None. "
                "Please provide a list of node names."
            )
        
        # Validate nodes is a list (Requirements: 1.3)
        if not isinstance(nodes, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: nodes must be a list, "
                f"got {type(nodes).__name__}."
            )
        
        # Validate nodes is not empty (Requirements: 1.2)
        if not nodes:
            raise ValueError(
                "[ChartForgeTK] Error: nodes cannot be empty. "
                "Please provide at least one node."
            )
        
        # Validate edges is not None
        if edges is None:
            raise TypeError(
                "[ChartForgeTK] Error: edges cannot be None. "
                "Please provide a list of (source, target) tuples."
            )
        
        # Validate edges is a list
        if not isinstance(edges, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: edges must be a list, "
                f"got {type(edges).__name__}."
            )
        
        # Validate each edge
        node_set = set(str(n) for n in nodes)
        validated_edges = []
        for i, edge in enumerate(edges):
            if not isinstance(edge, (tuple, list)) or len(edge) != 2:
                raise ValueError(
                    f"[ChartForgeTK] Error: edges[{i}] must be a (source, target) tuple."
                )
            source, target = str(edge[0]), str(edge[1])
            if source not in node_set:
                raise ValueError(
                    f"[ChartForgeTK] Error: edges[{i}] source '{source}' is not in nodes list."
                )
            if target not in node_set:
                raise ValueError(
                    f"[ChartForgeTK] Error: edges[{i}] target '{target}' is not in nodes list."
                )
            validated_edges.append((source, target))
        
        # Validate node_values if provided
        if node_values is not None:
            if not isinstance(node_values, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: node_values must be a list, "
                    f"got {type(node_values).__name__}."
                )
            if len(node_values) != len(nodes):
                raise ValueError(
                    f"[ChartForgeTK] Error: node_values length ({len(node_values)}) "
                    f"must match nodes length ({len(nodes)})."
                )
            for i, val in enumerate(node_values):
                if not isinstance(val, (int, float)):
                    raise TypeError(
                        f"[ChartForgeTK] Error: node_values[{i}] must be a number."
                    )
        
        # Validate edge_values if provided
        if edge_values is not None:
            if not isinstance(edge_values, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: edge_values must be a list, "
                    f"got {type(edge_values).__name__}."
                )
            if len(edge_values) != len(edges):
                raise ValueError(
                    f"[ChartForgeTK] Error: edge_values length ({len(edge_values)}) "
                    f"must match edges length ({len(edges)})."
                )
            for i, val in enumerate(edge_values):
                if not isinstance(val, (int, float)):
                    raise TypeError(
                        f"[ChartForgeTK] Error: edge_values[{i}] must be a number."
                    )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Clean up pinned tooltips
        for tooltip in self.pinned_tooltips.values():
            try:
                tooltip.destroy()
            except tk.TclError:
                pass
        self.pinned_tooltips.clear()
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        self.nodes = [str(n) for n in nodes]
        self.edges = validated_edges
        self.node_values = [float(v) for v in node_values] if node_values else [1.0] * len(self.nodes)
        self.edge_values = [float(v) for v in edge_values] if edge_values else [1.0] * len(self.edges)
        self.title = str(title)
        self.show_edge_labels = show_edge_labels
        
        # Handle edge case: single node (Requirements: 2.1)
        if len(self.nodes) == 1:
            logger.debug("Single node detected in NetworkGraph")
        
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
        """Animate the force-directed layout.
        
        Requirements: 3.2, 3.6, 6.3
        """
        max_steps = 50
        if step >= max_steps:
            self.redraw_chart()
            self._add_interactivity()
            return
        
        # Check if widget still exists before updating (Requirements: 6.3)
        try:
            if not self.canvas.winfo_exists():
                return
        except tk.TclError:
            return
        
        self._calculate_layout(iterations=1)
        self.redraw_chart()
        
        # Register animation callback with resource manager (Requirements: 3.2, 3.6)
        after_id = self.after(20, lambda: self._animate_layout(step + 1))
        self.resource_manager.register_animation(after_id)

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
        """Add hover effects, tooltips, and dragging.
        
        Requirements: 3.1, 3.5, 7.1, 7.2, 7.6
        """
        # Create tooltip window
        tooltip = tk.Toplevel(self.canvas)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        try:
            tooltip.attributes('-topmost', True)
        except tk.TclError:
            pass  # Some platforms may not support this
        
        # Register tooltip with resource manager (Requirements: 3.1, 7.6)
        self.resource_manager.register_tooltip(tooltip)
        self._tooltip = tooltip
        
        tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)

        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND)

        current_highlight = None

        def on_enter(event):
            """Handle mouse enter events (Requirements: 7.2)"""
            nonlocal current_highlight
            try:
                items = self.canvas.find_closest(event.x, event.y)
                if not items:
                    return
                item = items[0]
                tags = self.canvas.gettags(item)
                if not tags:  # No tags, ignore
                    return

                if current_highlight:
                    for h in current_highlight:
                        try:
                            self.canvas.delete(h)
                        except tk.TclError:
                            pass
                    current_highlight = None

                if 'node' in tags and len(tags) >= 3:  # Ensure node tag has label
                    node = tags[2]
                    if node not in self.nodes:
                        return
                    idx = self.nodes.index(node)
                    if node not in self.node_positions:
                        return
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
                    if edge_idx < 0 or edge_idx >= len(self.edges):
                        return
                    source, target = self.edges[edge_idx]
                    self.canvas.itemconfig(item, fill=self.style.PRIMARY, width=self.edge_width * 2)
                    tooltip_text = f"Edge: {source} -> {target}\nValue: {self.edge_values[edge_idx]:.2f}"
                    label.config(text=tooltip_text)
                    tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 30}")
                    tooltip.deiconify()
                    tooltip.lift()
            except tk.TclError as e:
                logger.debug(f"TclError in network hover: {e}")
            except Exception as e:
                logger.warning(f"Error in network hover: {e}")

        def on_leave(event):
            """Handle mouse leave events"""
            nonlocal current_highlight
            try:
                if not self._drag_data:
                    items = self.canvas.find_closest(event.x, event.y)
                    if items:
                        item = items[0]
                        tags = self.canvas.gettags(item)
                        if current_highlight:
                            for h in current_highlight:
                                try:
                                    self.canvas.delete(h)
                                except tk.TclError:
                                    pass
                            current_highlight = None
                        if 'edge' in tags:
                            try:
                                self.canvas.itemconfig(item, fill=self.edge_color, width=self.edge_width)
                            except tk.TclError:
                                pass
                        if item not in self.pinned_tooltips:
                            try:
                                tooltip.withdraw()
                            except tk.TclError:
                                pass
            except tk.TclError:
                pass
            except Exception:
                pass

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

        # Bind events and register with resource manager (Requirements: 3.5)
        motion_id = self.canvas.bind('<Motion>', on_enter)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        press_id = self.canvas.bind('<ButtonPress-1>', on_drag_start)
        drag_id = self.canvas.bind('<B1-Motion>', on_drag)
        release_id = self.canvas.bind('<ButtonRelease-1>', on_drag_stop)
        click_id = self.canvas.bind('<Button-1>', on_click)
        
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)
        self.resource_manager.register_binding(self.canvas, '<ButtonPress-1>', press_id)
        self.resource_manager.register_binding(self.canvas, '<B1-Motion>', drag_id)
        self.resource_manager.register_binding(self.canvas, '<ButtonRelease-1>', release_id)
        self.resource_manager.register_binding(self.canvas, '<Button-1>', click_id)

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