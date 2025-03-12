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


from typing import List, Optional, Union, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart
class BarChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
        self.bar_width_factor = 0.8  # Percentage of available space per bar
        self.animation_duration = 500  # ms
        self.bars = []  # Store bar references
        
    def plot(self, data: List[float], labels: Optional[List[str]] = None):
        """Plot the bar chart with the given data and optional labels"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        if any(x < 0 for x in data):
            raise ValueError("Bar chart data cannot contain negative values")
        if labels and len(labels) != len(data):
            raise ValueError("Number of labels must match number of data points")
            
        self.data = data
        self.labels = labels or [f"{i}" for i in range(len(data))]
        
        # Calculate ranges
        x_min, x_max = -0.5, len(data) - 0.5
        y_min, y_max = 0, max(data)
        padding = y_max * 0.1 or 1  # Avoid zero padding
        y_max += padding
        
        # Clear previous content
        self.canvas.delete('all')
        self.bars.clear()
        
        self._draw_axes(x_min, x_max, y_min, y_max)
        self._animate_bars(y_min, y_max)
        self._add_interactive_effects()

    def _animate_bars(self, y_min: float, y_max: float):
        """Draw bars with smooth height animation"""
        bar_spacing = (self.width - 2 * self.padding) / len(self.data)
        bar_width = bar_spacing * self.bar_width_factor
        
        def ease(t):
            return t * t * (3 - 2 * t)  # Ease-in-out
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            # Clear previous bars
            for item in self.bars:
                self.canvas.delete(item)
            self.bars.clear()
            
            for i, value in enumerate(self.data):
                x = self._data_to_pixel_x(i, -0.5, len(self.data) - 0.5)
                y_base = self._data_to_pixel_y(y_min, y_min, y_max)
                y_top = self._data_to_pixel_y(value, y_min, y_max)
                y_current = y_base - (y_base - y_top) * progress
                
                # Get color
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Draw shadow
                shadow = self.canvas.create_rectangle(
                    x - bar_width/2 + 3,
                    y_current + 3,
                    x + bar_width/2 + 3,
                    y_base + 3,
                    fill=self.style.create_shadow(color),
                    outline="",
                    tags=('shadow', f'bar_{i}')
                )
                self.bars.append(shadow)
                
                # Draw bar with gradient
                bar = self.canvas.create_rectangle(
                    x - bar_width/2,
                    y_current,
                    x + bar_width/2,
                    y_base,
                    fill=color,
                    outline=self.style.adjust_brightness(color, 0.8),
                    width=1,
                    tags=('bar', f'bar_{i}')
                )
                self.bars.append(bar)
                
                # Add label when fully drawn
                if progress == 1:
                    label = self.canvas.create_text(
                        x,
                        y_top - 10,
                        text=f"{self.labels[i]}\n{value:,.0f}",
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='s',
                        justify='center',
                        tags=('label', f'bar_{i}')
                    )
                    self.bars.append(label)
            
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
            x = event.x
            
            if self.padding <= x <= self.width - self.padding:
                bar_spacing = (self.width - 2 * self.padding) / len(self.data)
                bar_index = int((x - self.padding) / bar_spacing)
                
                if 0 <= bar_index < len(self.data):
                    # Calculate bar position
                    bar_x = self._data_to_pixel_x(bar_index, -0.5, len(self.data) - 0.5)
                    bar_width = bar_spacing * self.bar_width_factor
                    value = self.data[bar_index]
                    y_top = self._data_to_pixel_y(value, 0, max(self.data) * 1.1)
                    y_base = self._data_to_pixel_y(0, 0, max(self.data) * 1.1)
                    
                    # Remove previous highlight
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    # Create highlight effect
                    highlight = self.canvas.create_rectangle(
                        bar_x - bar_width/2 - 2,
                        y_top - 2,
                        bar_x + bar_width/2 + 2,
                        y_base + 2,
                        outline=self.style.ACCENT,
                        width=2,
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    # Update tooltip
                    label.config(text=f"{self.labels[bar_index]}\nValue: {value:,.0f}")
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
chart = BarChart()
data = [10, 20, 15, 25]
labels = ["A", "B", "C", "D"]
chart.plot(data, labels)
"""