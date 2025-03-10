from typing import List
import tkinter as tk
from tkinter import ttk, filedialog
import math
from .core import Chart, ChartStyle

class Histogram(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # Single list of values
        self.bins = 10  # Default number of bins
        self.animation_duration = 500
        self.bars = []  # Store canvas items
        self.tooltip = None
        self.current_highlight = None
        self.zoom_level = 1.0
        self.pan_offset = 0.0

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
        
        self._calculate_bins()
        self._add_padding()
        self._set_labels()
        
        self.canvas.delete('all')
        self.bars.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_bars()
        self._add_interactive_effects()
        # self._add_legend()
        self._add_statistics()
        # self._add_export_button()
        # self._add_theme_switch()

    def _calculate_bins(self):
        """Calculate bins and frequencies"""
        self.x_min, self.x_max = min(self.data), max(self.data)
        bin_width = (self.x_max - self.x_min) / self.bins if self.x_max > self.x_min else 1
        self.bin_edges = [self.x_min + i * bin_width for i in range(self.bins + 1)]
        self.frequencies = [0] * self.bins
        for value in self.data:
            bin_index = min(int((value - self.x_min) / bin_width), self.bins - 1)
            self.frequencies[bin_index] += 1
        self.y_min, self.y_max = 0, max(self.frequencies) if self.frequencies else 1

    def _add_padding(self):
        """Add padding to the axes"""
        x_padding = (self.x_max - self.x_min) * 0.1 or 1
        y_padding = (self.y_max - self.y_min) * 0.1 or 1
        self.x_min -= x_padding
        self.x_max += x_padding
        self.y_max += y_padding

    def _set_labels(self):
        """Set labels for the axes and title"""
        self.title = "Histogram"
        self.x_label = "Values"
        self.y_label = "Frequency"

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
                
                color = self.style.get_histogram_color(i, self.bins)
                
                if freq > 0:
                    shadow = self.canvas.create_rectangle(
                        x_left + 2, y_current + 2,
                        x_right + 2, y_base + 2,
                        fill=self.style.create_shadow(color),
                        outline="",
                        tags=('shadow', f'bar_{i}')
                    )
                    self.bars.append(shadow)
                
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
        self.tooltip = tk.Toplevel()
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes('-topmost', True)
        
        tooltip_frame = ttk.Frame(self.tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        def on_motion(event):
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                bar_width = (self.width - 2 * self.padding) / self.bins
                bar_index = int((x - self.padding) / bar_width)
                
                if 0 <= bar_index < self.bins and self.frequencies[bar_index] > 0:
                    x_left = self._data_to_pixel_x(self.bin_edges[bar_index], self.x_min, self.x_max)
                    x_right = self._data_to_pixel_x(self.bin_edges[bar_index + 1], self.x_min, self.x_max)
                    y_base = self._data_to_pixel_y(self.y_min, self.y_min, self.y_max)
                    y_top = self._data_to_pixel_y(self.frequencies[bar_index], self.y_min, self.y_max)
                    
                    if self.current_highlight:
                        self.canvas.delete(self.current_highlight)
                    
                    highlight = self.canvas.create_rectangle(
                        x_left - 2, y_top - 2,
                        x_right + 2, y_base + 2,
                        outline=self.style.ACCENT,
                        width=2,
                        tags=('highlight',)
                    )
                    self.current_highlight = highlight
                    
                    label.config(text=f"Range: [{self.bin_edges[bar_index]:.1f}, {self.bin_edges[bar_index+1]:.1f})\nFrequency: {self.frequencies[bar_index]}")
                    self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                    self.tooltip.deiconify()
                    self.tooltip.lift()
                else:
                    if self.current_highlight:
                        self.canvas.delete(self.current_highlight)
                        self.current_highlight = None
                    self.tooltip.withdraw()
        
        def on_leave(event):
            if self.current_highlight:
                self.canvas.delete(self.current_highlight)
                self.current_highlight = None
            self.tooltip.withdraw()
        
        self.canvas.bind('<Motion>', on_motion)
        self.canvas.bind('<Leave>', on_leave)

    # def _add_legend(self):
    #     """Add a legend to the histogram"""
    #     legend_frame = ttk.Frame(self.canvas)
    #     legend_frame.place(relx=0.95, rely=0.05, anchor='ne')
        
    #     for i in range(self.bins):
    #         color = self.style.get_gradient_color(i, self.bins)
    #         ttk.Label(legend_frame, text=f"Bin {i+1}", background=color).pack(anchor='w')

    def _add_statistics(self):
        """Display statistical information"""
        stats_frame = ttk.Frame(self.canvas)
        stats_frame.place(relx=0.05, rely=0.05, anchor='nw')
        
        mean = sum(self.data) / len(self.data)
        median = sorted(self.data)[len(self.data) // 2]
        mode = max(set(self.data), key=self.data.count)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in self.data) / len(self.data))
        
        ttk.Label(stats_frame, text=f"Mean: {mean:.2f}").pack(anchor='w')
        ttk.Label(stats_frame, text=f"Median: {median:.2f}").pack(anchor='w')
        ttk.Label(stats_frame, text=f"Mode: {mode:.2f}").pack(anchor='w')
        ttk.Label(stats_frame, text=f"Std Dev: {std_dev:.2f}").pack(anchor='w')

    # def _add_export_button(self):
    #     """Add a button to export the histogram as an image"""
    #     export_button = ttk.Button(self.canvas, text="Export", command=self._export_image)
    #     export_button.place(relx=0.95, rely=0.95, anchor='se')

    # def _export_image(self):
    #     """Export the histogram as an image"""
    #     file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    #     if file_path:
    #         self.canvas.postscript(file=file_path, colormode='color')

    # def _add_theme_switch(self):
    #     """Add a button to switch between light and dark themes"""
    #     theme_button = ttk.Button(self.canvas, text="Switch Theme", command=self._switch_theme)
    #     theme_button.place(relx=0.05, rely=0.95, anchor='sw')

    # def _switch_theme(self):
    #     """Switch between light and dark themes"""
    #     self.theme = 'dark' if self.theme == 'light' else 'light'
    #     self.style = ChartStyle(self.theme)
    #     self.plot(self.data, self.bins)

    def _zoom(self, event):
        """Zoom in or out based on mouse wheel"""
        if event.delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level /= 1.1
        self._redraw()

    def _pan(self, event):
        """Pan the histogram based on mouse drag"""
        self.pan_offset += event.x
        self._redraw()

    def _redraw(self):
        """Redraw the histogram with the current zoom and pan settings"""
        self.canvas.delete('all')
        self._draw_axes(self.x_min * self.zoom_level + self.pan_offset, self.x_max * self.zoom_level + self.pan_offset, self.y_min, self.y_max)
        self._animate_bars()

    def bind_zoom_pan(self):
        """Bind zoom and pan events to the canvas"""
        self.canvas.bind("<MouseWheel>", self._zoom)
        self.canvas.bind("<B1-Motion>", self._pan)