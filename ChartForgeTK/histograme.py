from typing import List
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle

class Histogram(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # Single list of values
        self.bins = 10  # Default number of bins
        self.animation_duration = 500
        self.bars = []  # Store canvas items
        
    def plot(self, data: List[float], bins: int = 10):
        """Plot a true histogram with the given data and number of bins"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("Data must be a list of numbers")
        if bins <= 0:
            raise ValueError("Number of bins must be positive")
            
        self.data = data
        self.bins = bins
        
        # Calculate bins and frequencies
        self.x_min, self.x_max = min(data), max(data)
        bin_width = (self.x_max - self.x_min) / bins if self.x_max > self.x_min else 1
        self.bin_edges = [self.x_min + i * bin_width for i in range(bins + 1)]
        self.frequencies = [0] * bins
        for value in data:
            # Handle edge case where value equals x_max
            bin_index = min(int((value - self.x_min) / bin_width), bins - 1)
            self.frequencies[bin_index] += 1
        self.y_min, self.y_max = 0, max(self.frequencies) if self.frequencies else 1
        
        # Add padding
        x_padding = (self.x_max - self.x_min) * 0.1 or 1
        y_padding = (self.y_max - self.y_min) * 0.1 or 1
        self.x_min -= x_padding
        self.x_max += x_padding
        self.y_max += y_padding
        
        # Set labels
        self.title = "Histogram"
        self.x_label = "Values"
        self.y_label = "Frequency"
        
        self.canvas.delete('all')
        self.bars.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_bars()
        self._add_interactive_effects()

    def _animate_bars(self):
        """Draw contiguous bars with smooth height animation"""
        def ease(t):
            return t * t * (3 - 2 * t)
        
        bar_width = (self.width - 2 * self.padding) / self.bins  # No gaps between bars
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            for item in self.bars:
                self.canvas.delete(item)
            self.bars.clear()
            
            for i, freq in enumerate(self.frequencies):
                x_left = self._data_to_pixel_x(self.bin_edges[i], self.x_min, self.x_max)
                x_right = self._data_to_pixel_x(self.bin_edges[i + 1], self.x_min, self.x_max)
                y_base = self._data_to_pixel_y(self.y_min, self.y_min, self.y_max)
                y_top = self._data_to_pixel_y(freq, self.y_min, self.y_max)
                y_current = y_base - (y_base - y_top) * progress
                
                color = self.style.get_gradient_color(i, self.bins)
                
                # Shadow (only if frequency > 0)
                if freq > 0:
                    shadow = self.canvas.create_rectangle(
                        x_left + 2, y_current + 2,
                        x_right + 2, y_base + 2,
                        fill=self.style.create_shadow(color),
                        outline="",
                        tags=('shadow', f'bar_{i}')
                    )
                    self.bars.append(shadow)
                
                    # Bar
                    bar = self.canvas.create_rectangle(
                        x_left, y_current,
                        x_right, y_base,
                        fill=color,
                        outline=self.style.adjust_brightness(color, 0.8),
                        tags=('bar', f'bar_{i}')
                    )
                    self.bars.append(bar)
                
                    if progress == 1 and freq > 0:
                        label = self.canvas.create_text(
                            (x_left + x_right) / 2, y_top - 10,
                            text=f"{freq}",
                            font=self.style.VALUE_FONT,
                            fill=self.style.TEXT,
                            anchor='s',
                            tags=('label', f'bar_{i}')
                        )
                        self.bars.append(label)
            
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
                bar_width = (self.width - 2 * self.padding) / self.bins
                bar_index = int((x - self.padding) / bar_width)
                
                if 0 <= bar_index < self.bins and self.frequencies[bar_index] > 0:
                    x_left = self._data_to_pixel_x(self.bin_edges[bar_index], self.x_min, self.x_max)
                    x_right = self._data_to_pixel_x(self.bin_edges[bar_index + 1], self.x_min, self.x_max)
                    y_base = self._data_to_pixel_y(self.y_min, self.y_min, self.y_max)
                    y_top = self._data_to_pixel_y(self.frequencies[bar_index], self.y_min, self.y_max)
                    
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    highlight = self.canvas.create_rectangle(
                        x_left - 2, y_top - 2,
                        x_right + 2, y_base + 2,
                        outline=self.style.ACCENT,
                        width=2,
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    label.config(text=f"Range: [{self.bin_edges[bar_index]:.1f}, {self.bin_edges[bar_index+1]:.1f})\nFrequency: {self.frequencies[bar_index]}")
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