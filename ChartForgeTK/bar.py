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
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
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
        Draw bars with smooth height animation.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - Zero values (Requirements: 2.4)
        - Identical values (Requirements: 2.2)
        
        Requirements: 3.2, 3.6
        """
        # Handle edge case: single data point (Requirements: 2.1)
        if len(self.data) == 1:
            bar_spacing = (self.width - 2 * self.padding) / 2  # Center the single bar
            bar_width = bar_spacing * self.bar_width_factor
        else:
            bar_spacing = (self.width - 2 * self.padding) / len(self.data)
            bar_width = bar_spacing * self.bar_width_factor
        
        def ease(t):
            return t * t * (3 - 2 * t)  # Ease-in-out
        
        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            
            # Clear previous bars
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
                
                # Handle zero values - ensure bar is still visible as a line (Requirements: 2.4)
                if value == 0:
                    y_current = y_base
                else:
                    y_current = y_base - (y_base - y_top) * progress
                
                # Get color
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Draw shadow (only if bar has height)
                if y_current < y_base:
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
                
                # Draw bar with gradient (Requirements: 2.4 - zero-height bars render without errors)
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
                    # Format value appropriately
                    if value == 0:
                        value_text = "0"
                    elif value == int(value):
                        value_text = f"{int(value):,}"
                    else:
                        value_text = f"{value:,.1f}"
                    
                    label = self.canvas.create_text(
                        x,
                        y_top - 10,
                        text=f"{self.labels[i]}\n{value_text}",
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='s',
                        justify='center',
                        tags=('label', f'bar_{i}')
                    )
                    self.bars.append(label)
            
            if frame < total_frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
        total_frames = self.animation_duration // 16  # ~60 FPS
        update_animation(0, total_frames)

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
        
        def on_motion(event):
            """Handle mouse motion events (Requirements: 7.2)"""
            nonlocal current_highlight
            
            # Safety check - ensure data exists
            if not self.data:
                return
            
            x = event.x
            
            if self.padding <= x <= self.width - self.padding:
                bar_spacing = (self.width - 2 * self.padding) / len(self.data)
                bar_index = int((x - self.padding) / bar_spacing)
                
                if 0 <= bar_index < len(self.data):
                    # Calculate bar position
                    bar_x = self._data_to_pixel_x(bar_index, -0.5, len(self.data) - 0.5)
                    bar_width = bar_spacing * self.bar_width_factor
                    value = self.data[bar_index]
                    
                    # Calculate y_max safely (handle edge cases)
                    max_val = max(self.data) if self.data else 1
                    if max_val == 0:
                        max_val = 1
                    y_max_display = max_val * 1.1
                    
                    y_top = self._data_to_pixel_y(value, 0, y_max_display)
                    y_base = self._data_to_pixel_y(0, 0, y_max_display)
                    
                    # Remove previous highlight
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                    
                    # Create highlight effect
                    try:
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
                    except tk.TclError:
                        current_highlight = None
                    
                    # Update tooltip - format value appropriately
                    if value == 0:
                        value_text = "0"
                    elif value == int(value):
                        value_text = f"{int(value):,}"
                    else:
                        value_text = f"{value:,.2f}"
                    
                    try:
                        label.config(text=f"{self.labels[bar_index]}\nValue: {value_text}")
                        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                        tooltip.deiconify()
                        tooltip.lift()
                    except tk.TclError:
                        pass  # Tooltip may have been destroyed
                else:
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                        current_highlight = None
                    try:
                        tooltip.withdraw()
                    except tk.TclError:
                        pass
        
        def on_leave(event):
            """Handle mouse leave events"""
            nonlocal current_highlight
            if current_highlight:
                try:
                    self.canvas.delete(current_highlight)
                except tk.TclError:
                    pass
                current_highlight = None
            try:
                tooltip.withdraw()
            except tk.TclError:
                pass
        
        # Bind events and register with resource manager (Requirements: 3.5)
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