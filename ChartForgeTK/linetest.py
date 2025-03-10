from typing import List, Optional, Dict, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
from core import Chart, ChartStyle

class EnhancedLineChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, 
                 display_mode='frame', theme='dark'):
        super().__init__(parent, width=width, height=height, 
                         display_mode=display_mode, theme=theme)
        self.series: List[Dict] = []
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.current_scale = 1.0
        self.hover_point = None
        self.padding = 50  # Added default padding value
        self._bind_events()
        self._setup_styles()
        
    def _setup_styles(self):
        self.default_colors = [
            '#4E79A7', '#F28E2B', '#E15759', '#76B7B2',
            '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7'
        ]
        self.configure(bg=self.style.BACKGROUND)
        self.tooltip_font = ('Arial', 10, 'bold')
        self.line_width = 2
        self.dot_radius = 4
        self.animation_duration = 500  # milliseconds
        
    def _bind_events(self):
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._on_pan)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Configure>", self._on_resize)
        # Bind click on data points for details popup
        self.canvas.tag_bind('data_point', '<Button-1>', self._on_data_point_click)

    def add_series(self, data: List[float], name: str = "", 
                   color: str = None, line_style: str = 'solid'):
        """Add a data series with customization options."""
        # Cycle through default colors if none provided or invalid
        color = color or self.default_colors[len(self.series) % len(self.default_colors)]
        self.series.append({
            'data': data,
            'name': name,
            'color': self._validate_color(color),
            'line_style': line_style,
            'visible': True
        })
        self._redraw()

    def _validate_color(self, color: str) -> str:
        """Ensure valid hex color format using regex."""
        if re.fullmatch(r'#[0-9A-Fa-f]{6}', color):
            return color
        # Fallback to a color based on the series index
        return self.default_colors[len(self.series) % len(self.default_colors)]

    def _redraw(self):
        """Redraw the entire chart with current settings."""
        self.canvas.delete('all')
        if not self.series:
            return
            
        self._calculate_scaling()
        self._draw_grid()
        self._draw_axes()
        self._draw_legend()
        
        for idx, series in enumerate(self.series):
            if series['visible']:
                self._draw_series(series, idx)

    def _calculate_scaling(self):
        """Calculate data ranges and scaling factors."""
        all_data = [point for series in self.series for point in series['data']]
        self.x_min = 0
        self.x_max = max(len(series['data']) - 1 for series in self.series)
        self.y_min = min(all_data)
        self.y_max = max(all_data)
        
        # Add 10% vertical padding
        y_padding = (self.y_max - self.y_min) * 0.1
        self.y_min -= y_padding
        self.y_max += y_padding
        
        # Calculate scaling factors based on canvas size and padding
        self.x_scale = (self.width - 2 * self.padding) / (self.x_max - self.x_min) if self.x_max - self.x_min != 0 else 1
        self.y_scale = (self.height - 2 * self.padding) / (self.y_max - self.y_min) if self.y_max - self.y_min != 0 else 1

    def _draw_grid(self):
        """Draw background grid with adaptive spacing."""
        x_step = (self.x_max - self.x_min) / 10
        y_step = (self.y_max - self.y_min) / 10
        
        for i in range(11):
            # Vertical grid lines
            x = self.x_min + i * x_step
            px = self.padding + (x - self.x_min) * self.x_scale
            self.canvas.create_line(px, self.padding, px, self.height - self.padding, 
                                    fill=self.style.SECONDARY, tags='grid')
            # Horizontal grid lines
            y = self.y_min + i * y_step
            py = self.height - self.padding - (y - self.y_min) * self.y_scale
            self.canvas.create_line(self.padding, py, self.width - self.padding, py, 
                                    fill=self.style.SECONDARY, tags='grid')

    def _draw_axes(self):
        """Draw X and Y axes with labels."""
        # X axis
        self.canvas.create_line(
            self.padding, self.height - self.padding,
            self.width - self.padding, self.height - self.padding,
            fill=self.style.TEXT, width=2
        )
        # Y axis
        self.canvas.create_line(
            self.padding, self.padding,
            self.padding, self.height - self.padding,
            fill=self.style.TEXT, width=2
        )

    def _draw_series(self, series: Dict, series_idx: int):
        """Draw a single data series with animation."""
        points = []
        for i, y in enumerate(series['data']):
            # Convert data coordinates to canvas pixels
            x = self.padding + i * self.x_scale
            py = self.height - self.padding - (y - self.y_min) * self.y_scale
            points.extend([x, py])
            
            # Draw data point (circle) with binding for click events
            self.canvas.create_oval(
                x - self.dot_radius, py - self.dot_radius,
                x + self.dot_radius, py + self.dot_radius,
                fill=series['color'], outline=series['color'],
                tags=('data_point', f'series_{series_idx}')
            )

        # Animated line drawing if animation_duration > 0
        if self.animation_duration > 0:
            self._animate_series_line(points, series, series_idx)
        else:
            self.canvas.create_line(
                *points, fill=series['color'], width=self.line_width,
                dash=self._get_dash_style(series['line_style']),
                tags=('line', f'series_{series_idx}')
            )

    def _animate_series_line(self, points: List[float], series: Dict, series_idx: int):
        total_points = len(points) // 2
        # If only one point is provided, draw a degenerate line.
        if total_points < 2:
            self.canvas.create_line(
                points[0], points[1], points[0], points[1],
                fill=series['color'], width=self.line_width,
                dash=self._get_dash_style(series['line_style']),
                tags=('line', f'series_{series_idx}')
            )
            return

        frames_per_segment = 20  # Number of frames between two data points
        total_segments = total_points - 1
        total_frames = total_segments * frames_per_segment

        # Create the initial line item (starting as a degenerate line at the first point)
        line_item = self.canvas.create_line(
            points[0], points[1], points[0], points[1],
            fill=series['color'], width=self.line_width,
            dash=self._get_dash_style(series['line_style']),
            tags=('line', f'series_{series_idx}')
        )
        
        def animate(frame: int):
            if frame > total_frames:
                # Final update: draw the complete line.
                self.canvas.coords(line_item, *points)
                return

            seg_index = frame // frames_per_segment  # which segment we are animating
            seg_frame = frame % frames_per_segment   # frame within the current segment

            coords = []
            # Append fully completed segments (each segment is a full point)
            for i in range(seg_index):
                coords.extend(points[i*2:(i*2)+2])
            
            # For the current segment, get its starting point.
            start_index = seg_index * 2
            x0, y0 = points[start_index], points[start_index+1]
            if seg_index < total_points - 1:
                # Next point in the series.
                x1, y1 = points[start_index+2], points[start_index+3]
                # Determine the fraction of the current segment to draw.
                fraction = seg_frame / frames_per_segment
                xi = x0 + fraction * (x1 - x0)
                yi = y0 + fraction * (y1 - y0)
                # Append the starting point and the interpolated point.
                coords.extend([x0, y0, xi, yi])
            else:
                # Last point reached.
                coords.extend([x0, y0])
            
            self.canvas.coords(line_item, *coords)
            delay = self.animation_duration // total_frames
            self.canvas.after(delay, lambda: animate(frame + 1))
        
        animate(1)

    def _get_dash_style(self, style: str) -> tuple:
        """Convert line style to canvas dash pattern."""
        return {
            'solid': (),
            'dashed': (6, 4),
            'dotted': (2, 2)
        }.get(style, ())

    def _draw_legend(self):
        """Draw interactive legend with toggle capability."""
        x_start = self.width - 150
        y_start = 20
        for idx, series in enumerate(self.series):
            color = series['color']
            # Legend item background
            self.canvas.create_rectangle(
                x_start - 5, y_start - 5, x_start + 155, y_start + 25,
                fill=self.style.BACKGROUND, outline=self.style.SECONDARY,
                tags=('legend', f'legend_{idx}')
            )
            # Color indicator
            self.canvas.create_rectangle(
                x_start, y_start, x_start + 20, y_start + 20,
                fill=color, tags=('legend', f'legend_{idx}')
            )
            # Series name
            self.canvas.create_text(
                x_start + 25, y_start + 10,
                text=series['name'], anchor='w',
                font=self.style.TOOLTIP_FONT,
                fill=self.style.TEXT,
                tags=('legend', f'legend_{idx}')
            )
            y_start += 30

        # Bind click event for legend items to toggle series visibility
        self.canvas.tag_bind('legend', '<Button-1>', self._toggle_series)

    def _toggle_series(self, event):
        """Toggle series visibility when clicking legend items."""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if len(tags) > 1 and tags[1].startswith('legend_'):
            series_idx = int(tags[1].split('_')[1])
            self.series[series_idx]['visible'] = not self.series[series_idx]['visible']
            self._redraw()

    def _inverse_scale(self, px: float, py: float) -> Tuple[float, float]:
        """Convert canvas coordinates (pixels) to data coordinates (X, Y values)."""
        x = self.x_min + (px - self.padding) / self.x_scale
        y = self.y_min + (self.height - py - self.padding) / self.y_scale
        return x, y

    def _clear_highlights(self):
        """Remove all highlight elements (circles, guide lines, etc.)."""
        self.canvas.delete('highlight')

    def _on_mouse_move(self, event):
        """Handle hover effects and tooltips."""
        x, y = self._inverse_scale(event.x, event.y)
        closest = self._find_closest_point(x, y)
        
        if closest:
            self._highlight_point(*closest)
            self._show_tooltip(event.x, event.y, *closest)
        else:
            self._clear_highlights()
            self._hide_tooltip()

    def _find_closest_point(self, x: float, y: float) -> Optional[Tuple]:
        """Find the closest data point to the mouse position."""
        min_dist = float('inf')
        closest = None
        for series_idx, series in enumerate(self.series):
            if not series['visible']:
                continue
            for i, py in enumerate(series['data']):
                # x coordinate in data space is just the index
                px = i
                dist = math.hypot((px - x) / self.x_scale, (py - y) / self.y_scale)
                if dist < min_dist and dist < 10:
                    min_dist = dist
                    closest = (series_idx, i, px, py)
        return closest

    def _highlight_point(self, series_idx: int, point_idx: int, x: float, y: float):
        """Highlight the closest data point."""
        self._clear_highlights()
        px = self.padding + x * self.x_scale
        py = self.height - self.padding - (y - self.y_min) * self.y_scale
        
        # Draw highlight circle
        self.canvas.create_oval(
            px - 6, py - 6, px + 6, py + 6,
            outline=self.style.ACCENT, width=2,
            tags='highlight'
        )
        # Draw vertical guide line
        self.canvas.create_line(
            px, self.padding, px, self.height - self.padding,
            fill=self.style.SECONDARY, dash=(2, 2),
            tags='highlight'
        )

    def _show_tooltip(self, x: int, y: int, series_idx: int, point_idx: int, val_x: float, val_y: float):
        """Show an interactive tooltip with data values."""
        self._hide_tooltip()
        series = self.series[series_idx]
        text = f"{series['name']}\nX: {val_x:.2f}\nY: {val_y:.2f}"
        
        # Tooltip background
        self.canvas.create_rectangle(
            x + 10, y - 10, x + 160, y + 40,
            fill=self.style.BACKGROUND, outline=self.style.ACCENT,
            tags='tooltip'
        )
        # Tooltip text
        self.canvas.create_text(
            x + 15, y - 5, text=text,
            anchor='nw', font=self.tooltip_font,
            fill=self.style.TEXT, tags='tooltip'
        )

    def _hide_tooltip(self):
        """Remove tooltip elements."""
        self.canvas.delete('tooltip')

    def _on_data_point_click(self, event):
        """Handle click event on a data point to show details."""
        x, y = self._inverse_scale(event.x, event.y)
        closest = self._find_closest_point(x, y)
        if closest:
            series_idx, point_idx, _, val_y = closest
            series = self.series[series_idx]
            messagebox.showinfo("Data Point Details", 
                                f"Series: {series['name']}\nIndex: {point_idx}\nValue: {val_y}")

    def _start_pan(self, event):
        """Begin panning operation."""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan(self, event):
        """Handle panning of the chart."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_zoom(self, event):
        """Handle zoom with mouse wheel."""
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_level *= scale_factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
        self._redraw()

    def _on_resize(self, event):
        """Handle window resize event."""
        self.width = event.width
        self.height = event.height
        self._redraw()

    def export_image(self, filename: str):
        """Export chart to image file.
        
        Exports as EPS and attempts to convert to PNG using Pillow.
        """
        self.postscript(file=f"{filename}.eps", colormode='color')
        try:
            from PIL import Image
            img = Image.open(f"{filename}.eps")
            img.save(f"{filename}.png", "png")
            print("Exported image as PNG.")
        except ImportError:
            print("Pillow is not installed. Only EPS export is available.")

import tkinter as tk
from tkinter import ttk
import turtle

# Assume EnhancedLineChart is already defined/imported from your module.
# from your_module import EnhancedLineChart

# Create the main tkinter window
root = tk.Tk()
root.title("Tkinter with Turtle Integration")

# Create a frame for the custom chart
chart_frame = ttk.Frame(root)
chart_frame.pack(side='left', fill='both', expand=True)

# Create a frame for the turtle canvas
turtle_frame = ttk.Frame(root)
turtle_frame.pack(side='right', fill='both', expand=True)

# Initialize your EnhancedLineChart in the chart_frame
chart = EnhancedLineChart(chart_frame, theme='dark')
chart.pack(fill='both', expand=True)

# Add sample series to the chart
chart.add_series(
    [10, 15, 13, 18, 16, 20, 22, 19, 25],
    name="Temperature",
    color="#FF6B6B",
    line_style='dashed'
)
chart.add_series(
    [5, 8, 14, 12, 10, 9, 11, 13, 12],
    name="Humidity",
    color="#4ECDC4",
    line_style='solid'
)

# Create a Canvas for Turtle inside turtle_frame
turtle_canvas = tk.Canvas(turtle_frame, width=400, height=400)
turtle_canvas.pack(fill='both', expand=True)

# Create a TurtleScreen on the tkinter Canvas
screen = turtle.TurtleScreen(turtle_canvas)
screen.bgcolor("white")

# Create a RawTurtle instance using the screen
t = turtle.RawTurtle(screen)
t.speed(1)
t.color("blue")
t.pensize(2)

# Draw a simple coordinate system using turtle
t.penup()
t.goto(-150, 0)
t.pendown()
t.goto(150, 0)  # X-axis
t.penup()
t.goto(0, -150)
t.pendown()
t.goto(0, 150)  # Y-axis

# Optionally, draw additional elements using turtle.
t.penup()
t.goto(-100, -100)
t.pendown()
t.write("Turtle Area", font=("Arial", 12, "normal"))

# Start the main event loop
root.mainloop()


