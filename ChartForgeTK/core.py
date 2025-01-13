import math
from typing import List, Optional, Union, Tuple
import colorsys
import tkinter as tk
from tkinter import ttk, font

class ChartStyle:
    # Modern color palette
    PRIMARY = "#2196F3"  # Blue
    SECONDARY = "#FF4081"  # Pink
    BACKGROUND = "#FFFFFF"  # White
    GRID = "#E0E0E0"  # Light Gray
    TEXT = "#333333"  # Dark Gray
    ACCENT = "#00BCD4"  # Cyan
    SHADOW = "#CCCCCC"  # Light Shadow
    AXIS_COLOR = "#333333"
    AXIS_WIDTH = 2
    GRID_COLOR = "#E0E0E0"
    GRID_WIDTH = 1
    TICK_COLOR = "#333333"
    TICK_LENGTH = 5
    AXIS_FONT = ("Helvetica", 10)
    TITLE_FONT = ("Helvetica", 16, "bold")
    LABEL_FONT = ("Helvetica", 10)
    VALUE_FONT = ("Helvetica", 9)
    TEXT_SECONDARY = "#666666"
    TOOLTIP_BACKGROUND = "#FFFFFF"
    TOOLTIP_TEXT = "#333333"
    TOOLTIP_FONT = ("Helvetica", 10)
    TOOLTIP_PADDING = (5, 5)
    PADDING = 50
    
    # Chart colors
    CHART_COLORS = [
        "#2196F3",  # Blue
        "#4CAF50",  # Green
        "#FFC107",  # Amber
        "#9C27B0",  # Purple
        "#FF5722",  # Deep Orange
        "#00BCD4",  # Cyan
        "#FF4081",  # Pink
        "#8BC34A",  # Light Green
    ]
    
    @staticmethod
    def get_gradient_color(index: int, total: int) -> str:
        """Get a color from the gradient based on position"""
        return ChartStyle.CHART_COLORS[index % len(ChartStyle.CHART_COLORS)]
    
    @staticmethod
    def create_shadow(color: str) -> str:
        """Create a shadow color from the given color"""
        rgb = tuple(int(int(color[1:][j:j+2], 16)) for j in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(
            int(rgb[0] * 0.8),
            int(rgb[1] * 0.8),
            int(rgb[2] * 0.8)
        )
    
    @staticmethod
    def create_rgba_from_hex(hex_color: str, alpha: float) -> str:
        """Create a darker version of the color based on alpha"""
        rgb = tuple(int(int(hex_color[1:][j:j+2], 16)) for j in (0, 2, 4))
        darkened = tuple(int(c * alpha) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    @staticmethod
    def adjust_brightness(hex_color: str, factor: float) -> str:
        """Adjust the brightness of a hex color"""
        rgb = tuple(int(int(hex_color[1:][j:j+2], 16)) for j in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(
            int(rgb[0] + (255 - rgb[0]) * (1 - factor)),
            int(rgb[1] + (255 - rgb[1]) * (1 - factor)),
            int(rgb[2] + (255 - rgb[2]) * (1 - factor))
        )

class Chart(tk.Frame):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        """Initialize chart with modern styling"""
        # Validate input parameters
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        if display_mode not in ['frame', 'window']:
            raise ValueError("Display mode must be either 'frame' or 'window'")
            
        self.style = ChartStyle()
        
        if display_mode == 'window':
            self.window = tk.Toplevel()
            self.window.title("Chart View")
            parent = self.window
            
            # Create modern window controls
            control_frame = ttk.Frame(self.window)
            control_frame.pack(fill='x', padx=1, pady=1)
            
            # Configure styles for window control buttons
            style = ttk.Style()
            
            # Close button style
            style.configure('Close.WindowControl.TButton',
                          padding=4,
                          relief='flat',
                          background=self.style.BACKGROUND,
                          foreground=self.style.TEXT,
                          font=('Helvetica', 14))
            
            # Maximize button style
            style.configure('Max.WindowControl.TButton',
                          padding=4,
                          relief='flat',
                          background=self.style.BACKGROUND,
                          foreground=self.style.TEXT,
                          font=('Helvetica', 12))
            
            # Minimize button style
            style.configure('Min.WindowControl.TButton',
                          padding=4,
                          relief='flat',
                          background=self.style.BACKGROUND,
                          foreground=self.style.TEXT,
                          font=('Helvetica', 12))
            
            # Add hover effects
            for btn_style in ['Close', 'Max', 'Min']:
                style.map(f'{btn_style}.WindowControl.TButton',
                         background=[('active', self.style.PRIMARY)],
                         foreground=[('active', self.style.BACKGROUND)])
            
            # Close button (×)
            close_btn = ttk.Button(
                control_frame,
                text="×",
                width=3,
                style='Close.WindowControl.TButton',
                command=self.window.destroy
            )
            close_btn.pack(side='right', padx=1)
            
            # Maximize button (□)
            self.maximize_btn = ttk.Button(
                control_frame,
                text="□",
                width=3,
                style='Max.WindowControl.TButton',
                command=self._toggle_maximize
            )
            self.maximize_btn.pack(side='right', padx=1)
            
            # Minimize button (_)
            minimize_btn = ttk.Button(
                control_frame,
                text="_",
                width=3,
                style='Min.WindowControl.TButton',
                command=lambda: self.window.iconify()
            )
            minimize_btn.pack(side='right', padx=1)
            
            # Track window state
            self.is_maximized = False
            self.window.bind("<Configure>", self._on_window_configure)
            
            # Store original window size and position
            self.original_geometry = None
            
            # Center window on screen
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        super().__init__(parent)
        
        # Initialize chart properties
        self.width = width
        self.height = height
        self.padding = self.style.PADDING
        self.display_mode = display_mode
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        
        # Modern styling for the chart
        self.configure(
            width=width,
            height=height,
            background=self.style.BACKGROUND
        )
        
        # Create canvas with modern styling
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            background=self.style.BACKGROUND,
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Add modern styling
        if display_mode == 'window':
            self.window.configure(background=self.style.BACKGROUND)
            self.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if not self.is_maximized:
            # Store current geometry before maximizing
            self.original_geometry = self.window.geometry()
            
            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Set window to maximum size
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")
            self.maximize_btn.configure(text="❐")
            self.is_maximized = True
        else:
            # Restore original geometry
            if self.original_geometry:
                self.window.geometry(self.original_geometry)
            self.maximize_btn.configure(text="□")
            self.is_maximized = False
    
    def _on_window_configure(self, event):
        """Handle window resize events"""
        if event.widget == self.window:
            # Update canvas size to match window
            width = event.width - 20  # Account for padding
            height = event.height - 20
            self.canvas.configure(width=width, height=height)
            self.width = width
            self.height = height
            
            # Redraw chart with new dimensions
            self.redraw()
    
    def redraw(self):
        """Redraw the chart with current data"""
        self.clear()
        if hasattr(self, 'data'):
            if hasattr(self, 'redraw_chart'):
                # Call specialized redraw if available
                self.redraw_chart()
            else:
                # Default redraw behavior
                self.plot(self.data)
    
    def clear(self):
        """Clear the canvas"""
        self.canvas.delete("all")
    
    def show(self):
        """Display the chart in window mode"""
        if self.display_mode == 'window':
            self.window.mainloop()
            
    def to_window(self):
        """Convert the chart to a separate window"""
        if self.display_mode != 'window':
            # Store current data and settings
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)
            
            # Create new instance in window mode
            new_chart = self.__class__(width=self.width, height=self.height, display_mode='window')
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label
            
            # Replot the data
            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            
            return new_chart
            
    def to_frame(self, parent):
        """Convert the chart to an embedded frame"""
        if self.display_mode != 'frame':
            # Store current data and settings
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)
            
            # Create new instance in frame mode
            new_chart = self.__class__(parent=parent, width=self.width, height=self.height, display_mode='frame')
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label
            
            # Replot the data
            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            
            return new_chart

    def _draw_axes(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw beautiful axes with grid lines."""
        # Draw grid lines first
        self._draw_grid(x_min, x_max, y_min, y_max)
        
        # Draw axes with modern style
        # Y-axis
        self.canvas.create_line(
            self.padding, self.padding,
            self.padding, self.height - self.padding,
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )
        
        # X-axis
        self.canvas.create_line(
            self.padding, self._data_to_pixel_y(0, y_min, y_max),
            self.width - self.padding, self._data_to_pixel_y(0, y_min, y_max),
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )
        
        # Draw ticks and labels
        self._draw_ticks(x_min, x_max, y_min, y_max)
        
        # Draw title if set
        if hasattr(self, 'title') and self.title:
            self.canvas.create_text(
                self.width / 2,
                self.padding / 2,
                text=self.title,
                font=self.style.TITLE_FONT,
                fill=self.style.TEXT,
                anchor='center'
            )
        
        # Draw axis labels if set
        if hasattr(self, 'x_label') and self.x_label:
            self.canvas.create_text(
                self.width / 2,
                self.height - self.padding / 3,
                text=self.x_label,
                font=self.style.LABEL_FONT,
                fill=self.style.TEXT_SECONDARY,
                anchor='center'
            )
            
        if hasattr(self, 'y_label') and self.y_label:
            self.canvas.create_text(
                self.padding / 3,
                self.height / 2,
                text=self.y_label,
                font=self.style.LABEL_FONT,
                fill=self.style.TEXT_SECONDARY,
                anchor='center',
                angle=90
            )
    
    def _draw_grid(self, x_min, x_max, y_min, y_max):
        """Draw subtle grid lines."""
        # Calculate nice tick intervals
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)
        
        # Draw vertical grid lines
        x = math.ceil(x_min / x_interval) * x_interval
        while x <= x_max:
            px = self._data_to_pixel_x(x, x_min, x_max)
            self.canvas.create_line(
                px, self.padding,
                px, self.height - self.padding,
                fill=self.style.GRID_COLOR,
                width=self.style.GRID_WIDTH,
                dash=(2, 4)
            )
            x += x_interval
        
        # Draw horizontal grid lines
        y = math.ceil(y_min / y_interval) * y_interval
        while y <= y_max:
            py = self._data_to_pixel_y(y, y_min, y_max)
            self.canvas.create_line(
                self.padding, py,
                self.width - self.padding, py,
                fill=self.style.GRID_COLOR,
                width=self.style.GRID_WIDTH,
                dash=(2, 4)
            )
            y += y_interval
    
    def _draw_ticks(self, x_min, x_max, y_min, y_max):
        """Draw axis ticks and labels with modern styling."""
        # Calculate nice tick intervals
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)
        
        # Draw x-axis ticks and labels
        x = math.ceil(x_min / x_interval) * x_interval
        while x <= x_max:
            px = self._data_to_pixel_x(x, x_min, x_max)
            py = self._data_to_pixel_y(0, y_min, y_max)
            
            # Draw tick
            self.canvas.create_line(
                px, py,
                px, py + self.style.TICK_LENGTH,
                fill=self.style.TICK_COLOR,
                width=self.style.AXIS_WIDTH,
                capstyle=tk.ROUND
            )
            
            # Draw label
            self.canvas.create_text(
                px,
                py + self.style.TICK_LENGTH + 5,
                text=f"{x:g}",
                font=self.style.AXIS_FONT,
                fill=self.style.TEXT_SECONDARY,
                anchor='n'
            )
            x += x_interval
        
        # Draw y-axis ticks and labels
        y = math.ceil(y_min / y_interval) * y_interval
        while y <= y_max:
            px = self.padding
            py = self._data_to_pixel_y(y, y_min, y_max)
            
            # Draw tick
            self.canvas.create_line(
                px - self.style.TICK_LENGTH, py,
                px, py,
                fill=self.style.TICK_COLOR,
                width=self.style.AXIS_WIDTH,
                capstyle=tk.ROUND
            )
            
            # Draw label with proper formatting
            if abs(y) >= 1000:
                text = f"{y/1000:g}k"
            else:
                text = f"{y:g}"
                
            self.canvas.create_text(
                px - self.style.TICK_LENGTH - 5,
                py,
                text=text,
                font=self.style.AXIS_FONT,
                fill=self.style.TEXT_SECONDARY,
                anchor='e'
            )
            y += y_interval
            
    def _create_tooltip(self) -> Tuple[tk.Toplevel, ttk.Label]:
        """Create a beautiful modern tooltip."""
        tooltip = tk.Toplevel(self.canvas)
        tooltip.wm_overrideredirect(True)
        
        # Create a frame with padding and modern styling
        frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        frame.pack(fill='both', expand=True)
        
        # Configure tooltip style
        style = ttk.Style()
        style.configure('Tooltip.TFrame',
                       background=self.style.TEXT,
                       relief='solid',
                       borderwidth=0)
        
        # Create label with modern font
        label = ttk.Label(frame,
                         font=self.style.TOOLTIP_FONT,
                         foreground=self.style.BACKGROUND,
                         background=self.style.TEXT,
                         padding=self.style.TOOLTIP_PADDING)
        label.pack()
        
        tooltip.withdraw()
        return tooltip, label

    def _data_to_pixel_x(self, x: float, x_min: float, x_max: float) -> float:
        """Convert data coordinate to pixel coordinate for x-axis"""
        if x_max == x_min:
            return self.padding
        try:
            return self.padding + (x - x_min) * (self.width - 2 * self.padding) / (x_max - x_min)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid x coordinate conversion: {e}")

    def _data_to_pixel_y(self, y: float, y_min: float, y_max: float) -> float:
        """Convert data coordinate to pixel coordinate for y-axis"""
        if y_max == y_min:
            return self.height - self.padding
        try:
            return self.height - (self.padding + (y - y_min) * (self.height - 2 * self.padding) / (y_max - y_min))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid y coordinate conversion: {e}")

    def _calculate_tick_interval(self, range: float) -> float:
        """Calculate a nice tick interval based on the range."""
        if range == 0:
            return 1
        
        exp = math.floor(math.log10(range))
        interval = 10 ** exp
        
        if range / interval < 5:
            interval /= 2
        elif range / interval < 10:
            interval /= 5
        
        return interval

class LineChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.line_width = 2.5
        self.point_radius = 4
        self.show_points = True
        self.smooth = True
        self.x_labels = []  # Store x-axis labels
        self.interactive_elements = {}  # Store interactive elements
        self.hover_effects = {}  # Store hover effects
        
    def plot(self, data: List[float], x_labels: Optional[List[str]] = None):
        """Plot the line chart with the given data"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
            
        self.data = data  # Store the data
        self.x_labels = x_labels if x_labels else [str(i) for i in range(len(data))]
            
        # Calculate data ranges with padding
        x_min, x_max = 0, len(data) - 1
        y_min, y_max = min(data), max(data)
        padding = (y_max - y_min) * 0.1
        y_min -= padding
        y_max += padding
        
        self.canvas.delete("all")  # Clear before redrawing
        
        # Create points for the line
        points = []
        for i, y in enumerate(data):
            px = self._data_to_pixel_x(i, x_min, x_max)
            py = self._data_to_pixel_y(y, y_min, y_max)
            points.extend([px, py])
            
        if len(points) >= 4:
            # Draw gradient background under the line first
            fill_points = points.copy()
            # Add bottom corners to create a closed polygon
            fill_points.append(points[-2])  # Last x
            fill_points.append(self._data_to_pixel_y(y_min, y_min, y_max))  # Bottom y
            fill_points.append(points[0])   # First x
            fill_points.append(self._data_to_pixel_y(y_min, y_min, y_max))  # Bottom y
            
            # Create gradient effect with reduced opacity
            gradient_steps = 20
            base_color = self.style.PRIMARY
            for i in range(gradient_steps):
                alpha = 0.05 * (1 - i/gradient_steps)  # Reduced opacity
                rgb = tuple(int(int(base_color[1:][j:j+2], 16)) for j in (0, 2, 4))
                gradient_color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] + (255 - rgb[0]) * (1 - alpha)),
                    int(rgb[1] + (255 - rgb[1]) * (1 - alpha)),
                    int(rgb[2] + (255 - rgb[2]) * (1 - alpha))
                )
                
                offset = i * (self._data_to_pixel_y(y_min, y_min, y_max) - 
                            min(points[1::2])) / gradient_steps
                
                fill_points_offset = fill_points.copy()
                for j in range(1, len(fill_points_offset), 2):
                    if j < len(points):
                        fill_points_offset[j] = min(
                            fill_points_offset[j] + offset,
                            self._data_to_pixel_y(y_min, y_min, y_max)
                        )
                
                self.canvas.create_polygon(
                    fill_points_offset,
                    fill=gradient_color,
                    outline="",
                    smooth=self.smooth
                )
        
        # Draw axes with custom x labels
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Draw x-axis labels
        label_interval = max(1, len(self.x_labels) // 10)  # Show at most 10 labels
        for i, label in enumerate(self.x_labels):
            if i % label_interval == 0:
                x = self._data_to_pixel_x(i, x_min, x_max)
                y = self.height - self.padding + 20
                self.canvas.create_text(
                    x, y,
                    text=label,
                    font=self.style.LABEL_FONT,
                    fill=self.style.TEXT,
                    anchor='n'
                )
        
        # Draw the main line on top
        if len(points) >= 4:
            # Draw shadow line
            shadow_offset = 3
            shadow_points = points.copy()
            for i in range(1, len(shadow_points), 2):
                shadow_points[i] += shadow_offset
            
            self.canvas.create_line(
                shadow_points,
                fill=self.style.create_shadow(self.style.PRIMARY),
                width=self.line_width + 1,
                smooth=self.smooth
            )
            
            # Draw main line
            line = self.canvas.create_line(
                points,
                fill=self.style.PRIMARY,
                width=self.line_width,
                smooth=self.smooth
            )
            
            # Draw points if enabled
            if self.show_points:
                for i in range(0, len(points), 2):
                    px, py = points[i], points[i+1]
                    
                    # Draw point shadow
                    self.canvas.create_oval(
                        px - self.point_radius + 1, py - self.point_radius + 1,
                        px + self.point_radius + 1, py + self.point_radius + 1,
                        fill=self.style.create_shadow(self.style.PRIMARY),
                        outline=""
                    )
                    
                    # Draw point
                    point = self.canvas.create_oval(
                        px - self.point_radius, py - self.point_radius,
                        px + self.point_radius, py + self.point_radius,
                        fill=self.style.BACKGROUND,
                        outline=self.style.PRIMARY,
                        width=2
                    )
                    
                    # Add tooltip
                    index = i // 2
                    tooltip_text = f"Point {self.x_labels[index]}\nValue: {self.data[index]:.2f}"
                    self.interactive_elements[point] = tooltip_text
                    
                    # Add hover effect
                    self.hover_effects[point] = ("glow", self.style.PRIMARY)
    
    def redraw_chart(self):
        """Specialized redraw for line chart"""
        if self.data:
            self.plot(self.data, self.x_labels)

class BarChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.bar_width = 0.7  # Percentage of available space
        
    def plot(self, data: List[float]):
        """Plot the bar chart with the given data"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        if any(x < 0 for x in data):
            raise ValueError("Bar chart data cannot contain negative values")
            
        self.data = data  # Store the data
            
        # Calculate data ranges
        x_min, x_max = -0.5, len(data) - 0.5
        y_min, y_max = min(min(data), 0), max(data)
        padding = (y_max - y_min) * 0.1
        y_min -= padding
        y_max += padding
        
        # Clear previous content
        self.canvas.delete('all')
        
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Calculate bar width based on available space
        bar_width = (self.width - 2 * self.padding) / len(data) * self.bar_width
        
        # Draw bars
        for i, y in enumerate(data):
            x = self._data_to_pixel_x(i, x_min, x_max)
            y0 = self._data_to_pixel_y(0, y_min, y_max)
            y1 = self._data_to_pixel_y(y, y_min, y_max)
            
            # Get bar color with gradient
            color = self.style.get_gradient_color(i, len(data))
            
            # Draw bar shadow
            shadow_offset = 3
            self.canvas.create_rectangle(
                x - bar_width/2 + shadow_offset,
                min(y0, y1),
                x + bar_width/2 + shadow_offset,
                max(y0, y1),
                fill=self.style.create_shadow(color),
                outline="",
                tags=('bar_shadow', f'bar_{i}')
            )
            
            # Create gradient effect
            bar_height = abs(y1 - y0)
            gradient_steps = 20
            step_height = bar_height / gradient_steps
            
            # Draw gradient rectangles from bottom to top
            for step in range(gradient_steps):
                y_start = min(y0, y1) + step * step_height
                y_end = y_start + step_height
                
                # Calculate gradient color
                progress = step / gradient_steps
                alpha = 0.95 - progress * 0.3  # Fade out slightly towards the top
                gradient_color = self.style.create_rgba_from_hex(color, alpha)
                
                self.canvas.create_rectangle(
                    x - bar_width/2,
                    y_start,
                    x + bar_width/2,
                    y_end,
                    fill=gradient_color,
                    outline="",
                    tags=('bar_gradient', f'bar_{i}')
                )
            
            # Draw bar outline
            self.canvas.create_rectangle(
                x - bar_width/2,
                min(y0, y1),
                x + bar_width/2,
                max(y0, y1),
                outline=self.style.adjust_brightness(color, 0.8),
                width=1,
                tags=('bar_outline', f'bar_{i}')
            )
            
            # Add value label
            value_text = f"{y:,.0f}"
            self.canvas.create_text(
                x,
                y1 - 10 if y >= 0 else y1 + 10,
                text=value_text,
                font=self.style.VALUE_FONT,
                fill=self.style.TEXT,
                anchor='s' if y >= 0 else 'n',
                tags=('value_label', f'bar_{i}')
            )
        
        # Add hover effect
        self._add_hover_effect(bar_width)
        
    def _add_hover_effect(self, bar_width):
        """Add hover effect to bars with smooth animation and modern tooltip"""
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)
        
        # Create modern tooltip style
        tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        
        # Create tooltip label with modern font
        label = ttk.Label(tooltip_frame, 
                         style='Tooltip.TLabel',
                         font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        # Configure tooltip styles
        style = ttk.Style()
        style.configure('Tooltip.TFrame', 
                       background=self.style.TEXT,
                       relief='solid',
                       borderwidth=0)
        style.configure('Tooltip.TLabel',
                       background=self.style.TEXT,
                       foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        # Track current highlight and hovered bar
        current_highlight = None
        hovered_bar = None
        
        def on_enter(event):
            nonlocal current_highlight, hovered_bar
            
            # Check if we have data to work with
            if not self.data:
                return
                
            x = event.x
            if self.padding <= x <= self.width - self.padding:
                try:
                    # Calculate which bar we're hovering over
                    relative_x = x - self.padding
                    bar_total_width = (self.width - 2 * self.padding) / len(self.data)
                    bar_index = int(relative_x / bar_total_width)
                    
                    if 0 <= bar_index < len(self.data):
                        value = self.data[bar_index]
                        
                        # Only update if hovering over a new bar
                        if hovered_bar != bar_index:
                            hovered_bar = bar_index
                            
                            # Remove previous highlight
                            if current_highlight:
                                for item in current_highlight:
                                    self.canvas.delete(item)
                            
                            # Get bar position
                            px = self._data_to_pixel_x(bar_index, -0.5, len(self.data) - 0.5)
                            py0 = self._data_to_pixel_y(0, min(min(self.data), 0), max(self.data))
                            py1 = self._data_to_pixel_y(value, min(min(self.data), 0), max(self.data))
                            
                            # Create highlight effect
                            highlight_items = []
                            
                            # Glow effect
                            for i in range(3):
                                offset = i * 2
                                alpha = 0.3 - i * 0.1
                                glow_color = self.style.create_rgba_from_hex(self.style.ACCENT, alpha)
                                glow = self.canvas.create_rectangle(
                                    px - bar_width/2 - offset,
                                    min(py0, py1) - offset,
                                    px + bar_width/2 + offset,
                                    max(py0, py1) + offset,
                                    fill="",
                                    outline=glow_color,
                                    width=2,
                                    tags=('highlight',)
                                )
                                highlight_items.append(glow)
                            
                            # Main highlight
                            border = self.canvas.create_rectangle(
                                px - bar_width/2 - 1,
                                min(py0, py1) - 1,
                                px + bar_width/2 + 1,
                                max(py0, py1) + 1,
                                outline=self.style.ACCENT,
                                width=2,
                                tags=('highlight',)
                            )
                            highlight_items.append(border)
                            
                            current_highlight = highlight_items
                            
                            # Update tooltip
                            label.config(text=f"Value: {value:,.0f}")
                            
                            # Position tooltip above or below the bar based on value
                            if value >= 0:
                                tooltip_y = event.y_root - 30
                            else:
                                tooltip_y = event.y_root + 10
                            
                            tooltip.wm_geometry(f"+{event.x_root+10}+{tooltip_y}")
                            tooltip.deiconify()
                            tooltip.lift()
                        else:
                            # Just update tooltip position
                            if value >= 0:
                                tooltip_y = event.y_root - 30
                            else:
                                tooltip_y = event.y_root + 10
                            tooltip.wm_geometry(f"+{event.x_root+10}+{tooltip_y}")
                except (ZeroDivisionError, ValueError, IndexError):
                    pass
        
        def on_leave(event):
            nonlocal current_highlight, hovered_bar
            # Only hide if actually leaving the chart area
            if not (self.padding <= event.x <= self.width - self.padding and
                   self.padding <= event.y <= self.height - self.padding):
                if current_highlight:
                    for item in current_highlight:
                        self.canvas.delete(item)
                current_highlight = None
                hovered_bar = None
                tooltip.withdraw()
        
        self.canvas.bind('<Motion>', on_enter)
        self.canvas.bind('<Leave>', on_leave)

class PieChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.labels = []
        self.colors = []
        
    def redraw_chart(self):
        """Specialized redraw for pie chart"""
        if self.data and self.labels:
            self.plot(self.data, self.labels)
    
    def _generate_colors(self):
        """Generate colors for pie slices"""
        self.colors = [self.style.get_gradient_color(i, len(self.data)) for i in range(len(self.data))]
    
    def plot(self, data: List[float], labels: List[str]):
        """Plot the pie chart with the given data and labels"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        if any(x < 0 for x in data):
            raise ValueError("Pie chart data cannot contain negative values")
        if not labels:
            raise ValueError("Labels cannot be empty")
        if len(data) != len(labels):
            raise ValueError("Number of data points must match number of labels")
            
        self.data = data
        self.labels = labels
        self._generate_colors()
            
        # Calculate center and radius
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(self.width, self.height) // 3
        
        # Draw title
        if self.title:
            self.canvas.create_text(
                center_x, self.padding,
                text=self.title,
                font=self.style.TITLE_FONT,
                fill=self.style.TEXT
            )
        
        # Draw shadow
        shadow_offset = 3
        self.canvas.create_oval(
            center_x - radius + shadow_offset,
            center_y - radius + shadow_offset,
            center_x + radius + shadow_offset,
            center_y + radius + shadow_offset,
            fill=self.style.SHADOW,
            outline=""
        )
        
        # Draw pie slices
        start_angle = 0
        total = sum(self.data)
        
        for i, (value, color) in enumerate(zip(self.data, self.colors)):
            angle = value / total * 360
            
            # Draw slice
            self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle,
                extent=angle,
                fill=color,
                outline=self.style.BACKGROUND,
                width=2
            )
            
            # Calculate label position
            label_angle = math.radians(start_angle + angle/2)
            label_radius = radius * 1.2
            label_x = center_x + math.cos(label_angle) * label_radius
            label_y = center_y - math.sin(label_angle) * label_radius
            
            if i < len(self.labels):
                # Draw label background for better readability
                text = f"{self.labels[i]}\n{value/total*100:.1f}%"
                
                # Create label background
                bbox = self.canvas.create_text(
                    label_x, label_y,
                    text=text,
                    font=self.style.LABEL_FONT,
                    fill=self.style.TEXT,
                    justify=tk.CENTER,
                    tags=('label',)
                )
                
                # Get bbox coordinates
                bbox = self.canvas.bbox(bbox)
                padding = 4
                
                # Draw label background
                self.canvas.create_rectangle(
                    bbox[0] - padding,
                    bbox[1] - padding,
                    bbox[2] + padding,
                    bbox[3] + padding,
                    fill=self.style.BACKGROUND,
                    outline="",
                    tags=('label_bg',)
                )
                
                # Redraw text over background
                self.canvas.create_text(
                    label_x, label_y,
                    text=text,
                    font=self.style.LABEL_FONT,
                    fill=self.style.TEXT,
                    justify=tk.CENTER,
                    tags=('label',)
                )
            
            start_angle += angle
            
        # Bring labels to front
        self.canvas.tag_raise('label_bg')
        self.canvas.tag_raise('label')
        
        # Add hover effect
        self._add_hover_effect()
        
    def _add_hover_effect(self):
        tooltip, label = self._create_tooltip()
        
        def on_enter(event):
            # Find which slice was hovered
            x = event.x - self.width // 2
            y = self.height // 2 - event.y
            angle = math.degrees(math.atan2(y, x))
            if angle < 0:
                angle += 360
                
            # Calculate which slice this angle corresponds to
            current_angle = 0
            total = sum(self.data)
            
            for i, value in enumerate(self.data):
                slice_angle = value / total * 360
                if current_angle <= angle < current_angle + slice_angle:
                    # Update tooltip
                    if i < len(self.labels):
                        text = f"{self.labels[i]}\nValue: {value:,.0f}\n{value/total*100:.1f}%"
                        label.config(text=text)
                        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                        tooltip.deiconify()
                    break
                current_angle += slice_angle
                
        def on_leave(event):
            tooltip.withdraw()
            
        self.canvas.bind('<Motion>', on_enter)
        self.canvas.bind('<Leave>', on_leave)

# Example usage
if __name__ == "__main__":
    line_chart = LineChart(width=800, height=600, display_mode='window')
    line_chart.plot([10, 20, 30, 40, 50])
    line_chart.show()

    bar_chart = BarChart(width=800, height=600, display_mode='window')
    bar_chart.plot([10, 20, 30, 40, 50])
    bar_chart.show()

    pie_chart = PieChart(width=800, height=600, display_mode='window')
    pie_chart.plot([10, 20, 30, 40], ['A', 'B', 'C', 'D'])
    pie_chart.show()
