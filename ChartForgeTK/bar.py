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


from typing import List, Optional, Union, Tuple, Any
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class BarChart(Chart):
    """
    Bar chart implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.4, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light', palette='modern'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme, palette=palette)
        self.data = []
        self.labels = []
        self.bar_width_factor = 0.8  # Percentage of available space per bar
        self.animation_duration = 500  # ms
        self.bars = []  # Store bar references
        self._tooltip = None  # Tooltip window reference
        
    def plot(
        self,
        data: Any,
        labels: Optional[Union[List[str], str]] = None,
        value_column: Optional[str] = None,
        label_column: Optional[str] = None
    ):
        """
        Plot the bar chart with the given data and optional labels.
        
        Supports pandas DataFrame, Series, or list input. When a DataFrame or Series
        is passed, the data is automatically converted to lists for plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of numeric values (must be non-negative)
                - pandas DataFrame (uses value_column or first numeric column)
                - pandas Series (uses values with index as labels)
            labels: Optional labels for each bar. Can be:
                - List of strings
                - Ignored when data is a pandas object (use label_column instead)
            value_column: Column name for values when data is a DataFrame.
                If not specified, uses the first numeric column.
            label_column: Column name for labels when data is a DataFrame.
                If not specified, uses the DataFrame index.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty, contains negative values, or labels mismatch
            ImportError: If pandas DataFrame/Series is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.5, 2.4, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.1, 4.5)
        if DataValidator.is_pandas_dataframe(data):
            converted_values, converted_labels = DataValidator.convert_dataframe_to_list(
                data,
                value_column=value_column,
                label_column=label_column,
                param_name="data"
            )
            data = converted_values
            # Use converted labels if no explicit labels provided
            if labels is None:
                labels = converted_labels
        # Handle pandas Series input (Requirements: 4.1, 4.5)
        elif DataValidator.is_pandas_series(data):
            converted_values, converted_labels = DataValidator.convert_series_to_list(
                data,
                param_name="data"
            )
            data = converted_values
            # Use converted labels if no explicit labels provided
            if labels is None:
                labels = converted_labels
        # When column parameters are provided with non-DataFrame data, ignore them (Requirements: 2.4)
        # This maintains backward compatibility - no action needed, just proceed with list validation
        
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_numeric_list(
            data,
            allow_empty=False,
            allow_negative=False,  # Bar charts don't support negative values
            allow_nan=False,
            allow_inf=False,
            param_name="data"
        )
        
        # Validate labels (Requirements: 1.4)
        validated_labels = DataValidator.validate_labels(labels, len(validated_data), param_name="labels")
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        self.data = validated_data.copy()
        self.labels = validated_labels.copy()
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Calculate ranges with edge case handling
        x_min, x_max = -0.5, len(self.data) - 0.5
        y_min = 0
        y_max = max(self.data) if self.data else 0
        
        # Handle edge case: all values are identical or zero (Requirements: 2.2, 2.4)
        if y_max == 0:
            # All values are zero - use a default range
            y_max = 1.0
            logger.debug("All data values are zero, using default y-axis range [0, 1]")
        elif len(set(self.data)) == 1:
            # All values are identical - create meaningful range
            # Use 20% padding above and below the value
            value = self.data[0]
            y_max = value * 1.2 if value > 0 else 1.0
            logger.debug(f"All data values identical ({value}), adjusted y-axis range")
        else:
            # Normal case: add 10% padding
            padding = y_max * 0.1
            y_max += padding
        
        # Clear previous content
        self.canvas.delete('all')
        self.bars.clear()
        
        self._draw_axes(x_min, x_max, y_min, y_max)
        self._animate_bars(y_min, y_max)
        self._add_interactive_effects()

    def _animate_bars(self, y_min: float, y_max: float):
        """
        Draw bars with smooth height animation and professional styling.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - Zero values (Requirements: 2.4)
        - Identical values (Requirements: 2.2)
        
        Requirements: 3.2, 3.6
        """
        if len(self.data) == 1:
            bar_spacing = (self.width - 2 * self.padding) / 2
            bar_width = bar_spacing * self.bar_width_factor
        else:
            bar_spacing = (self.width - 2 * self.padding) / len(self.data)
            bar_width = bar_spacing * self.bar_width_factor
        
        corner_radius = min(4, bar_width / 4)
        
        def ease(t):
            return t * t * (3 - 2 * t)
        
        def update_animation(frame: int, total_frames: int):
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            
            for item in self.bars:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.bars.clear()
            
            for i, value in enumerate(self.data):
                x = self._data_to_pixel_x(i, -0.5, len(self.data) - 0.5)
                y_base = self._data_to_pixel_y(y_min, y_min, y_max)
                y_top = self._data_to_pixel_y(value, y_min, y_max)
                
                if value == 0:
                    y_current = y_base
                else:
                    y_current = y_base - (y_base - y_top) * progress
                
                color = self.style.get_color(i)
                
                # Gradient bar
                x1 = x - bar_width / 2
                x2 = x + bar_width / 2
                
                if y_current < y_base:
                    num_steps = max(8, int((y_base - y_current) / 3))
                    step_h = (y_base - y_current) / num_steps
                    for s in range(num_steps):
                        sy1 = y_current + s * step_h
                        sy2 = sy1 + step_h + 1
                        ratio = s / num_steps
                        lighter = self.style.create_lighter(color, 1.0 + 0.3 * (1 - ratio))
                        self.bars.append(
                            self.canvas.create_rectangle(
                                x1, sy1, x2, sy2,
                                fill=lighter, outline="",
                                tags=('bar_grad', f'bar_{i}')
                            )
                        )
                    
                    # Highlight top edge
                    self.bars.append(
                        self.canvas.create_line(
                            x1, y_current, x2, y_current,
                            fill=self.style.create_lighter(color, 1.4),
                            width=2, capstyle=tk.ROUND,
                            tags=('bar_highlight', f'bar_{i}')
                        )
                    )
                    
                    # Bottom shadow
                    self.bars.append(
                        self.canvas.create_rectangle(
                            x1 + 2, y_base - 1, x2 + 2, y_base + 2,
                            fill=self.style.create_shadow(color, 0.5),
                            outline="",
                            tags=('shadow', f'bar_{i}')
                        )
                    )
                
                if progress == 1:
                    if value == 0:
                        value_text = "0"
                    elif value == int(value):
                        value_text = f"{int(value):,}"
                    else:
                        value_text = f"{value:,.1f}"
                    
                    label_y = y_top - 8
                    self.bars.append(
                        self.canvas.create_text(
                            x, label_y,
                            text=f"{value_text}",
                            font=self.style.VALUE_FONT,
                            fill=self.style.TEXT,
                            anchor='s',
                            tags=('label', f'bar_{i}')
                        )
                    )
            
            if frame < total_frames:
                after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
        total_frames = self.animation_duration // 16
        update_animation(0, total_frames)
    
    def _redraw_bars(self, y_min, y_max):
        """Redraw bars for resize/redraw without animation."""
        if len(self.data) == 1:
            bar_spacing = (self.width - 2 * self.padding) / 2
            bar_width = bar_spacing * self.bar_width_factor
        else:
            bar_spacing = (self.width - 2 * self.padding) / len(self.data)
            bar_width = bar_spacing * self.bar_width_factor
        
        for i, value in enumerate(self.data):
            x = self._data_to_pixel_x(i, -0.5, len(self.data) - 0.5)
            y_base = self._data_to_pixel_y(y_min, y_min, y_max)
            y_top = self._data_to_pixel_y(value, y_min, y_max)
            
            color = self.style.get_color(i)
            x1 = x - bar_width / 2
            x2 = x + bar_width / 2
            
            num_steps = max(8, int((y_base - y_top) / 3))
            step_h = (y_base - y_top) / num_steps
            for s in range(num_steps):
                sy1 = y_top + s * step_h
                sy2 = sy1 + step_h + 1
                ratio = s / num_steps
                lighter = self.style.create_lighter(color, 1.0 + 0.3 * (1 - ratio))
                self.canvas.create_rectangle(
                    x1, sy1, x2, sy2,
                    fill=lighter, outline="",
                    tags=('bar_grad', f'bar_{i}')
                )
            
            self.canvas.create_line(
                x1, y_top, x2, y_top,
                fill=self.style.create_lighter(color, 1.4),
                width=2, capstyle=tk.ROUND,
                tags=('bar_highlight', f'bar_{i}')
            )
            
            self.canvas.create_rectangle(
                x1 + 2, y_base - 1, x2 + 2, y_base + 2,
                fill=self.style.create_shadow(color, 0.5),
                outline="",
                tags=('shadow', f'bar_{i}')
            )
            
            if value == 0:
                value_text = "0"
            elif value == int(value):
                value_text = f"{int(value):,}"
            else:
                value_text = f"{value:,.1f}"
            
            self.canvas.create_text(
                x, y_top - 8,
                text=value_text,
                font=self.style.VALUE_FONT,
                fill=self.style.TEXT,
                anchor='s',
                tags=('label', f'bar_{i}')
            )

    def redraw_chart(self):
        """Redraw chart for resize events."""
        if not self.data:
            return
        x_min, x_max = -0.5, len(self.data) - 0.5
        y_min = 0
        y_max = max(self.data) if self.data else 0
        if y_max == 0:
            y_max = 1.0
        elif len(set(self.data)) == 1:
            y_max = self.data[0] * 1.2 if self.data[0] > 0 else 1.0
        else:
            y_max += y_max * 0.1
        self._draw_axes(x_min, x_max, y_min, y_max)
        self._redraw_bars(y_min, y_max)
        self._add_interactive_effects()

    def _add_interactive_effects(self):
        """
        Add hover effects and tooltips with proper resource management.
        
        Requirements: 3.1, 3.5, 7.1, 7.2, 7.6
        """
        current_highlight = None
        current_glow = None
        
        def on_motion(event):
            nonlocal current_highlight, current_glow
            
            if not self.data:
                return
            
            x = event.x
            
            if self.padding <= x <= self.width - self.padding:
                bar_spacing = (self.width - 2 * self.padding) / len(self.data)
                bar_index = int((x - self.padding) / bar_spacing)
                
                if 0 <= bar_index < len(self.data):
                    bar_x = self._data_to_pixel_x(bar_index, -0.5, len(self.data) - 0.5)
                    bar_width = bar_spacing * self.bar_width_factor
                    value = self.data[bar_index]
                    
                    max_val = max(self.data) if self.data else 1
                    if max_val == 0:
                        max_val = 1
                    y_max_display = max_val * 1.1
                    
                    y_top = self._data_to_pixel_y(value, 0, y_max_display)
                    y_base = self._data_to_pixel_y(0, 0, y_max_display)
                    
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                    
                    if current_glow:
                        try:
                            self.canvas.delete(current_glow)
                        except tk.TclError:
                            pass
                    
                    try:
                        glow = self.canvas.create_rectangle(
                            bar_x - bar_width/2 - 4,
                            y_top - 4,
                            bar_x + bar_width/2 + 4,
                            y_base + 4,
                            fill="",
                            outline=self.style.HIGHLIGHT_GLOW,
                            width=3,
                            stipple="gray12",
                            tags=('glow',)
                        )
                        current_glow = glow
                    except tk.TclError:
                        current_glow = None
                    
                    if value == 0:
                        value_text = "0"
                    elif value == int(value):
                        value_text = f"{int(value):,}"
                    else:
                        value_text = f"{value:,.2f}"
                    
                    self.show_tooltip(
                        event.x_root, event.y_root,
                        f"{self.labels[bar_index]}\nValue: {value_text}"
                    )
                else:
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                        current_highlight = None
                    if current_glow:
                        try:
                            self.canvas.delete(current_glow)
                        except tk.TclError:
                            pass
                        current_glow = None
                    self.hide_tooltip()
            else:
                if current_highlight:
                    try:
                        self.canvas.delete(current_highlight)
                    except tk.TclError:
                        pass
                    current_highlight = None
                if current_glow:
                    try:
                        self.canvas.delete(current_glow)
                    except tk.TclError:
                        pass
                    current_glow = None
                self.hide_tooltip()
        
        def on_leave(event):
            nonlocal current_highlight, current_glow
            if current_highlight:
                try:
                    self.canvas.delete(current_highlight)
                except tk.TclError:
                    pass
                current_highlight = None
            if current_glow:
                try:
                    self.canvas.delete(current_glow)
                except tk.TclError:
                    pass
                current_glow = None
            self.hide_tooltip()
        
        motion_id = self.canvas.bind('<Motion>', on_motion)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)

# Usage example:
"""
chart = BarChart()
data = [10, 20, 15, 25]
labels = ["A", "B", "C", "D"]
chart.plot(data, labels)
"""