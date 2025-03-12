from typing import List, Optional, Union, Tuple, Dict
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle
import sys
sys.setrecursionlimit(10**8)

class LineChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', use_container_width_height: bool = False):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.datasets = []
        self.points = {}  # Now stores (x_pixel, y_pixel, data_index) tuples
        self.line_width = 1
        self.dot_radius = 5
        self.animation_duration = 500
        self.shapes = ['circle', 'square', 'triangle', 'diamond']
        self.bars = []
        self.zoom_level = 1.0
        self.zoom_center_x = None
        self.zoom_center_y = None
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.zoom_step = 0.2
        self.use_container_width_height = use_container_width_height

        if self.use_container_width_height and self.parent:
            self.parent.bind('<Configure>', self._on_parent_resize)
            self.width = self.parent.winfo_width() if self.parent.winfo_width() > 1 else width
            self.height = self.parent.winfo_height() if self.parent.winfo_height() > 1 else height

        self.canvas.config(width=self.width, height=self.height)

    def _on_parent_resize(self, event):
        if self.use_container_width_height:
            new_width = event.width
            new_height = event.height
            if new_width != self.width or new_height != self.height:
                self.width = new_width
                self.height = new_height
                self.canvas.config(width=self.width, height=self.height)
                if self.datasets:
                    self.plot(self.datasets)

    def _clamp_color(self, color: str) -> str:
        if not color.startswith('#') or len(color) != 7:
            return "#000000"
        try:
            r = max(0, min(255, int(color[1:3], 16)))
            g = max(0, min(255, int(color[3:5], 16)))
            b = max(0, min(255, int(color[5:7], 16)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            return "#000000"

    def plot(self, data: Union[List[float], List[Dict[str, Union[List[float], str]]]], 
             x_min: Optional[float] = None, x_max: Optional[float] = None, 
             y_min: Optional[float] = None, y_max: Optional[float] = None):
        if not data:
            raise ValueError("Data cannot be empty")

        if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
            self.datasets = [{
                'data': data,
                'color': self._clamp_color(self.style.ACCENT),
                'shape': 'circle',
                'label': 'Line 1'
            }]
        else:
            self.datasets = []
            for dataset in data:
                if 'data' not in dataset or not dataset['data']:
                    raise ValueError("Each dataset must contain non-empty 'data'")
                if not all(isinstance(x, (int, float)) for x in dataset['data']):
                    raise TypeError("All data points must be numbers")
                
                self.datasets.append({
                    'data': dataset['data'],
                    'color': self._clamp_color(dataset.get('color', self.style.ACCENT)),
                    'shape': dataset.get('shape', 'circle') if dataset.get('shape') in self.shapes else 'circle',
                    'label': dataset.get('label', f'Line {len(self.datasets) + 1}')
                })

        all_data = [x for ds in self.datasets for x in ds['data']]
        full_x_min, full_x_max = 0, max(len(ds['data']) for ds in self.datasets) - 1
        full_y_min, full_y_max = min(all_data), max(all_data)
        padding = (full_y_max - full_y_min) * 0.1 or 1
        full_y_min -= padding
        full_y_max += padding

        if x_min is None or x_max is None or y_min is None or y_max is None:
            x_range = (full_x_max - full_x_min) / self.zoom_level
            y_range = (full_y_max - full_y_min) / self.zoom_level
            if self.zoom_center_x is None:
                self.zoom_center_x = (full_x_max + full_x_min) / 2
            if self.zoom_center_y is None:
                self.zoom_center_y = (full_y_max + full_y_min) / 2
            
            x_min = max(full_x_min, self.zoom_center_x - x_range / 2)
            x_max = min(full_x_max, self.zoom_center_x + x_range / 2)
            y_min = max(full_y_min, self.zoom_center_y - y_range / 2)
            y_max = min(full_y_max, self.zoom_center_y + y_range / 2)

        self.canvas.delete('all')
        self._draw_axes(x_min, x_max, y_min, y_max)

        # Store pixel coordinates with original data indices
        self.points = {}
        for idx, dataset in enumerate(self.datasets):
            self.points[idx] = []
            for i, y in enumerate(dataset['data']):
                if x_min <= i <= x_max and y_min <= y <= y_max:
                    x = self._data_to_pixel_x(i, x_min, x_max)
                    y = self._data_to_pixel_y(y, y_min, y_max)
                    self.points[idx].append((x, y, i))  # Store (x_pixel, y_pixel, data_index)

        self._animate_lines(y_min, y_max)
        self._add_interactive_effects()

        for bar in self.bars[:]:
            self.canvas.delete(bar['id'])
            if bar['label_id']:
                self.canvas.delete(bar['label_id'])
            self.add_bar(bar['orientation'], bar['value'], bar['color'], bar['width'], bar['dash'], bar['label'])

    def _create_shape(self, x: float, y: float, shape: str, radius: float, fill: str, outline: str) -> int:
        if shape == 'square':
            return self.canvas.create_rectangle(
                x - radius, y - radius, x + radius, y + radius,
                fill=fill, outline=outline, tags=('dot',)
            )
        elif shape == 'triangle':
            return self.canvas.create_polygon(
                x, y - radius, x - radius, y + radius, x + radius, y + radius,
                fill=fill, outline=outline, tags=('dot',)
            )
        elif shape == 'diamond':
            return self.canvas.create_polygon(
                x, y - radius, x + radius, y, x, y + radius, x - radius, y,
                fill=fill, outline=outline, tags=('dot',)
            )
        else:  # circle
            return self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=fill, outline=outline, tags=('dot',)
            )

    def _animate_lines(self, y_min: float, y_max: float):
        lines = {}
        shadows = {}
        dots = {}
        labels = {}

        for idx, dataset in enumerate(self.datasets):
            if idx in self.points and len(self.points[idx]) >= 2:
                lines[idx] = self.canvas.create_line(
                    self.points[idx][0][0], self.points[idx][0][1], 
                    self.points[idx][0][0], self.points[idx][0][1],
                    fill=dataset['color'],
                    width=self.line_width,
                    tags=('line',)
                )
                shadows[idx] = self.canvas.create_line(
                    self.points[idx][0][0], self.points[idx][0][1], 
                    self.points[idx][0][0], self.points[idx][0][1],
                    fill=self.style.create_shadow(dataset['color']),
                    width=self.line_width + 2,
                    tags=('shadow',)
                )
                dots[idx] = []
                labels[idx] = []
            elif idx in self.points and len(self.points[idx]) == 1:
                x, y, data_idx = self.points[idx][0]
                fill_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 1.2))
                outline_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 0.8))
                dot = self._create_shape(x, y, dataset['shape'], self.dot_radius, fill_color, outline_color)
                label = self.canvas.create_text(
                    x, y - 15, text=f"{dataset['data'][data_idx]:,.2f}",
                    font=self.style.VALUE_FONT, fill=self.style.TEXT,
                    anchor='s', tags=('label', f'point_{idx}_0')
                )
                dots[idx] = [dot]
                labels[idx] = [label]
            else:
                dots[idx] = []
                labels[idx] = []

        def ease(t):
            return t * t * (3 - 2 * t)

        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            for idx, dataset in enumerate(self.datasets):
                if idx not in lines:
                    continue
                current_points = []
                for i in range(len(self.points[idx])):
                    x0, y0, _ = self.points[idx][max(0, i-1)]
                    x1, y1, _ = self.points[idx][i]
                    if i == 0:
                        current_points.extend([x1, y1])
                    else:
                        interp_x = x0 + (x1 - x0) * min(1.0, progress * len(self.points[idx]) / (i + 1))
                        interp_y = y0 + (y1 - y0) * min(1.0, progress * len(self.points[idx]) / (i + 1))
                        current_points.extend([interp_x, interp_y])
                    
                    if i < len(dots[idx]) and progress * len(self.points[idx]) >= i + 1:
                        self.canvas.coords(dots[idx][i], x1 - self.dot_radius, y1 - self.dot_radius,
                                           x1 + self.dot_radius, y1 + self.dot_radius)
                        self.canvas.coords(labels[idx][i], x1, y1 - 15)
                        self.canvas.itemconfig(dots[idx][i], state='normal')
                        self.canvas.itemconfig(labels[idx][i], state='normal')

                self.canvas.coords(shadows[idx], *current_points)
                self.canvas.coords(lines[idx], *current_points)

                if frame == total_frames:
                    for i, (x, y, data_idx) in enumerate(self.points[idx]):
                        if i >= len(dots[idx]):
                            fill_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 1.2))
                            outline_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 0.8))
                            dot = self._create_shape(x, y, dataset['shape'], self.dot_radius, fill_color, outline_color)
                            label = self.canvas.create_text(
                                x, y - 15, text=f"{dataset['data'][data_idx]:,.2f}",
                                font=self.style.VALUE_FONT, fill=self.style.TEXT,
                                anchor='s', tags=('label', f'point_{idx}_{i}')
                            )
                            dots[idx].append(dot)
                            labels[idx].append(label)

            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)

        total_frames = self.animation_duration // 16
        update_animation(0, total_frames)

    def add_bar(self, orientation: str, value: float, color: str = '#808080', width: int = 1, 
                dash: Optional[Tuple[int, int]] = None, label: Optional[str] = None):
        if orientation not in ['vertical', 'horizontal']:
            raise ValueError("Orientation must be 'vertical' or 'horizontal'")
        
        if not self.datasets:
            raise ValueError("Cannot add bar before plotting data")
        
        all_data = [x for ds in self.datasets for x in ds['data']]
        x_min, x_max = 0, max(len(ds['data']) for ds in self.datasets) - 1
        y_min, y_max = min(all_data), max(all_data)
        padding = (y_max - y_min) * 0.1 or 1
        y_min -= padding
        y_max += padding

        if orientation == 'vertical':
            if not (x_min <= value <= x_max):
                raise ValueError(f"Vertical bar value {value} is outside x-axis range [{x_min}, {x_max}]")
            x_pixel = self._data_to_pixel_x(value, x_min, x_max)
            bar = self.canvas.create_line(
                x_pixel, self.padding, x_pixel, self.height - self.padding,
                fill=self._clamp_color(color),
                width=width,
                dash=dash,
                tags=('static_bar',)
            )
        else:
            y_pixel = self._data_to_pixel_y(value, y_min, y_max)
            bar = self.canvas.create_line(
                self.padding, y_pixel, self.width - self.padding, y_pixel,
                fill=self._clamp_color(color),
                width=width,
                dash=dash,
                tags=('static_bar',)
            )
        
        label_id = None
        if label:
            if orientation == 'vertical':
                label_id = self.canvas.create_text(
                    x_pixel, self.padding + 10,
                    text=label,
                    font=self.style.VALUE_FONT,
                    fill=self.style.TEXT,
                    anchor='s',
                    tags=('static_bar_label',)
                )
            else:
                label_id = self.canvas.create_text(
                    self.padding + 10, y_pixel - 10 if value >= 0 else y_pixel + 10,
                    text=label,
                    font=self.style.VALUE_FONT,
                    fill=self.style.TEXT,
                    anchor='sw' if value >= 0 else 'nw',
                    tags=('static_bar_label',)
                )
        
        self.bars.append({
            'id': bar,
            'label_id': label_id,
            'orientation': orientation,
            'value': value,
            'color': color,
            'width': width,
            'dash': dash,
            'label': label
        })

    def _add_interactive_effects(self):
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
        v_bar = None
        h_bar = None
        
        def on_motion(event):
            nonlocal current_highlight, v_bar, h_bar
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                closest_idx = -1
                closest_dataset = -1
                min_dist = float('inf')
                
                for dataset_idx, points in self.points.items():
                    for i, (px, py, _) in enumerate(points):
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_dist and dist < 20:
                            min_dist = dist
                            closest_idx = i
                            closest_dataset = dataset_idx
                
                if v_bar:
                    self.canvas.coords(v_bar, x, self.padding, x, self.height - self.padding)
                else:
                    v_bar = self.canvas.create_line(
                        x, self.padding, x, self.height - self.padding,
                        fill='#808080',
                        width=1,
                        dash=(4, 2),
                        tags=('tracking',)
                    )
                
                if h_bar:
                    self.canvas.coords(h_bar, self.padding, y, self.width - self.padding, y)
                else:
                    h_bar = self.canvas.create_line(
                        self.padding, y, self.width - self.padding, y,
                        fill='#808080',
                        width=1,
                        dash=(4, 2),
                        tags=('tracking',)
                    )
                
                if closest_idx >= 0:
                    px, py, data_idx = self.points[closest_dataset][closest_idx]
                    
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    highlight = self.canvas.create_oval(
                        px - self.dot_radius * 1.5,
                        py - self.dot_radius * 1.5,
                        px + self.dot_radius * 1.5,
                        py + self.dot_radius * 1.5,
                        outline=self.datasets[closest_dataset]['color'],
                        width=2,
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    value = self.datasets[closest_dataset]['data'][data_idx]
                    label.config(text=f"Dataset: {self.datasets[closest_dataset]['label']}\n"
                                f"Index: {data_idx}\nValue: {value:,.2f}")
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                    tooltip.deiconify()
                    tooltip.lift()
                else:
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                        current_highlight = None
                    tooltip.withdraw()
            else:
                if v_bar:
                    self.canvas.delete(v_bar)
                    v_bar = None
                if h_bar:
                    self.canvas.delete(h_bar)
                    h_bar = None
                if current_highlight:
                    self.canvas.delete(current_highlight)
                    current_highlight = None
                tooltip.withdraw()
        
        def on_leave(event):
            nonlocal current_highlight, v_bar, h_bar
            if current_highlight:
                self.canvas.delete(current_highlight)
                current_highlight = None
            if v_bar:
                self.canvas.delete(v_bar)
                v_bar = None
            if h_bar:
                self.canvas.delete(h_bar)
                h_bar = None
            tooltip.withdraw()

        def on_mouse_wheel(event):
            if self.padding <= event.x <= self.width - self.padding and self.padding <= event.y <= self.height - self.padding:
                zoom_in = event.delta > 0
                new_zoom = self.zoom_level + (self.zoom_step if zoom_in else -self.zoom_step)
                new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

                if new_zoom != self.zoom_level:
                    all_data = [x for ds in self.datasets for x in ds['data']]
                    full_x_min, full_x_max = 0, max(len(ds['data']) for ds in self.datasets) - 1
                    full_y_min, full_y_max = min(all_data), max(all_data)
                    padding = (full_y_max - full_y_min) * 0.1 or 1
                    full_y_min -= padding
                    full_y_max += padding

                    x_range = (full_x_max - full_x_min) / self.zoom_level
                    y_range = (full_y_max - full_y_min) / self.zoom_level
                    current_x_min = max(full_x_min, self.zoom_center_x - x_range / 2)
                    current_x_max = min(full_x_max, self.zoom_center_x + x_range / 2)
                    current_y_min = max(full_y_min, self.zoom_center_y - y_range / 2)
                    current_y_max = min(full_y_max, self.zoom_center_y + y_range / 2)

                    data_x = current_x_min + (event.x - self.padding) * (current_x_max - current_x_min) / (self.width - 2 * self.padding)
                    data_y = current_y_max - (event.y - self.padding) * (current_y_max - current_y_min) / (self.height - 2 * self.padding)

                    self.zoom_level = new_zoom
                    self.zoom_center_x = data_x
                    self.zoom_center_y = data_y
                    self.plot(self.datasets)

        self.canvas.bind('<Motion>', on_motion)
        self.canvas.bind('<Leave>', on_leave)
        self.canvas.bind('<MouseWheel>', on_mouse_wheel)
        self.canvas.bind('<Button-4>', lambda e: on_mouse_wheel(type('Event', (), {'delta': 120, 'x': e.x, 'y': e.y})()))
        self.canvas.bind('<Button-5>', lambda e: on_mouse_wheel(type('Event', (), {'delta': -120, 'x': e.x, 'y': e.y})()))