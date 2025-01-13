from typing import List, Optional, Tuple, Dict
import tkinter as tk
from tkinter import ttk
import math
import colorsys
from .core import Chart, ChartStyle

class InteractiveTooltip:
    """A modern tooltip that follows the mouse"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.tooltip_window = None
        self.current_item = None
    
    def show(self, text: str, x: int, y: int):
        """Show tooltip at specified position"""
        if self.tooltip_window:
            self.hide()
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.canvas)
        self.tooltip_window.overrideredirect(True)
        self.tooltip_window.configure(bg="#1E293B")
        
        # Add padding and rounded corners
        frame = ttk.Frame(self.tooltip_window, style="Tooltip.TFrame")
        frame.pack(padx=1, pady=1)
        
        # Create label with modern styling
        label = ttk.Label(frame,
                         text=text,
                         font=("Inter", 11),
                         foreground="#F8FAFC",
                         background="#1E293B",
                         padding=(8, 4))
        label.pack()
        
        # Position tooltip near mouse but not under it
        self.tooltip_window.update_idletasks()
        width = self.tooltip_window.winfo_width()
        height = self.tooltip_window.winfo_height()
        
        # Adjust position to keep tooltip on screen
        screen_width = self.canvas.winfo_screenwidth()
        screen_height = self.canvas.winfo_screenheight()
        
        x = min(x + 15, screen_width - width)
        y = min(y - height - 10, screen_height - height)
        
        self.tooltip_window.geometry(f"+{x}+{y}")
        
        # Ensure tooltip is on top
        self.tooltip_window.lift()
    
    def hide(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.current_item = None

class InteractiveChart(Chart):
    """Base class for interactive charts"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        
        # Create tooltip
        self.tooltip = InteractiveTooltip(self.canvas)
        
        # Bind mouse events
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Button-1>", self._on_click)
        
        # Store interactive elements
        self.interactive_elements = {}
        self.hover_effects = {}
        self.click_handlers = {}
    
    def _on_mouse_move(self, event):
        """Handle mouse movement"""
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        
        # Find topmost interactive item
        current_item = None
        for item in reversed(items):
            if item in self.interactive_elements:
                current_item = item
                break
        
        # Handle hover effects
        if current_item != self.tooltip.current_item:
            # Reset previous hover effect
            if self.tooltip.current_item in self.hover_effects:
                self._reset_hover(self.tooltip.current_item)
            
            # Apply new hover effect
            if current_item in self.hover_effects:
                self._apply_hover(current_item)
            
            # Update tooltip
            if current_item in self.interactive_elements:
                tooltip_text = self.interactive_elements[current_item]
                self.tooltip.show(tooltip_text, event.x_root, event.y_root)
            else:
                self.tooltip.hide()
            
            self.tooltip.current_item = current_item
    
    def _on_mouse_leave(self, event):
        """Handle mouse leaving the canvas"""
        if self.tooltip.current_item in self.hover_effects:
            self._reset_hover(self.tooltip.current_item)
        self.tooltip.hide()
    
    def _on_click(self, event):
        """Handle mouse clicks"""
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        
        # Find topmost clickable item
        for item in reversed(items):
            if item in self.click_handlers:
                self.click_handlers[item]()
                break
    
    def _apply_hover(self, item):
        """Apply hover effect to an item"""
        effect, original = self.hover_effects[item]
        try:
            if effect == "highlight":
                # Convert hex to RGB, adjust brightness, convert back to hex
                r = int(original[1:3], 16)
                g = int(original[3:5], 16)
                b = int(original[5:7], 16)
                
                # Increase brightness by 10%
                r = min(255, int(r * 1.1))
                g = min(255, int(g * 1.1))
                b = min(255, int(b * 1.1))
                
                hover_color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.itemconfig(item, fill=hover_color)
            elif effect == "glow":
                # Similar brightness adjustment for glow
                r = int(original[1:3], 16)
                g = int(original[3:5], 16)
                b = int(original[5:7], 16)
                
                # Increase brightness by 20%
                r = min(255, int(r * 1.2))
                g = min(255, int(g * 1.2))
                b = min(255, int(b * 1.2))
                
                hover_color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.itemconfig(item, fill=hover_color, width=2)
        except Exception as e:
            print(f"Error applying hover effect: {e}")
    
    def _reset_hover(self, item):
        """Reset hover effect"""
        effect, original = self.hover_effects[item]
        try:
            self.canvas.itemconfig(item, fill=original)
            if effect == "glow":
                self.canvas.itemconfig(item, width=1)
        except Exception as e:
            print(f"Error resetting hover effect: {e}")

class ColumnChart(InteractiveChart):
    """An interactive vertical bar (column) chart"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.column_width = 0.7
    
    def plot(self, data: List[float], labels: Optional[List[str]] = None):
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        
        self.data = data
        self.labels = labels or [str(i+1) for i in range(len(data))]
        
        # Calculate ranges
        x_min, x_max = -0.5, len(data) - 0.5
        y_min, y_max = 0, max(data) * 1.1
        
        self.canvas.delete("all")
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Clear previous interactive elements
        self.interactive_elements.clear()
        self.hover_effects.clear()
        self.click_handlers.clear()
        
        # Draw columns
        column_width = self.column_width
        for i, value in enumerate(data):
            x = self._data_to_pixel_x(i, x_min, x_max)
            y = self._data_to_pixel_y(value, y_min, y_max)
            bottom = self._data_to_pixel_y(0, y_min, y_max)
            
            half_width = (self._data_to_pixel_x(column_width/2, x_min, x_max) - 
                        self._data_to_pixel_x(0, x_min, x_max))
            
            # Draw column shadow
            shadow = self.canvas.create_rectangle(
                x - half_width + 3,
                y + 3,
                x + half_width + 3,
                bottom + 3,
                fill=self.style.SHADOW,
                outline=""
            )
            
            # Draw column
            color = self.style.get_gradient_color(i, len(data))
            column = self.canvas.create_rectangle(
                x - half_width,
                y,
                x + half_width,
                bottom,
                fill=color,
                outline=self.style.adjust_brightness(color, 0.8)
            )
            
            # Add interactivity
            tooltip_text = f"{self.labels[i]}\nValue: {value:,.1f}"
            self.interactive_elements[column] = tooltip_text
            self.hover_effects[column] = ("highlight", color)
            
            # Add click handler
            self.click_handlers[column] = lambda i=i, v=value: print(f"Clicked {self.labels[i]}: {v}")
            
            # Draw label
            self.canvas.create_text(
                x,
                bottom + 20,
                text=self.labels[i],
                font=self.style.LABEL_FONT,
                fill=self.style.TEXT,
                anchor='n'
            )

class GroupedBarChart(InteractiveChart):
    """An interactive chart showing multiple series of bars grouped by category"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.bar_width = 0.15
        self.data = []
        self.category_labels = []
        self.series_labels = []
        self.labels = []  # Alias for category_labels for compatibility
    
    def plot(self, data: List[List[float]], category_labels: List[str], series_labels: List[str]):
        if not data or not data[0]:
            raise ValueError("Data cannot be empty")
        if len(data) != len(series_labels):
            raise ValueError("Number of series must match number of series labels")
        if len(data[0]) != len(category_labels):
            raise ValueError("Number of categories must match number of category labels")
        
        # Store data and labels for redraw
        self.data = data
        self.category_labels = category_labels
        self.labels = category_labels  # Keep labels alias in sync
        self.series_labels = series_labels
        
        # Calculate ranges
        x_min, x_max = -0.5, len(category_labels) - 0.5
        y_min, y_max = 0, max(max(series) for series in data) * 1.1
        
        self.canvas.delete("all")
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Clear previous interactive elements
        self.interactive_elements.clear()
        self.hover_effects.clear()
        self.click_handlers.clear()
        
        # Draw bars for each series
        n_series = len(data)
        total_width = self.bar_width * n_series
        
        for series_idx, series_data in enumerate(data):
            series_color = self.style.get_gradient_color(series_idx, n_series)
            
            for cat_idx, value in enumerate(series_data):
                # Calculate bar position
                center_x = self._data_to_pixel_x(cat_idx, x_min, x_max)
                offset = (series_idx - (n_series-1)/2) * self.bar_width
                x = center_x + offset * (self.width - 2*self.padding)/(x_max - x_min)
                
                y = self._data_to_pixel_y(value, y_min, y_max)
                bottom = self._data_to_pixel_y(0, y_min, y_max)
                bar_width = self.bar_width * (self.width - 2*self.padding)/(x_max - x_min)
                
                # Draw bar shadow
                shadow = self.canvas.create_rectangle(
                    x + 2,
                    y + 2,
                    x + bar_width + 2,
                    bottom + 2,
                    fill=self.style.SHADOW,
                    outline=""
                )
                
                # Draw bar
                bar = self.canvas.create_rectangle(
                    x,
                    y,
                    x + bar_width,
                    bottom,
                    fill=series_color,
                    outline=self.style.adjust_brightness(series_color, 0.8)
                )
                
                # Add interactivity
                tooltip_text = f"{series_labels[series_idx]}\n{category_labels[cat_idx]}\nValue: {value:,.1f}"
                self.interactive_elements[bar] = tooltip_text
                self.hover_effects[bar] = ("highlight", series_color)
                
                # Add click handler
                self.click_handlers[bar] = lambda s=series_idx, c=cat_idx, v=value: (
                    print(f"Clicked {self.series_labels[s]} - {self.labels[c]}: {v}")
                )
        
        # Draw category labels
        for i, label in enumerate(category_labels):
            x = self._data_to_pixel_x(i, x_min, x_max)
            y = self._data_to_pixel_y(y_min, y_min, y_max) + 20
            self.canvas.create_text(
                x,
                y,
                text=label,
                font=self.style.LABEL_FONT,
                fill=self.style.TEXT,
                anchor='n'
            )
        
        # Draw legend
        legend_x = self.width - self.padding + 20
        legend_y = self.padding
        for i, label in enumerate(series_labels):
            color = self.style.get_gradient_color(i, len(series_labels))
            
            # Draw color box
            box = self.canvas.create_rectangle(
                legend_x,
                legend_y + i*25,
                legend_x + 15,
                legend_y + i*25 + 15,
                fill=color,
                outline=self.style.adjust_brightness(color, 0.8)
            )
            
            # Add interactivity to legend
            self.interactive_elements[box] = f"Series: {label}"
            self.hover_effects[box] = ("glow", color)
            
            # Draw label
            self.canvas.create_text(
                legend_x + 25,
                legend_y + i*25 + 7,
                text=label,
                font=self.style.LABEL_FONT,
                fill=self.style.TEXT,
                anchor='w'
            )

    def redraw_chart(self):
        """Specialized redraw for grouped bar chart"""
        if self.data and self.category_labels and self.series_labels:
            self.plot(self.data, self.category_labels, self.series_labels)

class ScatterPlot(InteractiveChart):
    """An interactive scatter plot showing relationships between variables"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.x_data = []
        self.y_data = []
        self.show_trend = False
        self.point_radius = 5
    
    def plot(self, x_data: List[float], y_data: List[float], show_trend: bool = False):
        """Plot scatter points with optional trend line"""
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have the same length")
            
        # Store data for redraw
        self.x_data = x_data
        self.y_data = y_data
        self.show_trend = show_trend
        
        # Calculate ranges with padding
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding
        
        self.canvas.delete("all")
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Clear previous interactive elements
        self.interactive_elements.clear()
        self.hover_effects.clear()
        self.click_handlers.clear()
        
        # Draw points
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            px = self._data_to_pixel_x(x, x_min, x_max)
            py = self._data_to_pixel_y(y, y_min, y_max)
            
            # Draw point shadow
            shadow = self.canvas.create_oval(
                px - self.point_radius + 2,
                py - self.point_radius + 2,
                px + self.point_radius + 2,
                py + self.point_radius + 2,
                fill=self.style.SHADOW,
                outline=""
            )
            
            # Draw point
            point = self.canvas.create_oval(
                px - self.point_radius,
                py - self.point_radius,
                px + self.point_radius,
                py + self.point_radius,
                fill=self.style.PRIMARY,
                outline=self.style.adjust_brightness(self.style.PRIMARY, 0.8)
            )
            
            # Add interactivity
            tooltip_text = f"X: {x:.1f}\nY: {y:.1f}"
            self.interactive_elements[point] = tooltip_text
            self.hover_effects[point] = ("glow", self.style.PRIMARY)
            
            # Add click handler
            self.click_handlers[point] = lambda x=x, y=y: print(f"Clicked point ({x:.1f}, {y:.1f})")
        
        # Draw trend line if requested
        if show_trend and len(x_data) > 1:
            # Calculate linear regression
            n = len(x_data)
            sum_x = sum(x_data)
            sum_y = sum(y_data)
            sum_xy = sum(x*y for x, y in zip(x_data, y_data))
            sum_xx = sum(x*x for x in x_data)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Draw trend line
            trend_x1 = x_min
            trend_y1 = slope * x_min + intercept
            trend_x2 = x_max
            trend_y2 = slope * x_max + intercept
            
            px1 = self._data_to_pixel_x(trend_x1, x_min, x_max)
            py1 = self._data_to_pixel_y(trend_y1, y_min, y_max)
            px2 = self._data_to_pixel_x(trend_x2, x_min, x_max)
            py2 = self._data_to_pixel_y(trend_y2, y_min, y_max)
            
            # Draw trend line shadow
            shadow = self.canvas.create_line(
                px1 + 2,
                py1 + 2,
                px2 + 2,
                py2 + 2,
                fill=self.style.SHADOW,
                width=2,
                dash=(5, 5)
            )
            
            # Draw trend line
            line = self.canvas.create_line(
                px1,
                py1,
                px2,
                py2,
                fill=self.style.SECONDARY,
                width=2,
                dash=(5, 5)
            )
            
            # Add tooltip for trend line
            tooltip_text = f"Trend Line\nSlope: {slope:.2f}\nIntercept: {intercept:.2f}"
            self.interactive_elements[line] = tooltip_text

    def redraw_chart(self):
        """Specialized redraw for scatter plot"""
        if self.x_data and self.y_data:
            self.plot(self.x_data, self.y_data, self.show_trend)

class BubbleChart(InteractiveChart):
    """An interactive bubble chart showing relationships with variable-sized bubbles"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.x_data = []
        self.y_data = []
        self.sizes = []
        self.labels = []
        self.min_radius = 5
        self.max_radius = 30
        self.show_trend = False
        
    def plot(self, x_data: List[float], y_data: List[float], sizes: List[float], labels: Optional[List[str]] = None):
        """Plot bubbles with variable sizes"""
        if len(x_data) != len(y_data) or len(x_data) != len(sizes):
            raise ValueError("x_data, y_data, and sizes must have the same length")
        
        # Store data for redraw
        self.x_data = x_data
        self.y_data = y_data
        self.sizes = sizes
        self.labels = labels if labels else [f"Point {i+1}" for i in range(len(x_data))]
        
        # Calculate ranges with padding
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding
        
        self.canvas.delete("all")
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Normalize sizes to bubble radii
        size_min, size_max = min(sizes), max(sizes)
        size_range = size_max - size_min
        
        # Draw bubbles
        for i, (x, y, size) in enumerate(zip(x_data, y_data, sizes)):
            px = self._data_to_pixel_x(x, x_min, x_max)
            py = self._data_to_pixel_y(y, y_min, y_max)
            
            # Calculate radius based on size
            if size_range == 0:
                radius = (self.min_radius + self.max_radius) / 2
            else:
                normalized_size = (size - size_min) / size_range
                radius = self.min_radius + normalized_size * (self.max_radius - self.min_radius)
            
            # Create gradient fill
            gradient_color = self.style.get_gradient_color(i, len(x_data))
            
            # Draw bubble shadow
            shadow = self.canvas.create_oval(
                px - radius + 2, py - radius + 2,
                px + radius + 2, py + radius + 2,
                fill=self.style.create_shadow(gradient_color),
                outline=""
            )
            
            # Draw bubble
            bubble = self.canvas.create_oval(
                px - radius, py - radius,
                px + radius, py + radius,
                fill=gradient_color,
                outline=self.style.BACKGROUND,
                width=2
            )
            
            # Add hover effect and tooltip
            tooltip_text = f"{self.labels[i]}\nX: {x:.2f}\nY: {y:.2f}\nSize: {size:.2f}"
            self.interactive_elements[bubble] = tooltip_text
            self.hover_effects[bubble] = ("glow", gradient_color)
            
            # Add click handler
            self.click_handlers[bubble] = lambda b=bubble, l=self.labels[i], x=x, y=y, s=size: \
                print(f"Clicked {l}: X={x:.2f}, Y={y:.2f}, Size={s:.2f}")
    
    def redraw_chart(self):
        """Specialized redraw for bubble chart"""
        if self.x_data and self.y_data and self.sizes:
            self.plot(self.x_data, self.y_data, self.sizes, self.labels)

class Heatmap(InteractiveChart):
    """An interactive heatmap showing relationships using color intensity"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.row_labels = []
        self.col_labels = []
        self.cell_size = 40
        self.colormap = [
            "#313695",  # Dark blue
            "#4575B4",  # Blue
            "#74ADD1",  # Light blue
            "#ABD9E9",  # Very light blue
            "#E0F3F8",  # Pale blue
            "#FFFFBF",  # Pale yellow
            "#FEE090",  # Light orange
            "#FDAE61",  # Orange
            "#F46D43",  # Dark orange
            "#D73027"   # Red
        ]
    
    def plot(self, data: List[List[float]], row_labels: Optional[List[str]] = None, 
            col_labels: Optional[List[str]] = None):
        """Plot heatmap with color intensity based on values"""
        if not data or not data[0]:
            raise ValueError("Data cannot be empty")
        
        # Store data for redraw
        self.data = data
        self.row_labels = row_labels if row_labels else [f"Row {i+1}" for i in range(len(data))]
        self.col_labels = col_labels if col_labels else [f"Col {i+1}" for i in range(len(data[0]))]
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Calculate cell size based on available space
        available_width = self.width - 2 * self.padding
        available_height = self.height - 2 * self.padding
        self.cell_size = min(
            available_width / len(data[0]),
            available_height / len(data)
        )
        
        # Find data range for color mapping
        all_values = [val for row in data for val in row]
        data_min, data_max = min(all_values), max(all_values)
        data_range = data_max - data_min if data_max != data_min else 1
        
        # Calculate starting position
        start_x = self.padding + (available_width - self.cell_size * len(data[0])) / 2
        start_y = self.padding + (available_height - self.cell_size * len(data)) / 2
        
        # Draw cells
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                x = start_x + j * self.cell_size
                y = start_y + i * self.cell_size
                
                # Calculate color based on value
                normalized_value = (value - data_min) / data_range
                color_index = min(int(normalized_value * (len(self.colormap) - 1)), len(self.colormap) - 1)
                cell_color = self.colormap[color_index]
                
                # Draw cell with shadow
                shadow = self.canvas.create_rectangle(
                    x + 2, y + 2,
                    x + self.cell_size + 2, y + self.cell_size + 2,
                    fill=self.style.create_shadow(cell_color),
                    outline=""
                )
                
                cell = self.canvas.create_rectangle(
                    x, y,
                    x + self.cell_size, y + self.cell_size,
                    fill=cell_color,
                    outline=self.style.BACKGROUND,
                    width=1
                )
                
                # Add hover effect and tooltip
                tooltip_text = f"{self.row_labels[i]} × {self.col_labels[j]}\nValue: {value:.2f}"
                self.interactive_elements[cell] = tooltip_text
                self.hover_effects[cell] = ("glow", cell_color)
                
                # Add click handler
                self.click_handlers[cell] = lambda r=self.row_labels[i], c=self.col_labels[j], v=value: \
                    print(f"Clicked {r} × {c}: {v:.2f}")
        
        # Draw labels
        label_font = self.style.LABEL_FONT
        
        # Column labels
        for j, label in enumerate(self.col_labels):
            x = start_x + j * self.cell_size + self.cell_size / 2
            y = start_y - 20
            self.canvas.create_text(
                x, y,
                text=label,
                font=label_font,
                fill=self.style.TEXT,
                anchor='s',
                angle=45 if len(label) > 5 else 0
            )
        
        # Row labels
        for i, label in enumerate(self.row_labels):
            x = start_x - 10
            y = start_y + i * self.cell_size + self.cell_size / 2
            self.canvas.create_text(
                x, y,
                text=label,
                font=label_font,
                fill=self.style.TEXT,
                anchor='e'
            )
    
    def redraw_chart(self):
        """Specialized redraw for heatmap"""
        if self.data:
            self.plot(self.data, self.row_labels, self.col_labels)

class NetworkGraph(InteractiveChart):
    """An interactive network graph showing relationships between nodes"""
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.nodes = []
        self.edges = []
        self.node_labels = []
        self.node_radius = 20
        self.edge_width = 2
        self.node_positions = {}  # Store node positions for redraw
        
    def plot(self, nodes: List[str], edges: List[Tuple[str, str]], 
            node_values: Optional[List[float]] = None,
            edge_values: Optional[List[float]] = None):
        """Plot network graph with nodes and edges"""
        if not nodes:
            raise ValueError("Nodes cannot be empty")
            
        # Store data for redraw
        self.nodes = nodes
        self.edges = edges
        self.node_values = node_values if node_values else [1.0] * len(nodes)
        self.edge_values = edge_values if edge_values else [1.0] * len(edges)
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Calculate node positions (simple circular layout)
        center_x = self.width / 2
        center_y = self.height / 2
        radius = min(self.width, self.height) / 3
        angle_step = 2 * math.pi / len(nodes)
        
        # Store node positions
        self.node_positions = {}
        for i, node in enumerate(nodes):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[node] = (x, y)
        
        # Draw edges first (so they appear behind nodes)
        for i, (source, target) in enumerate(edges):
            if source in self.node_positions and target in self.node_positions:
                x1, y1 = self.node_positions[source]
                x2, y2 = self.node_positions[target]
                
                # Calculate edge color and width based on value
                edge_color = self.style.PRIMARY
                if edge_values:
                    normalized_value = (self.edge_values[i] - min(self.edge_values)) / \
                                    (max(self.edge_values) - min(self.edge_values))
                    edge_color = self.style.get_gradient_color(
                        int(normalized_value * (len(self.style.CHART_COLORS) - 1)),
                        len(self.style.CHART_COLORS)
                    )
                
                # Draw edge shadow
                shadow = self.canvas.create_line(
                    x1 + 2, y1 + 2, x2 + 2, y2 + 2,
                    fill=self.style.create_shadow(edge_color),
                    width=self.edge_width + 1
                )
                
                # Draw edge
                edge = self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=edge_color,
                    width=self.edge_width,
                    smooth=True
                )
                
                # Add hover effect and tooltip for edge
                if edge_values:
                    tooltip_text = f"{source} → {target}\nValue: {self.edge_values[i]:.2f}"
                    self.interactive_elements[edge] = tooltip_text
                    self.hover_effects[edge] = ("highlight", edge_color)
        
        # Draw nodes
        for i, node in enumerate(nodes):
            x, y = self.node_positions[node]
            
            # Calculate node color and size based on value
            node_color = self.style.get_gradient_color(i, len(nodes))
            node_radius = self.node_radius
            if node_values:
                normalized_value = (self.node_values[i] - min(self.node_values)) / \
                                (max(self.node_values) - min(self.node_values))
                node_radius = self.node_radius * (0.5 + normalized_value)
            
            # Draw node shadow
            shadow = self.canvas.create_oval(
                x - node_radius + 2, y - node_radius + 2,
                x + node_radius + 2, y + node_radius + 2,
                fill=self.style.create_shadow(node_color),
                outline=""
            )
            
            # Draw node
            node_circle = self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=node_color,
                outline=self.style.BACKGROUND,
                width=2
            )
            
            # Draw node label
            self.canvas.create_text(
                x, y,
                text=node,
                font=self.style.LABEL_FONT,
                fill=self.style.BACKGROUND
            )
            
            # Add hover effect and tooltip for node
            tooltip_text = f"Node: {node}"
            if node_values:
                tooltip_text += f"\nValue: {self.node_values[i]:.2f}"
            self.interactive_elements[node_circle] = tooltip_text
            self.hover_effects[node_circle] = ("glow", node_color)
            
            # Add click handler
            self.click_handlers[node_circle] = lambda n=node, v=self.node_values[i]: \
                print(f"Clicked node {n}" + (f" (Value: {v:.2f})" if node_values else ""))
    
    def redraw_chart(self):
        """Specialized redraw for network graph"""
        if self.nodes and self.edges:
            self.plot(self.nodes, self.edges, self.node_values, self.edge_values)
