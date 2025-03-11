import math
from typing import List, Optional, Union, Tuple
import colorsys
import tkinter as tk
from tkinter import ttk, font
# import ttkbootstrap as ttkbs
class ChartStyle:
    def __init__(self, theme='light'):
        self.theme = theme
        if theme == 'light':
            self.BACKGROUND = "#FFFFFF"  # Clean, crisp white
            self.TEXT = "#1E293B"        # Deep slate gray for strong contrast
            self.TEXT_SECONDARY = "#64748B"  # Soft gray-blue for secondary text
            self.PRIMARY = "#2563EB"     # Bold modern blue
            self.ACCENT = "#FACC15"      # Bright yellow-gold for highlights
            self.AXIS_COLOR = "#94A3B8"  # Muted blue-gray for axes
            self.GRID_COLOR = "#E2E8F0"  # Soft light gray for subtle grids
            self.TICK_COLOR = "#64748B"  # Subtle gray-blue for ticks
            self.SECONDARY = "#38BDF8"   # Fresh cyan-blue for contrast
            self.ACCENT_HOVER = "#FB923C"  # Soft orange for interactive elements
            
        else:  # dark
            self.BACKGROUND = "#0F172A"  # Deep navy for a sleek dark theme
            self.TEXT = "#E2E8F0"        # Light gray for text clarity
            self.TEXT_SECONDARY = "#94A3B8"  # Muted blue-gray for balance
            self.PRIMARY = "#3B82F6"     # Bright blue with a modern touch
            self.ACCENT = "#EAB308"      # Neon gold for highlights
            self.AXIS_COLOR = "#475569"  # Darker gray-blue for soft contrast
            self.GRID_COLOR = "#334155"  # Dark gray-blue for subtle grid lines
            self.TICK_COLOR = "#94A3B8"  # Muted blue-gray for balance
            self.SECONDARY = "#22D3EE"   # Vibrant cyan for secondary elements
            self.ACCENT_HOVER = "#F87171"  # Coral red for hover interactions
        
        self.PADDING = 50
        self.AXIS_WIDTH = 2
        self.GRID_WIDTH = 1
        self.TICK_LENGTH = 5
        self.TITLE_FONT = ("Helvetica", 14, "bold")
        self.LABEL_FONT = ("Helvetica", 10)
        self.AXIS_FONT = ("Helvetica", 10)
        self.VALUE_FONT = ("Helvetica", 12)
        self.TOOLTIP_FONT = ("Helvetica", 10)
        self.TOOLTIP_PADDING = 5

    def get_gradient_color(self, index, total):
        # Updated modern gradient with bold yet refined colors
        colors = [
            "#2563EB",  # Deep blue
            "#FACC15",  # Vivid gold
            "#F43F5E",  # Bold pinkish red
            "#10B981",  # Bright green
            "#8B5CF6",  # Elegant violet
        ]
        return colors[index % len(colors)]

    def get_histogram_color(self, index, total):
        # Modernized, vibrant but deep blue
        colors = ["#2563EB"]  
        return colors[index % len(colors)]

    def create_shadow(self, color):
        return self.adjust_brightness(color, 0.7)

    def adjust_brightness(self, color, factor):
        r = max(0, min(255, int(int(color[1:3], 16) * factor)))
        g = max(0, min(255, int(int(color[3:5], 16) * factor)))
        b = max(0, min(255, int(int(color[5:7], 16) * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"


class Chart(tk.Frame):
    def __init__(self, parent=None, width: int = 400, height: int = 400, display_mode='frame', theme='light'):
        """Initialize chart with modern styling and enhanced features."""
        # Validate input parameters
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        if display_mode not in ['frame', 'window']:
            raise ValueError("Display mode must be either 'frame' or 'window'")
        if theme not in ['light', 'dark']:
            raise ValueError("Theme must be either 'light' or 'dark'")

        self.style = ChartStyle(theme=theme)  # Pass theme to ChartStyle
        self.theme = theme
        self.display_mode = display_mode
        self.width = width
        self.height = height
        self.padding = self.style.PADDING
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.is_maximized = False
        self.original_geometry = None
        self._tooltip = None
        self._tooltip_label = None
        self._hover_tag = None
        self._click_callback = None
        # Add range variables for interactivity
        self.x_min = self.x_max = self.y_min = self.y_max = 0

        if display_mode == 'window':
            self._initialize_window()

        super().__init__(parent)
        self._initialize_canvas()

    def _initialize_window(self):
        """Initialize window mode with modern controls."""
        self.window = tk.Toplevel()
        self.window.title("Chart View")
        self.window.configure(background=self.style.BACKGROUND)

        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill='x', padx=1, pady=1)

        style = ttk.Style()
        style.configure('WindowControl.TButton',
                       padding=4,
                       relief='flat',
                       background=self.style.BACKGROUND,
                       foreground=self.style.TEXT,
                       font=('Helvetica', 12))
        style.map('WindowControl.TButton',
                 background=[('active', self.style.PRIMARY)],
                 foreground=[('active', self.style.BACKGROUND)])

        close_btn = ttk.Button(control_frame, text="×", width=3,
                              style='WindowControl.TButton', command=self.window.destroy)
        close_btn.pack(side='right', padx=1)

        self.maximize_btn = ttk.Button(control_frame, text="□", width=3,
                                      style='WindowControl.TButton', command=self._toggle_maximize)
        self.maximize_btn.pack(side='right', padx=1)

        minimize_btn = ttk.Button(control_frame, text="_", width=3,
                                 style='WindowControl.TButton', command=lambda: self.window.iconify())
        minimize_btn.pack(side='right', padx=1)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        self.window.bind("<Configure>", self._on_window_configure)

    def _initialize_canvas(self):
        """Initialize the canvas with modern styling."""
        self.canvas = tk.Canvas(self, width=self.width, height=self.height,
                               background=self.style.BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Button-1>", self._on_mouse_click)

    def _toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if not self.is_maximized:
            self.original_geometry = self.window.geometry()
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")
            self.maximize_btn.configure(text="❐")
            self.is_maximized = True
        else:
            if self.original_geometry:
                self.window.geometry(self.original_geometry)
            self.maximize_btn.configure(text="□")
            self.is_maximized = False

    def _on_window_configure(self, event):
        """Handle window resize events."""
        if event.widget == self.window:
            self.width = event.width - 20
            self.height = event.height - 20
            self.canvas.configure(width=self.width, height=self.height)
            self.redraw()

    def _on_mouse_move(self, event):
        """Handle mouse move events for hover effects."""
        if self._tooltip:
            self._tooltip.withdraw()
        self._hover_tag = self._get_hovered_element(event.x, event.y)
        if self._hover_tag:
            self._show_tooltip(event.x_root, event.y_root, self._hover_tag)

    def _on_mouse_leave(self, event):
        """Handle mouse leave events."""
        if self._tooltip:
            self._tooltip.withdraw()
        self._hover_tag = None

    def _on_mouse_click(self, event):
        """Handle mouse click events."""
        if self._click_callback and self._hover_tag:
            self._click_callback(self._hover_tag)

    def _get_hovered_element(self, x: int, y: int) -> Optional[str]:
        """Get the hovered chart element (e.g., bar, point)."""
        return None  # Child classes override this


    def redraw(self):
        """Redraw the chart with current data."""
        self.clear()
        if hasattr(self, 'data'):
            if hasattr(self, 'redraw_chart'):
                self.redraw_chart()
            else:
                self.plot(self.data)

    def clear(self):
        """Clear the canvas."""
        self.canvas.delete("all")

    def show(self):
        """Display the chart in window mode."""
        if self.display_mode == 'window':
            self.window.mainloop()

    def to_window(self):
        """Convert the chart to a separate window."""
        if self.display_mode != 'window':
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)

            new_chart = self.__class__(width=self.width, height=self.height, display_mode='window', theme=self.theme)
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label

            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            return new_chart

    def to_frame(self, parent):
        """Convert the chart to an embedded frame."""
        if self.display_mode != 'frame':
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)

            new_chart = self.__class__(parent=parent, width=self.width, height=self.height, 
                                      display_mode='frame', theme=self.theme)
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label

            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            return new_chart

    def _draw_axes(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw beautiful axes with grid lines, storing ranges for interactivity."""
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

        self._draw_grid(x_min, x_max, y_min, y_max)

        # Y-axis (left edge)
        self.canvas.create_line(
            self.padding, self.padding,
            self.padding, self.height - self.padding,
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )

        # X-axis (at y=0 or bottom if no zero)
        y_zero = 0 if y_min <= 0 <= y_max else y_min
        self.canvas.create_line(
            self.padding, self._data_to_pixel_y(y_zero, y_min, y_max),
            self.width - self.padding, self._data_to_pixel_y(y_zero, y_min, y_max),
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )

        self._draw_ticks(x_min, x_max, y_min, y_max)

        if self.title:
            self.canvas.create_text(
                self.width / 2, self.padding / 2, text=self.title,
                font=self.style.TITLE_FONT, fill=self.style.TEXT, anchor='center'
            )

        if self.x_label:
            self.canvas.create_text(
                self.width / 2, self.height - self.padding / 3, text=self.x_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center'
            )

        if self.y_label:
            self.canvas.create_text(
                self.padding / 3, self.height / 2, text=self.y_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center', angle=90
            )

    def _draw_grid(self, x_min, x_max, y_min, y_max):
        """Draw subtle grid lines."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        x = math.ceil(x_min / x_interval) * x_interval
        while x <= x_max:
            px = self._data_to_pixel_x(x, x_min, x_max)
            self.canvas.create_line(px, self.padding, px, self.height - self.padding,
                                   fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(2, 4))
            x += x_interval

        y = math.ceil(y_min / y_interval) * y_interval
        while y <= y_max:
            py = self._data_to_pixel_y(y, y_min, y_max)
            self.canvas.create_line(self.padding, py, self.width - self.padding, py,
                                   fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(2, 4))
            y += y_interval

    def _draw_ticks(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw axis ticks and labels with modern styling, preventing duplicates."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        # X-axis ticks and labels
        x = math.ceil(x_min / x_interval) * x_interval
        y_zero = 0 if y_min <= 0 <= y_max else y_min
        drawn_x_labels = set()  # Track drawn X labels to avoid duplicates
        while x <= x_max + 1e-10:  # Add small epsilon to handle floating-point edge cases
            px = self._data_to_pixel_x(x, x_min, x_max)
            py = self._data_to_pixel_y(y_zero, y_min, y_max)
            self.canvas.create_line(px, py, px, py + self.style.TICK_LENGTH,
                                   fill=self.style.TICK_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND)
            label = f"{x:g}"
            if label not in drawn_x_labels:
                self.canvas.create_text(px, py + self.style.TICK_LENGTH + 5, text=label,
                                       font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='n')
                drawn_x_labels.add(label)
            x += x_interval

        # Y-axis ticks and labels
        y = math.ceil(y_min / y_interval) * y_interval
        drawn_y_labels = set()  # Track drawn Y labels to avoid duplicates
        while y <= y_max + 1e-10:  # Add small epsilon to handle floating-point edge cases
            px = self.padding
            py = self._data_to_pixel_y(y, y_min, y_max)
            self.canvas.create_line(px - self.style.TICK_LENGTH, py, px, py,
                                   fill=self.style.TICK_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND)
            label = f"{y/1000:g}k" if abs(y) >= 1000 else f"{y:g}"
            if label not in drawn_y_labels and abs(py - self.height / 2) > 10:  # Avoid overlap near center
                self.canvas.create_text(px - self.style.TICK_LENGTH - 5, py, text=label,
                                       font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='e')
                drawn_y_labels.add(label)
            y += y_interval

    def _data_to_pixel_x(self, x: float, x_min: float, x_max: float) -> float:
        """Convert data coordinate to pixel coordinate for x-axis."""
        if x_max == x_min:
            return self.padding
        return self.padding + (x - x_min) * (self.width - 2 * self.padding) / (x_max - x_min)

    def _data_to_pixel_y(self, y: float, y_min: float, y_max: float) -> float:
        """Convert data coordinate to pixel coordinate for y-axis."""
        if y_max == y_min:
            return self.height - self.padding
        return self.height - self.padding - (y - y_min) * (self.height - 2 * self.padding) / (y_max - y_min)

    def _calculate_tick_interval(self, range: float) -> float:
        """Calculate a nice tick interval based on the range, aiming for 5-10 ticks."""
        if range == 0:
            return 1
        # Target 5-10 ticks across the range
        magnitude = math.pow(10, math.floor(math.log10(range)))
        normalized_range = range / magnitude
        if normalized_range <= 2:
            interval = magnitude / 5  # e.g., 0.2 for range 1-2
        elif normalized_range <= 5:
            interval = magnitude / 2  # e.g., 0.5 for range 2-5
        else:
            interval = magnitude      # e.g., 1 for range 5-10+
        return interval

    
