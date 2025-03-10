from typing import List, Optional, Union, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart,ChartStyle
class PieChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.radius = min(width, height) * 0.35  # 70% of smallest dimension
        self.center_x = width / 2
        self.center_y = height / 2
        self.animation_duration = 500  # ms
        
    def plot(self, data: List[float], labels: Optional[List[str]] = None):
        """Plot the pie chart with the given data and optional labels"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        if any(x < 0 for x in data):
            raise ValueError("Pie chart data cannot contain negative values")
        if labels and len(labels) != len(data):
            raise ValueError("Number of labels must match number of data points")
            
        self.data = data
        self.labels = labels or [f"Slice {i}" for i in range(len(data))]
        self.total = sum(data)
        
        # Clear previous content
        self.canvas.delete('all')
        
        # Animate the pie chart drawing
        self._animate_pie()
        self._add_interactive_effects()

    def _animate_pie(self):
        """Draw the pie chart with smooth animation"""
        def ease(t):
            return t * t * (3 - 2 * t)  # Ease-in-out
        
        slices = []
        label_items = []
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            current_angle = 0
            
            # Clear previous slices
            for item in slices:
                self.canvas.delete(item)
            slices.clear()
            
            for i, value in enumerate(self.data):
                # Calculate slice angle
                angle = (value / self.total) * 2 * math.pi * progress
                end_angle = current_angle + angle
                
                # Calculate coordinates
                x0 = self.center_x
                y0 = self.center_y
                x1 = self.center_x + self.radius * math.cos(current_angle)
                y1 = self.center_y - self.radius * math.sin(current_angle)
                x2 = self.center_x + self.radius * math.cos(end_angle)
                y2 = self.center_y - self.radius * math.sin(end_angle)
                
                # Get color with gradient
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Draw slice shadow
                shadow = self.canvas.create_arc(
                    self.center_x - self.radius + 3,
                    self.center_y - self.radius + 3,
                    self.center_x + self.radius + 3,
                    self.center_y + self.radius + 3,
                    start=math.degrees(current_angle),
                    extent=math.degrees(angle),
                    fill=self.style.create_shadow(color),
                    outline="",
                    style=tk.PIESLICE,
                    tags=('shadow', f'slice_{i}')
                )
                slices.append(shadow)
                
                # Draw slice
                slice_item = self.canvas.create_arc(
                    self.center_x - self.radius,
                    self.center_y - self.radius,
                    self.center_x + self.radius,
                    self.center_y + self.radius,
                    start=math.degrees(current_angle),
                    extent=math.degrees(angle),
                    fill=color,
                    outline=self.style.adjust_brightness(color, 0.8),
                    width=1,
                    style=tk.PIESLICE,
                    tags=('slice', f'slice_{i}')
                )
                slices.append(slice_item)
                
                # Add label when slice is fully drawn
                if progress == 1 and i >= len(label_items):
                    mid_angle = current_angle + angle / 2
                    label_radius = self.radius * 1.2
                    lx = self.center_x + label_radius * math.cos(mid_angle)
                    ly = self.center_y - label_radius * math.sin(mid_angle)
                    
                    # Calculate percentage
                    percentage = (value / self.total) * 100
                    label_text = f"{self.labels[i]}\n{percentage:.1f}%"
                    
                    label = self.canvas.create_text(
                        lx, ly,
                        text=label_text,
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        justify='center',
                        tags=('label', f'slice_{i}')
                    )
                    label_items.append(label)
                
                current_angle = end_angle
            
            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)
        
        total_frames = self.animation_duration // 16  # ~60 FPS
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
            
            # Calculate angle from center
            dx = x - self.center_x
            dy = -(y - self.center_y)  # Invert y for canvas coordinates
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= self.radius:
                angle = math.atan2(dy, dx) % (2 * math.pi)
                current_angle = 0
                
                for i, value in enumerate(self.data):
                    slice_angle = (value / self.total) * 2 * math.pi
                    if current_angle <= angle < current_angle + slice_angle:
                        # Remove previous highlight
                        if current_highlight:
                            self.canvas.delete(current_highlight)
                        
                        # Create highlight effect (slightly larger slice)
                        highlight = self.canvas.create_arc(
                            self.center_x - self.radius * 1.1,
                            self.center_y - self.radius * 1.1,
                            self.center_x + self.radius * 1.1,
                            self.center_y + self.radius * 1.1,
                            start=math.degrees(current_angle),
                            extent=math.degrees(slice_angle),
                            outline=self.style.ACCENT,
                            width=2,
                            style=tk.PIESLICE,
                            tags=('highlight',)
                        )
                        current_highlight = highlight
                        
                        # Update tooltip
                        percentage = (value / self.total) * 100
                        label.config(text=f"{self.labels[i]}\nValue: {value:,.2f}\n{percentage:.1f}%")
                        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                        tooltip.deiconify()
                        tooltip.lift()
                        break
                    current_angle += slice_angle
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
chart = PieChart()
data = [30, 20, 15, 35]
labels = ["A", "B", "C", "D"]
chart.plot(data, labels)
"""