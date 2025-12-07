from typing import List, Optional, Union, Tuple, Dict, Any
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator
import sys
sys.setrecursionlimit(10**8)

logger = logging.getLogger('ChartForgeTK')


class LineChart(Chart):
    """
    Line chart implementation with comprehensive input validation and edge case handling.
    
    Supports single datasets (list of floats) or multiple datasets (list of dicts).
    Each dataset can have different lengths and will be rendered independently.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.6, 3.1, 3.2, 3.5, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', 
                 theme='light', use_container_width_height: bool = False, show_point_labels: bool = True):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
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
        self.show_point_labels = show_point_labels
        self._tooltip = None  # Tooltip window reference

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

    def plot(self, data: Union[List[float], List[Dict[str, Union[List[float], str]]], Any], 
             x_min: Optional[float] = None, x_max: Optional[float] = None, 
             y_min: Optional[float] = None, y_max: Optional[float] = None,
             y_columns: Optional[List[str]] = None,
             label_column: Optional[str] = None):
        """
        Plot the line chart with the given data.
        
        Supports pandas DataFrame, Series, or list input. When a DataFrame is passed,
        multiple columns can be extracted for multi-series plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of numeric values (single dataset)
                - List of dicts with 'data', 'color', 'shape', and 'label' keys (multiple datasets)
                - pandas DataFrame (uses y_columns for multi-series or first numeric column)
                - pandas Series (uses values with index as labels)
                Each dataset can have different lengths (Requirements: 2.6).
            x_min, x_max, y_min, y_max: Optional axis range limits
            y_columns: List of column names for multi-series plotting when data is a DataFrame.
                If not specified, uses the first numeric column for a single series.
            label_column: Column name for x-axis labels when data is a DataFrame.
                If not specified, uses the DataFrame index.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty
            ImportError: If pandas DataFrame/Series is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.6, 4.2, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.2, 4.5)
        if DataValidator.is_pandas_dataframe(data):
            if y_columns is not None and len(y_columns) > 0:
                # Multi-series extraction from DataFrame
                extracted_columns, labels = DataValidator.extract_dataframe_columns(
                    data,
                    columns=y_columns,
                    param_name="data"
                )
                # Handle label_column if specified
                if label_column is not None:
                    if label_column not in data.columns:
                        available_columns = list(data.columns)
                        raise ValueError(
                            f"[ChartForgeTK] Error: Column '{label_column}' not found in DataFrame. "
                            f"Available columns: {available_columns}"
                        )
                    # Re-extract with label column
                    labels = [str(val) for val in data[label_column].tolist()]
                    # Filter labels to match valid rows (same filtering as extract_dataframe_columns)
                    import math as _math
                    valid_indices = []
                    for i in range(len(data)):
                        row_valid = True
                        for col in y_columns:
                            val = float(data[col].iloc[i])
                            if _math.isnan(val) or _math.isinf(val):
                                row_valid = False
                                break
                        if row_valid:
                            valid_indices.append(i)
                    labels = [str(data[label_column].iloc[i]) for i in valid_indices]
                
                # Convert to multi-dataset format
                colors = ['#2563EB', '#DC2626', '#059669', '#D97706', '#7C3AED', '#DB2777']
                data = []
                for idx, col_values in enumerate(extracted_columns):
                    data.append({
                        'data': col_values,
                        'color': colors[idx % len(colors)],
                        'shape': self.shapes[idx % len(self.shapes)],
                        'label': y_columns[idx]
                    })
            else:
                # Single series from DataFrame (use first numeric column)
                converted_values, converted_labels = DataValidator.convert_dataframe_to_list(
                    data,
                    value_column=None,  # Use first numeric column
                    label_column=label_column,
                    param_name="data"
                )
                data = converted_values
        # Handle pandas Series input (Requirements: 4.5)
        elif DataValidator.is_pandas_series(data):
            converted_values, converted_labels = DataValidator.convert_series_to_list(
                data,
                param_name="data"
            )
            data = converted_values
        # When column parameters are provided with non-DataFrame data, ignore them (Requirements: 4.5)
        # This maintains backward compatibility - no action needed, just proceed with list validation
        
        # Validate data is not None (Requirements: 1.1)
        if data is None:
            raise TypeError(
                "[LineChart] Error: data cannot be None. "
                "Please provide a list of numeric values or a list of dataset dictionaries."
            )
        
        # Validate data is a list/tuple (Requirements: 1.3)
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[LineChart] Error: data must be a list, got {type(data).__name__}. "
                "Please provide a list of numeric values or a list of dataset dictionaries."
            )
        
        # Check for empty data (Requirements: 1.2)
        if not data:
            raise ValueError(
                "[LineChart] Error: data cannot be empty. "
                "Please provide at least one data point."
            )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()

        # Determine if single dataset (list of numbers) or multiple datasets (list of dicts)
        if isinstance(data, (list, tuple)) and len(data) > 0 and all(isinstance(x, (int, float)) for x in data):
            # Single dataset - validate using DataValidator (Requirements: 1.1, 1.2, 1.3)
            validated_data = DataValidator.validate_numeric_list(
                data,
                allow_empty=False,
                allow_negative=True,  # Line charts support negative values
                allow_nan=False,
                allow_inf=False,
                param_name="data"
            )
            # Create copy for immutability (Requirements: 9.1, 9.2)
            self.datasets = [{
                'data': validated_data.copy(),
                'color': self._clamp_color(self.style.ACCENT),
                'shape': 'circle',
                'label': 'Line 1'
            }]
        else:
            # Multiple datasets - validate each one (Requirements: 1.1, 1.2, 1.3, 2.6)
            self.datasets = []
            for idx, dataset in enumerate(data):
                # Validate dataset is a dict
                if not isinstance(dataset, dict):
                    raise TypeError(
                        f"[LineChart] Error: data[{idx}] must be a dictionary with 'data' key, "
                        f"got {type(dataset).__name__}."
                    )
                
                # Validate 'data' key exists
                if 'data' not in dataset:
                    raise ValueError(
                        f"[LineChart] Error: data[{idx}] must contain a 'data' key. "
                        "Each dataset dictionary must have a 'data' key with numeric values."
                    )
                
                # Validate the dataset's data using DataValidator (Requirements: 1.1, 1.2, 1.3)
                validated_dataset_data = DataValidator.validate_numeric_list(
                    dataset['data'],
                    allow_empty=False,
                    allow_negative=True,
                    allow_nan=False,
                    allow_inf=False,
                    param_name=f"data[{idx}]['data']"
                )
                
                # Create copy for immutability (Requirements: 9.1, 9.2)
                self.datasets.append({
                    'data': validated_dataset_data.copy(),
                    'color': self._clamp_color(dataset.get('color', self.style.ACCENT)),
                    'shape': dataset.get('shape', 'circle') if dataset.get('shape') in self.shapes else 'circle',
                    'label': str(dataset.get('label', f'Line {len(self.datasets) + 1}'))
                })

        # Collect all data points for range calculation
        all_data = [x for ds in self.datasets for x in ds['data']]
        
        # Handle edge case: single data point (Requirements: 2.1)
        max_dataset_length = max(len(ds['data']) for ds in self.datasets)
        if max_dataset_length == 1:
            # Single point - create a meaningful x-axis range
            full_x_min, full_x_max = -0.5, 0.5
            logger.debug("Single data point detected, using x-axis range [-0.5, 0.5]")
        else:
            full_x_min, full_x_max = 0, max_dataset_length - 1
        
        full_y_min, full_y_max = min(all_data), max(all_data)
        
        # Handle edge case: all values are identical (Requirements: 2.2)
        if full_y_min == full_y_max:
            # All values identical - create meaningful y-axis range
            if full_y_min == 0:
                # All zeros - use default range
                full_y_min, full_y_max = -1, 1
                logger.debug("All data values are zero, using y-axis range [-1, 1]")
            else:
                # Non-zero identical values - use 20% padding
                padding_val = abs(full_y_min) * 0.2 if full_y_min != 0 else 1
                full_y_min -= padding_val
                full_y_max += padding_val
                logger.debug(f"All data values identical, adjusted y-axis range to [{full_y_min}, {full_y_max}]")
        else:
            # Normal case: add 10% padding
            padding = (full_y_max - full_y_min) * 0.1
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

        self.canvas.delete('label')
        self.canvas.delete('all')
        self._draw_axes(x_min, x_max, y_min, y_max)

        # Store pixel coordinates with original data indices
        self.points = {}
        for idx, dataset in enumerate(self.datasets):
            self.points[idx] = []
            for i, y in enumerate(dataset['data']):
                if x_min <= i <= x_max and y_min <= y <= y_max:
                    x = self._data_to_pixel_x(i, x_min, x_max)
                    y_pixel = self._data_to_pixel_y(y, y_min, y_max)
                    self.points[idx].append((x, y_pixel, i))  # Store (x_pixel, y_pixel, data_index)

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
        """
        Draw lines with smooth animation.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - Identical values (Requirements: 2.2)
        - Variable length datasets (Requirements: 2.6)
        
        Requirements: 3.2, 3.6
        """
        MAX_POINTS_FOR_FULL_LABELS = 50
        LABEL_DECIMATION_FACTOR = 10
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
                # Handle single data point (Requirements: 2.1)
                x, y, data_idx = self.points[idx][0]
                fill_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 1.2))
                outline_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 0.8))
                dot = self._create_shape(x, y, dataset['shape'], self.dot_radius, fill_color, outline_color)
                dots[idx] = [dot]
                labels[idx] = []
                if self.show_point_labels:
                    label = self.canvas.create_text(
                        x, y - 15, text=f"{dataset['data'][data_idx]:,.2f}",
                        font=self.style.VALUE_FONT, fill=self.style.TEXT,
                        anchor='s', tags=('label', f'point_{idx}_0')
                    )
                    labels[idx].append(label)
            else:
                # Empty dataset for this view (may happen with zoom)
                dots[idx] = []
                labels[idx] = []

        def ease(t):
            return t * t * (3 - 2 * t)

        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
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
                        try:
                            self.canvas.coords(dots[idx][i], x1 - self.dot_radius, y1 - self.dot_radius,
                                               x1 + self.dot_radius, y1 + self.dot_radius)
                            self.canvas.itemconfig(dots[idx][i], state='normal')
                            if self.show_point_labels and i < len(labels[idx]):
                                self.canvas.coords(labels[idx][i], x1, y1 - 15)
                                self.canvas.itemconfig(labels[idx][i], state='normal')
                        except tk.TclError:
                            pass  # Widget may have been destroyed

                try:
                    self.canvas.coords(shadows[idx], *current_points)
                    self.canvas.coords(lines[idx], *current_points)
                except tk.TclError:
                    pass  # Widget may have been destroyed

                if frame == total_frames:
                    for i, (x, y, data_idx) in enumerate(self.points[idx]):
                        if i >= len(dots[idx]):
                            fill_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 1.2))
                            outline_color = self._clamp_color(self.style.adjust_brightness(dataset['color'], 0.8))
                            try:
                                dot = self._create_shape(x, y, dataset['shape'], self.dot_radius, fill_color, outline_color)
                                dots[idx].append(dot)
                                if self.show_point_labels:
                                    if len(dataset['data']) > MAX_POINTS_FOR_FULL_LABELS:
                                        if data_idx % LABEL_DECIMATION_FACTOR == 0:
                                            label = self.canvas.create_text(
                                                x, y - 15, text=f"{dataset['data'][data_idx]:,.2f}",
                                                font=self.style.VALUE_FONT, fill=self.style.TEXT,
                                                anchor='s', tags=('label', f'point_{idx}_{i}')
                                            )
                                            labels[idx].append(label)
                                    else:
                                        label = self.canvas.create_text(
                                            x, y - 15, text=f"{dataset['data'][data_idx]:,.2f}",
                                            font=self.style.VALUE_FONT, fill=self.style.TEXT,
                                            anchor='s', tags=('label', f'point_{idx}_{i}')
                                        )
                                        labels[idx].append(label)
                            except tk.TclError:
                                pass  # Widget may have been destroyed

            if frame < total_frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                try:
                    after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                    self.resource_manager.register_animation(after_id)
                except tk.TclError:
                    pass  # Widget may have been destroyed

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
        """
        Add hover effects and tooltips with proper resource management.
        
        Requirements: 3.1, 3.5, 7.1, 7.2, 7.6
        """
        # Create tooltip window
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        try:
            tooltip.attributes('-topmost', True)
        except tk.TclError:
            pass  # Some platforms may not support this
        
        # Register tooltip with resource manager (Requirements: 3.1, 7.6)
        self.resource_manager.register_tooltip(tooltip)
        self._tooltip = tooltip
        
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
            """Handle mouse motion events (Requirements: 7.2)"""
            nonlocal current_highlight, v_bar, h_bar
            
            # Safety check - ensure datasets exist
            if not self.datasets:
                return
            
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
                
                try:
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
                except tk.TclError:
                    pass  # Widget may have been destroyed
                
                if closest_idx >= 0:
                    px, py, data_idx = self.points[closest_dataset][closest_idx]
                    
                    try:
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
                    except tk.TclError:
                        pass  # Widget may have been destroyed
                else:
                    try:
                        if current_highlight:
                            self.canvas.delete(current_highlight)
                            current_highlight = None
                        tooltip.withdraw()
                    except tk.TclError:
                        pass
            else:
                try:
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
                except tk.TclError:
                    pass
        
        def on_leave(event):
            """Handle mouse leave events"""
            nonlocal current_highlight, v_bar, h_bar
            try:
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
            except tk.TclError:
                pass

        def on_mouse_wheel(event):
            """Handle mouse wheel events for zooming (Requirements: 7.4)"""
            # Safety check - ensure datasets exist
            if not self.datasets:
                return
            
            if self.padding <= event.x <= self.width - self.padding and self.padding <= event.y <= self.height - self.padding:
                zoom_in = event.delta > 0
                new_zoom = self.zoom_level + (self.zoom_step if zoom_in else -self.zoom_step)
                new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

                if new_zoom != self.zoom_level:
                    all_data = [x for ds in self.datasets for x in ds['data']]
                    
                    # Handle edge case: single data point
                    max_dataset_length = max(len(ds['data']) for ds in self.datasets)
                    if max_dataset_length == 1:
                        full_x_min, full_x_max = -0.5, 0.5
                    else:
                        full_x_min, full_x_max = 0, max_dataset_length - 1
                    
                    full_y_min, full_y_max = min(all_data), max(all_data)
                    
                    # Handle identical values
                    if full_y_min == full_y_max:
                        if full_y_min == 0:
                            full_y_min, full_y_max = -1, 1
                        else:
                            padding_val = abs(full_y_min) * 0.2 if full_y_min != 0 else 1
                            full_y_min -= padding_val
                            full_y_max += padding_val
                    else:
                        padding = (full_y_max - full_y_min) * 0.1
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

        # Bind events and register with resource manager (Requirements: 3.5)
        motion_id = self.canvas.bind('<Motion>', on_motion)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        wheel_id = self.canvas.bind('<MouseWheel>', on_mouse_wheel)
        
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)
        self.resource_manager.register_binding(self.canvas, '<MouseWheel>', wheel_id)
        
        # Linux scroll wheel support
        button4_id = self.canvas.bind('<Button-4>', lambda e: on_mouse_wheel(type('Event', (), {'delta': 120, 'x': e.x, 'y': e.y})()))
        button5_id = self.canvas.bind('<Button-5>', lambda e: on_mouse_wheel(type('Event', (), {'delta': -120, 'x': e.x, 'y': e.y})()))
        
        self.resource_manager.register_binding(self.canvas, '<Button-4>', button4_id)
        self.resource_manager.register_binding(self.canvas, '<Button-5>', button5_id)
