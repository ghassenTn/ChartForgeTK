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


from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle
class BubbleChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of (x, y, size) tuples
        self.min_radius = 5
        self.max_radius = 30
        self.animation_duration = 500
        self.bubbles = []  # Store canvas items
        
    def plot(self, data: List[Tuple[float, float, float]]):
        """Plot the bubble chart with (x, y, size) data"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(p, tuple) and len(p) == 3 and 
                  all(isinstance(v, (int, float)) for v in p) for p in data):
            raise TypeError("Data must be a list of (x, y, size) number tuples")
        if any(p[2] < 0 for p in data):
            raise ValueError("Bubble sizes cannot be negative")
            
        self.data = data
        
        
        # Calculate ranges
        x_values, y_values, sizes = zip(*data)
        self.x_min, self.x_max = min(x_values), max(x_values)
        self.y_min, self.y_max = min(y_values), max(y_values)
        size_min, size_max = min(sizes), max(sizes)
        x_padding = (self.x_max - self.x_min) * 0.1 or 1
        y_padding = (self.y_max - self.y_min) * 0.1 or 1
        self.x_min -= x_padding
        self.x_max += x_padding
        self.y_min -= y_padding
        self.y_max += y_padding
        self.size_min, self.size_max = size_min, size_max
        
        # Set labels
        self.title = "Bubble Chart"
        self.x_label = "X Axis"
        self.y_label = "Y Axis"
        
        self.canvas.delete('all')
        self.bubbles.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_bubbles()
        self._add_interactive_effects()

    def _animate_bubbles(self):
        """Draw bubbles with smooth size animation"""
        def ease(t):
            return t * t * (3 - 2 * t)
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            for item in self.bubbles:
                self.canvas.delete(item)
            self.bubbles.clear()
            
            for i, (x, y, size) in enumerate(self.data):
                px = self._data_to_pixel_x(x, self.x_min, self.x_max)
                py = self._data_to_pixel_y(y, self.y_min, self.y_max)
                # Scale radius based on size
                if self.size_max == self.size_min:
                    radius = self.min_radius
                else:
                    radius = self.min_radius + (self.max_radius - self.min_radius) * \
                            (size - self.size_min) / (self.size_max - self.size_min)
                radius *= progress
                
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Shadow
                shadow = self.canvas.create_oval(
                    px - radius + 2, py - radius + 2,
                    px + radius + 2, py + radius + 2,
                    fill=self.style.create_shadow(color),
                    outline="",
                    tags=('shadow', f'bubble_{i}')
                )
                self.bubbles.append(shadow)
                
                # Bubble
                bubble = self.canvas.create_oval(
                    px - radius, py - radius,
                    px + radius, py + radius,
                    fill=color,
                    outline=self.style.adjust_brightness(color, 0.8),
                    tags=('bubble', f'bubble_{i}')
                )
                self.bubbles.append(bubble)
                
                if progress == 1:
                    label = self.canvas.create_text(
                        px, py - radius - 10,
                        text=f"({x:.1f}, {y:.1f}, {size:.1f})",
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='s',
                        tags=('label', f'bubble_{i}')
                    )
                    self.bubbles.append(label)
            
            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)
        
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
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        current_highlight = None
        
        def on_motion(event):
            nonlocal current_highlight
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                closest_idx = -1
                min_dist = float('inf')
                
                for i, (dx, dy, size) in enumerate(self.data):
                    px = self._data_to_pixel_x(dx, self.x_min, self.x_max)
                    py = self._data_to_pixel_y(dy, self.y_min, self.y_max)
                    radius = self.min_radius + (self.max_radius - self.min_radius) * \
                            (size - self.size_min) / (self.size_max - self.size_min) if self.size_max != self.size_min else self.min_radius
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist and dist < radius + 10:  # Within bubble radius + buffer
                        min_dist = dist
                        closest_idx = i
                
                if closest_idx >= 0:
                    px = self._data_to_pixel_x(self.data[closest_idx][0], self.x_min, self.x_max)
                    py = self._data_to_pixel_y(self.data[closest_idx][1], self.y_min, self.y_max)
                    radius = self.min_radius + (self.max_radius - self.min_radius) * \
                            (self.data[closest_idx][2] - self.size_min) / (self.size_max - self.size_min) if self.size_max != self.size_min else self.min_radius
                    
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    highlight = self.canvas.create_oval(
                        px - radius * 1.2, py - radius * 1.2,
                        px + radius * 1.2, py + radius * 1.2,
                        outline=self.style.ACCENT, width=2, tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    x_val, y_val, size_val = self.data[closest_idx]
                    label.config(text=f"X: {x_val:.1f}\nY: {y_val:.1f}\nSize: {size_val:.1f}")
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