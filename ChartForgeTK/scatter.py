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

"""
ScatterPlot implementation with comprehensive input validation and edge case handling.

Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.6, 9.1, 9.2
"""

from typing import List, Optional, Union, Tuple, Any
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class ScatterPlot(Chart):
    """
    Scatter plot implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of (x, y) tuples
        self.point_radius = 5
        self.animation_duration = 500
        self.points = []
        self._tooltip = None  # Tooltip window reference
        # Initialize range variables
        self.x_min = self.x_max = self.y_min = self.y_max = 0

    def _convert_dataframe_to_tuples(
        self,
        df: Any,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> List[Tuple[float, float]]:
        """
        Convert a pandas DataFrame to a list of (x, y) tuples for scatter plotting.
        
        Args:
            df: pandas DataFrame to convert
            x_column: Column name for x values (defaults to first numeric column)
            y_column: Column name for y values (defaults to second numeric column)
            
        Returns:
            List of (x, y) tuples
            
        Raises:
            TypeError: If df is not a DataFrame or columns contain non-numeric data
            ValueError: If DataFrame is empty, columns don't exist, or not enough numeric columns
            
        Requirements: 4.3, 4.5
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
        
        # Determine x column
        if x_column is not None:
            if x_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{x_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            x_col = x_column
        else:
            # Find first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) < 1:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains no numeric columns. "
                    f"Expected at least two numeric columns for scatter plot. "
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
            # Find second numeric column (different from x_col)
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) < 2:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains fewer than two numeric columns. "
                    f"Expected at least two numeric columns for scatter plot. "
                    f"Available columns: {available_columns}"
                )
            # Use second numeric column (or first if x_col was explicitly specified and is not numeric_cols[0])
            y_col = numeric_cols[1] if numeric_cols[0] == x_col else numeric_cols[0]
            if y_col == x_col and len(numeric_cols) > 1:
                y_col = numeric_cols[1]
        
        # Validate that both columns are numeric
        if not pd.api.types.is_numeric_dtype(df[x_col]):
            raise TypeError(
                f"[ChartForgeTK] Error: Column '{x_col}' contains non-numeric data. "
                f"Expected numeric values for plotting."
            )
        if not pd.api.types.is_numeric_dtype(df[y_col]):
            raise TypeError(
                f"[ChartForgeTK] Error: Column '{y_col}' contains non-numeric data. "
                f"Expected numeric values for plotting."
            )
        
        # Convert to list of tuples, filtering NaN and infinity values
        result = []
        nan_count = 0
        inf_count = 0
        
        for idx, row in df.iterrows():
            x_val = float(row[x_col])
            y_val = float(row[y_col])
            
            # Check for NaN
            if math.isnan(x_val) or math.isnan(y_val):
                nan_count += 1
                continue
            
            # Check for infinity
            if math.isinf(x_val) or math.isinf(y_val):
                inf_count += 1
                continue
            
            result.append((x_val, y_val))
        
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
        y_column: Optional[str] = None
    ):
        """
        Plot the scatter chart with the given (x, y) data.
        
        Supports pandas DataFrame or list of tuples input. When a DataFrame
        is passed, the data is automatically converted to list of tuples for plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of (x, y) tuples representing data points
                - pandas DataFrame (uses x_column and y_column or first two numeric columns)
            x_column: Column name for x values when data is a DataFrame.
                If not specified, uses the first numeric column.
            y_column: Column name for y values when data is a DataFrame.
                If not specified, uses the second numeric column.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty or tuples have incorrect length
            ImportError: If pandas DataFrame is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 4.3, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.3, 4.5)
        if DataValidator.is_pandas_dataframe(data):
            data = self._convert_dataframe_to_tuples(data, x_column, y_column)
        # When column parameters are provided with non-DataFrame data, ignore them (Requirements: 4.5)
        # This maintains backward compatibility - no action needed, just proceed with list validation
        
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_tuple_list(
            data,
            expected_length=2,
            allow_empty=False,
            param_name="data"
        )
        
        # Create copy for immutability (Requirements: 9.1, 9.2)
        self.data = [tuple(point) for point in validated_data]
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Calculate ranges and store as instance variables
        x_values, y_values = zip(*self.data)
        self.x_min, self.x_max = min(x_values), max(x_values)
        self.y_min, self.y_max = min(y_values), max(y_values)
        
        # Handle edge case: single data point (Requirements: 2.1)
        if len(self.data) == 1:
            # Single point - create meaningful axis ranges
            x_val, y_val = self.data[0]
            if x_val == 0:
                self.x_min, self.x_max = -1, 1
            else:
                x_padding = abs(x_val) * 0.5 if x_val != 0 else 1
                self.x_min = x_val - x_padding
                self.x_max = x_val + x_padding
            
            if y_val == 0:
                self.y_min, self.y_max = -1, 1
            else:
                y_padding = abs(y_val) * 0.5 if y_val != 0 else 1
                self.y_min = y_val - y_padding
                self.y_max = y_val + y_padding
            logger.debug(f"Single data point detected, using ranges x=[{self.x_min}, {self.x_max}], y=[{self.y_min}, {self.y_max}]")
        else:
            # Handle edge case: all x values are identical (Requirements: 2.2)
            if self.x_max == self.x_min:
                if self.x_min == 0:
                    self.x_min, self.x_max = -1, 1
                else:
                    x_padding = abs(self.x_min) * 0.2 if self.x_min != 0 else 1
                    self.x_min -= x_padding
                    self.x_max += x_padding
                logger.debug(f"All x values identical, adjusted x-axis range to [{self.x_min}, {self.x_max}]")
            else:
                # Normal case: add 10% padding
                x_padding = (self.x_max - self.x_min) * 0.1
                self.x_min -= x_padding
                self.x_max += x_padding
            
            # Handle edge case: all y values are identical (Requirements: 2.2)
            if self.y_max == self.y_min:
                if self.y_min == 0:
                    self.y_min, self.y_max = -1, 1
                else:
                    y_padding = abs(self.y_min) * 0.2 if self.y_min != 0 else 1
                    self.y_min -= y_padding
                    self.y_max += y_padding
                logger.debug(f"All y values identical, adjusted y-axis range to [{self.y_min}, {self.y_max}]")
            else:
                # Normal case: add 10% padding
                y_padding = (self.y_max - self.y_min) * 0.1
                self.y_min -= y_padding
                self.y_max += y_padding
        
        # Handle edge case: extreme outliers (Requirements: 2.3)
        # The padding already ensures all points are visible, but we log if outliers exist
        if len(self.data) > 2:
            x_values_sorted = sorted(x_values)
            y_values_sorted = sorted(y_values)
            x_iqr = x_values_sorted[len(x_values_sorted) * 3 // 4] - x_values_sorted[len(x_values_sorted) // 4] if len(x_values_sorted) >= 4 else 0
            y_iqr = y_values_sorted[len(y_values_sorted) * 3 // 4] - y_values_sorted[len(y_values_sorted) // 4] if len(y_values_sorted) >= 4 else 0
            
            if x_iqr > 0:
                x_lower = x_values_sorted[len(x_values_sorted) // 4] - 1.5 * x_iqr
                x_upper = x_values_sorted[len(x_values_sorted) * 3 // 4] + 1.5 * x_iqr
                x_outliers = [x for x in x_values if x < x_lower or x > x_upper]
                if x_outliers:
                    logger.debug(f"Detected {len(x_outliers)} x-axis outliers, all points will be visible")
            
            if y_iqr > 0:
                y_lower = y_values_sorted[len(y_values_sorted) // 4] - 1.5 * y_iqr
                y_upper = y_values_sorted[len(y_values_sorted) * 3 // 4] + 1.5 * y_iqr
                y_outliers = [y for y in y_values if y < y_lower or y > y_upper]
                if y_outliers:
                    logger.debug(f"Detected {len(y_outliers)} y-axis outliers, all points will be visible")
        
        # Clear previous content
        self.canvas.delete('all')
        self.points.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_points(self.x_min, self.x_max, self.y_min, self.y_max)
        self._add_interactive_effects()


    def _animate_points(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """
        Draw points with smooth fade-in animation.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - Identical values (Requirements: 2.2)
        - Extreme outliers (Requirements: 2.3)
        
        Requirements: 3.2, 3.6
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
            
            # Clear previous points
            for item in self.points:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.points.clear()
            
            for i, (x, y) in enumerate(self.data):
                px = self._data_to_pixel_x(x, x_min, x_max)
                py = self._data_to_pixel_y(y, y_min, y_max)
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Draw shadow
                try:
                    shadow = self.canvas.create_oval(
                        px - self.point_radius + 2,
                        py - self.point_radius + 2,
                        px + self.point_radius + 2,
                        py + self.point_radius + 2,
                        fill=self.style.create_shadow(color),
                        outline="",
                        tags=('shadow', f'point_{i}')
                    )
                    self.points.append(shadow)
                    
                    point = self.canvas.create_oval(
                        px - self.point_radius,
                        py - self.point_radius,
                        px + self.point_radius,
                        py + self.point_radius,
                        fill=color,
                        outline=self.style.adjust_brightness(color, 0.8),
                        tags=('point', f'point_{i}')
                    )
                    self.points.append(point)
                    
                    if progress == 1:
                        label = self.canvas.create_text(
                            px, py - 15,
                            text=f"({x:.1f}, {y:.1f})",
                            font=self.style.VALUE_FONT,
                            fill=self.style.TEXT,
                            anchor='s',
                            tags=('label', f'point_{i}')
                        )
                        self.points.append(label)
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
            
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                closest_idx = -1
                min_dist = float('inf')
                
                # Use stored instance variables for coordinate conversion
                for i, (dx, dy) in enumerate(self.data):
                    px = self._data_to_pixel_x(dx, self.x_min, self.x_max)
                    py = self._data_to_pixel_y(dy, self.y_min, self.y_max)
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist and dist < 20:
                        min_dist = dist
                        closest_idx = i
                
                if closest_idx >= 0:
                    px = self._data_to_pixel_x(self.data[closest_idx][0], self.x_min, self.x_max)
                    py = self._data_to_pixel_y(self.data[closest_idx][1], self.y_min, self.y_max)
                    
                    try:
                        if current_highlight:
                            self.canvas.delete(current_highlight)
                        
                        highlight = self.canvas.create_oval(
                            px - self.point_radius * 1.5,
                            py - self.point_radius * 1.5,
                            px + self.point_radius * 1.5,
                            py + self.point_radius * 1.5,
                            outline=self.style.ACCENT,
                            width=2,
                            tags=('highlight',)
                        )
                        current_highlight = highlight
                        
                        x_val, y_val = self.data[closest_idx]
                        label.config(text=f"X: {x_val:.1f}\nY: {y_val:.1f}")
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
        
        def on_leave(event):
            """Handle mouse leave events"""
            nonlocal current_highlight
            try:
                if current_highlight:
                    self.canvas.delete(current_highlight)
                    current_highlight = None
                tooltip.withdraw()
            except tk.TclError:
                pass
        
        # Bind events and register with resource manager (Requirements: 3.5)
        motion_id = self.canvas.bind('<Motion>', on_motion)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)
