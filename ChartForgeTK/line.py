from typing import List, Optional, Union, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart , ChartStyle
class LineChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.points = []
        self.line_width = 1
        self.dot_radius = 3
        self.animation_duration = 500

    def _clamp_color(self, color: str) -> str:
        """Ensure a hex color is valid by clamping RGB values between 0 and 255."""
        if not color.startswith('#') or len(color) != 7:
            return "#000000"  # Fallback to black if invalid
        try:
            r = max(0, min(255, int(color[1:3], 16)))
            g = max(0, min(255, int(color[3:5], 16)))
            b = max(0, min(255, int(color[5:7], 16)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            return "#000000"
        
    def plot(self, data: List[float]):
        """Plot the line chart with the given data"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
            
        self.data = data
        
        # Calculate data ranges
        x_min, x_max = 0, len(data) - 1
        y_min, y_max = min(data), max(data)
        padding = (y_max - y_min) * 0.1 or 1  # Avoid zero padding
        y_min -= padding
        y_max += padding
        
        # Clear previous content
        self.canvas.delete('all')
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Calculate points
        self.points = []
        for i, y in enumerate(data):
            x = self._data_to_pixel_x(i, x_min, x_max)
            y = self._data_to_pixel_y(y, y_min, y_max)
            self.points.append((x, y))
        
        # Animate the line drawing
        self._animate_line(y_min, y_max)
        self._add_interactive_effects()

    def _animate_line(self, y_min: float, y_max: float):
        """Draw the line with smooth animation"""
        line = self.canvas.create_line(
            self.points[0][0], self.points[0][1], self.points[0][0], self.points[0][1],
            fill=self.style.ACCENT,
            width=self.line_width,
            tags=('line',)
        )
        
        shadow = self.canvas.create_line(
            self.points[0][0], self.points[0][1], self.points[0][0], self.points[0][1],
            fill=self.style.create_shadow(self.style.ACCENT),
            width=self.line_width + 2,
            tags=('shadow',)
        )
        
        dots = []
        labels = []
        
        def ease(t):
            return t * t * (3 - 2 * t)
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            current_points = []
            
            for i in range(len(self.points)):
                x0, y0 = self.points[max(0, i-1)]
                x1, y1 = self.points[i]
                if i == 0:
                    current_points.extend([x1, y1])
                else:
                    interp_x = x0 + (x1 - x0) * min(1.0, progress * len(self.points) / (i + 1))
                    interp_y = y0 + (y1 - y0) * min(1.0, progress * len(self.points) / (i + 1))
                    current_points.extend([interp_x, interp_y])
                
                if i < len(dots) and progress * len(self.points) >= i + 1:
                    self.canvas.coords(dots[i], 
                                     x1 - self.dot_radius, y1 - self.dot_radius,
                                     x1 + self.dot_radius, y1 + self.dot_radius)
                    self.canvas.coords(labels[i], x1, y1 - 15)
                    self.canvas.itemconfig(dots[i], state='normal')
                    self.canvas.itemconfig(labels[i], state='normal')
            
            # self.canvas.coords(line, *current_points)
            self.canvas.coords(shadow, *current_points)
            
            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)
            else:
                for i, (x, y) in enumerate(self.points):
                    if i >= len(dots):
                        # Clamp the colors to ensure validity
                        fill_color = self._clamp_color(self.style.adjust_brightness(self.style.ACCENT, 1.2))
                        outline_color = self._clamp_color(self.style.adjust_brightness(self.style.ACCENT, 0.8))
                        
                        dot = self.canvas.create_oval(
                            x - self.dot_radius, y - self.dot_radius,
                            x + self.dot_radius, y + self.dot_radius,
                            fill=fill_color,
                            outline=outline_color,
                            tags=('dot', f'point_{i}')
                        )
                        label = self.canvas.create_text(
                            x, y - 15,
                            text=f"{self.data[i]:,.2f}",
                            font=self.style.VALUE_FONT,
                            fill=self.style.TEXT,
                            anchor='s',
                            tags=('label', f'point_{i}')
                        )
                        dots.append(dot)
                        labels.append(label)
        
        total_frames = self.animation_duration // 16
        update_animation(0, total_frames)

    def _add_interactive_effects(self):
        """Add hover effects and tooltips"""
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)
        
        tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        label = ttk.Label(tooltip_frame, 
                         style='Tooltip.TLabel',
                         font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        style = ttk.Style()
        style.configure('Tooltip.TFrame', 
                       background=self.style.TEXT,
                       relief='solid',
                       borderwidth=0)
        style.configure('Tooltip.TLabel',
                       background=self.style.TEXT,
                       foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        current_highlight = None
        
        def on_motion(event):
            nonlocal current_highlight
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding:
                # Find nearest point
                closest_idx = -1
                min_dist = float('inf')
                
                for i, (px, py) in enumerate(self.points):
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist and dist < 20:  # 20 pixel radius
                        min_dist = dist
                        closest_idx = i
                
                if closest_idx >= 0:
                    px, py = self.points[closest_idx]
                    
                    # Remove previous highlight
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    # Create highlight effect
                    highlight = self.canvas.create_oval(
                        px - self.dot_radius * 1.5,
                        py - self.dot_radius * 1.5,
                        px + self.dot_radius * 1.5,
                        py + self.dot_radius * 1.5,
                        outline=self.style.ACCENT,
                        width=2,
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    # Update tooltip
                    value = self.data[closest_idx]
                    label.config(text=f"Index: {closest_idx}\nValue: {value:,.2f}")
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                    tooltip.deiconify()
                    tooltip.lift()
                else:
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                        current_highlight = None
                    tooltip.withdraw()
        
        def on_leave(event):
            nonlocal current_highlight
            if current_highlight:
                self.canvas.delete(current_highlight)
                current_highlight = None
            tooltip.withdraw()
        
        self.canvas.bind('<Motion>', on_motion)
        self.canvas.bind('<Leave>', on_leave)

# Usage example:
"""
chart = LineChart()
chart.plot([10, 15, 13, 18, 16, 20])
"""