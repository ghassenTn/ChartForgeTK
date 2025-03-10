from typing import List
import tkinter as tk
from tkinter import ttk
import math
import statistics
from .core import Chart, ChartStyle
class BoxPlot(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of lists (each sublist is a dataset)
        self.labels = []
        self.box_width_factor = 0.6  # Width of boxes relative to spacing
        self.animation_duration = 500
        self.elements = []  # Store canvas items
        
    def plot(self, data: List[List[float]], labels: List[str] = None):
        """Plot the box plot with multiple datasets"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(d, list) and all(isinstance(x, (int, float)) for x in d) for d in data):
            raise TypeError("Data must be a list of lists of numbers")
        if labels and len(labels) != len(data):
            raise ValueError("Number of labels must match number of datasets")
            
        self.data = data
        self.labels = labels or [f"Group {i+1}" for i in range(len(data))]
        
        # Calculate ranges
        all_values = [x for sublist in data for x in sublist]
        self.x_min, self.x_max = -0.5, len(data) - 0.5
        self.y_min, self.y_max = min(all_values), max(all_values)
        y_padding = (self.y_max - self.y_min) * 0.1 or 1
        self.y_min -= y_padding
        self.y_max += y_padding
        
        # Set labels
        self.title = "Box Plot"
        self.x_label = "Groups"
        self.y_label = "Values"
        
        self.canvas.delete('all')
        self.elements.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_boxes()
        self._add_interactive_effects()

    def _animate_boxes(self):
        """Draw box plots with smooth height animation"""
        def ease(t):
            return t * t * (3 - 2 * t)
        
        box_spacing = (self.width - 2 * self.padding) / len(self.data)
        box_width = box_spacing * self.box_width_factor
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            for item in self.elements:
                self.canvas.delete(item)
            self.elements.clear()
            
            for i, dataset in enumerate(self.data):
                x = self._data_to_pixel_x(i, self.x_min, self.x_max)
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Calculate box plot statistics
                q1 = statistics.quantiles(dataset, n=4)[0]  # First quartile
                median = statistics.median(dataset)
                q3 = statistics.quantiles(dataset, n=4)[2]  # Third quartile
                iqr = q3 - q1
                lower_whisker = max(min(dataset), q1 - 1.5 * iqr)
                upper_whisker = min(max(dataset), q3 + 1.5 * iqr)
                outliers = [y for y in dataset if y < lower_whisker or y > upper_whisker]
                
                # Animate box height
                y_q1 = self._data_to_pixel_y(q1, self.y_min, self.y_max)
                y_q3 = self._data_to_pixel_y(q3, self.y_min, self.y_max)
                y_median = self._data_to_pixel_y(median, self.y_min, self.y_max)
                y_lower = self._data_to_pixel_y(lower_whisker, self.y_min, self.y_max)
                y_upper = self._data_to_pixel_y(upper_whisker, self.y_min, self.y_max)
                box_height = (y_q1 - y_q3) * progress
                
                # Shadow
                shadow = self.canvas.create_rectangle(
                    x - box_width/2 + 2, y_q3 + 2,
                    x + box_width/2 + 2, y_q1 + 2,
                    fill=self.style.create_shadow(color),
                    outline="",
                    tags=('shadow', f'box_{i}')
                )
                self.elements.append(shadow)
                
                # Box
                box = self.canvas.create_rectangle(
                    x - box_width/2, y_q3 + box_height,
                    x + box_width/2, y_q1 - box_height,
                    fill=color,
                    outline=self.style.adjust_brightness(color, 0.8),
                    tags=('box', f'box_{i}')
                )
                self.elements.append(box)
                
                # Median line
                median_line = self.canvas.create_line(
                    x - box_width/2, y_median,
                    x + box_width/2, y_median,
                    fill=self.style.TEXT,
                    width=2,
                    tags=('median', f'box_{i}')
                )
                self.elements.append(median_line)
                
                # Whiskers (animate length)
                whisker_progress = progress
                self.canvas.create_line(
                    x, y_q1, x, y_q1 + (y_lower - y_q1) * whisker_progress,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('whisker', f'box_{i}')
                )
                self.canvas.create_line(
                    x, y_q3, x, y_q3 - (y_q3 - y_upper) * whisker_progress,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('whisker', f'box_{i}')
                )
                # Whisker caps
                self.canvas.create_line(
                    x - box_width/4, y_lower,
                    x + box_width/4, y_lower,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('cap', f'box_{i}')
                )
                self.canvas.create_line(
                    x - box_width/4, y_upper,
                    x + box_width/4, y_upper,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('cap', f'box_{i}')
                )
                
                # Outliers
                for outlier in outliers:
                    y_out = self._data_to_pixel_y(outlier, self.y_min, self.y_max)
                    outlier_mark = self.canvas.create_oval(
                        x - 3, y_out - 3,
                        x + 3, y_out + 3,
                        fill=self.style.ACCENT,
                        outline="",
                        tags=('outlier', f'box_{i}')
                    )
                    self.elements.append(outlier_mark)
                
                # Label
                if progress == 1:
                    label = self.canvas.create_text(
                        x, self.height - self.padding + 15,
                        text=self.labels[i],
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='n',
                        tags=('label', f'box_{i}')
                    )
                    self.elements.append(label)
            
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
                box_spacing = (self.width - 2 * self.padding) / len(self.data)
                box_width = box_spacing * self.box_width_factor
                box_index = int((x - self.padding) / box_spacing)
                
                if 0 <= box_index < len(self.data):
                    dataset = self.data[box_index]
                    px = self._data_to_pixel_x(box_index, self.x_min, self.x_max)
                    q1 = statistics.quantiles(dataset, n=4)[0]
                    median = statistics.median(dataset)
                    q3 = statistics.quantiles(dataset, n=4)[2]
                    iqr = q3 - q1
                    lower_whisker = max(min(dataset), q1 - 1.5 * iqr)
                    upper_whisker = min(max(dataset), q3 + 1.5 * iqr)
                    
                    y_q1 = self._data_to_pixel_y(q1, self.y_min, self.y_max)
                    y_q3 = self._data_to_pixel_y(q3, self.y_min, self.y_max)
                    
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    highlight = self.canvas.create_rectangle(
                        px - box_width/2 - 2, y_q3 - 2,
                        px + box_width/2 + 2, y_q1 + 2,
                        outline=self.style.ACCENT,
                        width=2,
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    label.config(text=f"{self.labels[box_index]}\nMin: {min(dataset):.1f}\nQ1: {q1:.1f}\nMedian: {median:.1f}\nQ3: {q3:.1f}\nMax: {max(dataset):.1f}")
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