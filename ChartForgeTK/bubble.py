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


from typing import List, Tuple, Optional, Any
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class BubbleChart(Chart):
    """
    Bubble chart implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of (x, y, size) tuples
        self.min_radius = 5
        self.max_radius = 30
        self.animation_duration = 500
        self.bubbles = []  # Store canvas items
        self._tooltip = None  # Tooltip window reference
        
    def _convert_dataframe_to_tuples(
        self,
        df: Any,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        size_column: Optional[str] = None
    ) -> List[Tuple[float, float, float]]:
        """
        Convert a pandas DataFrame to a list of (x, y, size) tuples for bubble plotting.
        
        Args:
            df: pandas DataFrame to convert
            x_column: Column name for x values (defaults to first numeric column)
            y_column: Column name for y values (defaults to second numeric column)
            size_column: Column name for size values (defaults to third numeric column)
            
        Returns:
            List of (x, y, size) tuples
            
        Raises:
            TypeError: If df is not a DataFrame or columns contain non-numeric data
            ValueError: If DataFrame is empty, columns don't exist, or not enough numeric columns
            
        Requirements: 4.5
        """
        if not DataValidator.is_pandas_dataframe(df):
            raise TypeError(
                f"[ChartForgeTK] Error: data must be a pandas DataFrame, "
                f"got {type(df).__name__}."
            )
        
        pd = DataValidator._get_pandas()
        
        # Check for empty DataFrame
        if len(df) == 0:
            raise ValueError(
                "[ChartForgeTK] Error: data DataFrame is empty. "
                "Please provide data with at least one row."
            )
        
        available_columns = list(df.columns)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Determine x column
        if x_column is not None:
            if x_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{x_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            x_col = x_column
        else:
            if len(numeric_cols) < 1:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains no numeric columns. "
                    f"Expected at least three numeric columns for bubble chart. "
                    f"Available columns: {available_columns}"
                )
            x_col = numeric_cols[0]
        
        # Determine y column
        if y_column is not None:
            if y_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{y_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            y_col = y_column
        else:
            if len(numeric_cols) < 2:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains fewer than two numeric columns. "
                    f"Expected at least three numeric columns for bubble chart. "
                    f"Available columns: {available_columns}"
                )
            # Use second numeric column different from x_col
            y_col = numeric_cols[1] if numeric_cols[0] == x_col else numeric_cols[0]
            if y_col == x_col and len(numeric_cols) > 1:
                y_col = numeric_cols[1]
        
        # Determine size column
        if size_column is not None:
            if size_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{size_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            size_col = size_column
        else:
            if len(numeric_cols) < 3:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains fewer than three numeric columns. "
                    f"Expected at least three numeric columns for bubble chart. "
                    f"Available columns: {available_columns}"
                )
            # Use third numeric column different from x_col and y_col
            for col in numeric_cols:
                if col != x_col and col != y_col:
                    size_col = col
                    break
        
        # Validate that all columns are numeric
        for col, name in [(x_col, 'x'), (y_col, 'y'), (size_col, 'size')]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(
                    f"[ChartForgeTK] Error: Column '{col}' ({name}) contains non-numeric data. "
                    f"Expected numeric values for plotting."
                )
        
        # Convert to list of tuples, filtering NaN and infinity values
        result = []
        nan_count = 0
        inf_count = 0
        
        for idx, row in df.iterrows():
            x_val = float(row[x_col])
            y_val = float(row[y_col])
            size_val = float(row[size_col])
            
            # Check for NaN
            if math.isnan(x_val) or math.isnan(y_val) or math.isnan(size_val):
                nan_count += 1
                continue
            
            # Check for infinity
            if math.isinf(x_val) or math.isinf(y_val) or math.isinf(size_val):
                inf_count += 1
                continue
            
            result.append((x_val, y_val, size_val))
        
        # Log warnings for filtered values
        if nan_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {nan_count} row(s) with NaN value(s) filtered from data."
            )
        
        if inf_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {inf_count} row(s) with infinity value(s) filtered from data."
            )
        
        # Check if all values were filtered
        if not result:
            raise ValueError(
                "[ChartForgeTK] Error: data is empty after filtering NaN/infinity values. "
                "Please provide valid numeric data."
            )
        
        return result

    def plot(
        self,
        data: Any,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        size_column: Optional[str] = None
    ):
        """Plot the bubble chart with (x, y, size) data
        
        Supports pandas DataFrame or list of tuples input. When a DataFrame
        is passed, the data is automatically converted to list of tuples for plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of (x, y, size) tuples representing data points
                - pandas DataFrame (uses x_column, y_column, size_column or first three numeric columns)
            x_column: Column name for x values when data is a DataFrame.
                If not specified, uses the first numeric column.
            y_column: Column name for y values when data is a DataFrame.
                If not specified, uses the second numeric column.
            size_column: Column name for size values when data is a DataFrame.
                If not specified, uses the third numeric column.
            
        Raises:
            ValueError: If data is empty or contains negative sizes
            TypeError: If data is not a list of (x, y, size) number tuples
            ImportError: If pandas DataFrame is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.5)
        if DataValidator.is_pandas_dataframe(data):
            data = self._convert_dataframe_to_tuples(
                data,
                x_column=x_column,
                y_column=y_column,
                size_column=size_column
            )
        # When column parameters are provided with non-DataFrame data, ignore them
        # This maintains backward compatibility
        
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_tuple_list(
            data,
            expected_length=3,
            allow_empty=False,
            param_name="data"
        )
        
        # Additional validation: sizes cannot be negative
        for i, (x, y, size) in enumerate(validated_data):
            if size < 0:
                raise ValueError(
                    f"[ChartForgeTK] Error: data[{i}] has negative size ({size}). "
                    f"Bubble sizes must be non-negative."
                )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Create copy for immutability (Requirements: 9.1, 9.2)
        self.data = [tuple(point) for point in validated_data]
        
        # Handle edge case: single data point (Requirements: 2.1)
        if len(self.data) == 1:
            logger.debug("Single data point detected, adjusting ranges")
        
        # Calculate ranges
        x_values, y_values, sizes = zip(*self.data)
        self.x_min, self.x_max = min(x_values), max(x_values)
        self.y_min, self.y_max = min(y_values), max(y_values)
        size_min, size_max = min(sizes), max(sizes)
        
        # Handle edge case: identical values (Requirements: 2.2)
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        
        if x_range == 0:
            # All x values identical - create meaningful range
            x_padding = abs(self.x_max) * 0.1 if self.x_max != 0 else 1
            logger.debug(f"All x values identical ({self.x_max}), using default padding")
        else:
            x_padding = x_range * 0.1
            
        if y_range == 0:
            # All y values identical - create meaningful range
            y_padding = abs(self.y_max) * 0.1 if self.y_max != 0 else 1
            logger.debug(f"All y values identical ({self.y_max}), using default padding")
        else:
            y_padding = y_range * 0.1
        
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
        """Draw bubbles with smooth size animation.
        
        Requirements: 3.2, 3.6, 6.3
        """
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
            
            for item in self.bubbles:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
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
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
        total_frames = self.animation_duration // 16
        update_animation(0, total_frames)

    def _add_interactive_effects(self):
        """Add hover effects and tooltips with proper resource management.
        
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
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        current_highlight = None
        
        def on_motion(event):
            """Handle mouse motion events (Requirements: 7.2)"""
            nonlocal current_highlight
            
            # Safety check - ensure data exists
            if not self.data:
                return
            
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
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                    
                    try:
                        highlight = self.canvas.create_oval(
                            px - radius * 1.2, py - radius * 1.2,
                            px + radius * 1.2, py + radius * 1.2,
                            outline=self.style.ACCENT, width=2, tags=('highlight',)
                        )
                        current_highlight = highlight
                    except tk.TclError:
                        current_highlight = None
                    
                    x_val, y_val, size_val = self.data[closest_idx]
                    try:
                        label.config(text=f"X: {x_val:.1f}\nY: {y_val:.1f}\nSize: {size_val:.1f}")
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