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


from typing import List, Optional, Any
import tkinter as tk
from tkinter import ttk, filedialog
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class Histogram(Chart):
    """
    Histogram implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.8, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
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

    def plot(
        self,
        data: Any,
        bins: int = 10,
        value_column: Optional[str] = None
    ):
        """
        Plot a true histogram with the given data and number of bins.
        
        Supports pandas DataFrame, Series, or list input. When a DataFrame or Series
        is passed, the data is automatically converted to lists for plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of numeric values to plot
                - pandas DataFrame (uses value_column or first numeric column)
                - pandas Series (uses values)
            bins: Number of bins for the histogram (must be positive)
            value_column: Column name for values when data is a DataFrame.
                If not specified, uses the first numeric column.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty, bins is not positive, or data has zero range with multiple bins
            ImportError: If pandas DataFrame/Series is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.5)
        if DataValidator.is_pandas_dataframe(data):
            converted_values, _ = DataValidator.convert_dataframe_to_list(
                data,
                value_column=value_column,
                label_column=None,
                param_name="data"
            )
            data = converted_values
        # Handle pandas Series input (Requirements: 4.5)
        elif DataValidator.is_pandas_series(data):
            converted_values, _ = DataValidator.convert_series_to_list(
                data,
                param_name="data"
            )
            data = converted_values
        # When column parameters are provided with non-DataFrame data, ignore them
        # This maintains backward compatibility
        
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_numeric_list(
            data,
            allow_empty=False,
            allow_negative=True,  # Histograms can have negative values
            allow_nan=False,
            allow_inf=False,
            param_name="data"
        )
        
        # Validate bins parameter
        if bins is None:
            raise TypeError(
                "[ChartForgeTK] Error: bins cannot be None. "
                "Please provide a positive integer."
            )
        if not isinstance(bins, (int, float)):
            raise TypeError(
                f"[ChartForgeTK] Error: bins must be a number, "
                f"got {type(bins).__name__}."
            )
        bins = int(bins)
        if bins <= 0:
            raise ValueError(
                "[ChartForgeTK] Error: bins must be positive. "
                "Please provide a positive integer for the number of bins."
            )
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        self.data = validated_data.copy()
        self.bins = bins
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        self._calculate_bins()
        self._add_padding()
        self._set_labels()
        
        self.canvas.delete('all')
        self.bars.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_bars()
        self._add_interactive_effects()
        self._add_statistics()

    def _calculate_bins(self):
        """
        Calculate bins and frequencies with edge case handling.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - All identical values / zero range (Requirements: 2.2, 2.8)
        - Extreme outliers (Requirements: 2.3)
        """
        self.x_min, self.x_max = min(self.data), max(self.data)
        
        # Handle edge case: single data point (Requirements: 2.1)
        if len(self.data) == 1:
            # Create a single bin centered on the value
            value = self.data[0]
            # Use a reasonable range around the single value
            if value == 0:
                self.x_min, self.x_max = -0.5, 0.5
            else:
                spread = abs(value) * 0.1 if value != 0 else 0.5
                self.x_min = value - spread
                self.x_max = value + spread
            self.bins = 1  # Force single bin for single data point
            self.bin_edges = [self.x_min, self.x_max]
            self.frequencies = [1]
            self.y_min, self.y_max = 0, 1
            logger.debug(f"Single data point ({value}), created single bin")
            return
        
        # Handle edge case: all identical values / zero range (Requirements: 2.2, 2.8)
        if self.x_max == self.x_min:
            # All values are identical - create a single bin
            value = self.x_min
            if value == 0:
                self.x_min, self.x_max = -0.5, 0.5
            else:
                spread = abs(value) * 0.1 if value != 0 else 0.5
                self.x_min = value - spread
                self.x_max = value + spread
            self.bins = 1  # Force single bin for identical values
            self.bin_edges = [self.x_min, self.x_max]
            self.frequencies = [len(self.data)]
            self.y_min, self.y_max = 0, len(self.data)
            logger.debug(f"All values identical ({value}), created single bin with frequency {len(self.data)}")
            return
        
        # Normal case: calculate bin width
        bin_width = (self.x_max - self.x_min) / self.bins
        
        # Handle edge case: extreme outliers (Requirements: 2.3)
        # Check for outliers using IQR method
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]
        iqr = q3 - q1
        
        # If IQR is very small compared to range, we have outliers
        data_range = self.x_max - self.x_min
        if iqr > 0 and data_range > 3 * iqr:
            # Log warning about outliers but still include them
            logger.debug(
                f"Data contains outliers (range={data_range:.2f}, IQR={iqr:.2f}). "
                f"All data points will be visible."
            )
        
        self.bin_edges = [self.x_min + i * bin_width for i in range(self.bins + 1)]
        self.frequencies = [0] * self.bins
        
        for value in self.data:
            # Calculate bin index, ensuring it's within valid range
            if bin_width > 0:
                bin_index = int((value - self.x_min) / bin_width)
            else:
                bin_index = 0
            # Clamp to valid range (handles edge case where value == x_max)
            bin_index = max(0, min(bin_index, self.bins - 1))
            self.frequencies[bin_index] += 1
        
        self.y_min = 0
        self.y_max = max(self.frequencies) if self.frequencies else 1
        
        # Ensure y_max is at least 1 for proper rendering
        if self.y_max == 0:
            self.y_max = 1

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
        """
        Draw contiguous bars with smooth height animation.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - Zero frequencies (Requirements: 2.4)
        - Widget destruction during animation (Requirements: 6.3)
        
        Requirements: 3.2, 3.6
        """
        def ease(t):
            return t * t * (3 - 2 * t)
        
        # Handle edge case: single bin (Requirements: 2.1)
        if self.bins == 1:
            bar_width = (self.width - 2 * self.padding) / 2  # Center the single bar
        else:
            bar_width = (self.width - 2 * self.padding) / self.bins 
        
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
            
            for i, freq in enumerate(self.frequencies):
                x_left = self._data_to_pixel_x(self.bin_edges[i], self.x_min, self.x_max)
                x_right = self._data_to_pixel_x(self.bin_edges[i + 1], self.x_min, self.x_max)
                y_base = self._data_to_pixel_y(self.y_min, self.y_min, self.y_max)
                y_top = self._data_to_pixel_y(freq, self.y_min, self.y_max)
                y_current = y_base - (y_base - y_top) * progress
                
                color = self.style.get_histogram_color(i, self.bins)
                
                # Draw bar even if freq is 0 (will be zero-height) (Requirements: 2.4)
                if freq > 0:
                    try:
                        bar = self.canvas.create_rectangle(
                            x_left, y_current,
                            x_right, y_base,
                            fill=color,
                            outline="",  # Remove the outline to make bars contiguous
                            tags=('bar', f'bar_{i}')
                        )
                        self.bars.append(bar)
                    except tk.TclError:
                        pass
                
                    if progress == 1 and freq > 0:
                        try:
                            label = self.canvas.create_text(
                                (x_left + x_right) / 2, y_top - 10,
                                text=f"{freq}",
                                font=self.style.VALUE_FONT,
                                fill=self.style.TEXT,
                                anchor='s',
                                tags=('label', f'bar_{i}')
                            )
                            self.bars.append(label)
                        except tk.TclError:
                            pass
            
            if frame < total_frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
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
        self.tooltip = tooltip
        
        tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
        tooltip_frame.pack(fill='both', expand=True)
        label = ttk.Label(tooltip_frame, style='Tooltip.TLabel', font=self.style.TOOLTIP_FONT)
        label.pack(padx=8, pady=4)
        
        style = ttk.Style()
        style.configure('Tooltip.TFrame', background=self.style.TEXT, relief='solid', borderwidth=0)
        style.configure('Tooltip.TLabel', background=self.style.TEXT, foreground=self.style.BACKGROUND,
                       font=self.style.TOOLTIP_FONT)
        
        def on_motion(event):
            """Handle mouse motion events (Requirements: 7.2)"""
            # Safety check - ensure data exists
            if not self.data or not self.frequencies:
                return
            
            x, y = event.x, event.y
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                # Handle single bin case
                if self.bins == 1:
                    bar_width = (self.width - 2 * self.padding) / 2
                else:
                    bar_width = (self.width - 2 * self.padding) / self.bins
                
                bar_index = int((x - self.padding) / bar_width) if bar_width > 0 else 0
                bar_index = max(0, min(bar_index, self.bins - 1))  # Clamp to valid range
                
                if 0 <= bar_index < self.bins and self.frequencies[bar_index] > 0:
                    x_left = self._data_to_pixel_x(self.bin_edges[bar_index], self.x_min, self.x_max)
                    x_right = self._data_to_pixel_x(self.bin_edges[bar_index + 1], self.x_min, self.x_max)
                    y_base = self._data_to_pixel_y(self.y_min, self.y_min, self.y_max)
                    y_top = self._data_to_pixel_y(self.frequencies[bar_index], self.y_min, self.y_max)
                    
                    # Remove previous highlight
                    if self.current_highlight:
                        try:
                            self.canvas.delete(self.current_highlight)
                        except tk.TclError:
                            pass
                    
                    # Create highlight effect
                    try:
                        highlight = self.canvas.create_rectangle(
                            x_left - 2, y_top - 2,
                            x_right + 2, y_base + 2,
                            outline=self.style.ACCENT,
                            width=2,
                            tags=('highlight',)
                        )
                        self.current_highlight = highlight
                    except tk.TclError:
                        self.current_highlight = None
                    
                    # Update tooltip
                    try:
                        label.config(text=f"Range: [{self.bin_edges[bar_index]:.2f}, {self.bin_edges[bar_index+1]:.2f})\nFrequency: {self.frequencies[bar_index]}")
                        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                        tooltip.deiconify()
                        tooltip.lift()
                    except tk.TclError:
                        pass  # Tooltip may have been destroyed
                else:
                    if self.current_highlight:
                        try:
                            self.canvas.delete(self.current_highlight)
                        except tk.TclError:
                            pass
                        self.current_highlight = None
                    try:
                        tooltip.withdraw()
                    except tk.TclError:
                        pass
        
        def on_leave(event):
            """Handle mouse leave events"""
            if self.current_highlight:
                try:
                    self.canvas.delete(self.current_highlight)
                except tk.TclError:
                    pass
                self.current_highlight = None
            try:
                tooltip.withdraw()
            except tk.TclError:
                pass
        
        # Bind events and register with resource manager (Requirements: 3.5)
        motion_id = self.canvas.bind('<Motion>', on_motion)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)
    def _add_statistics(self):
        """
        Display statistical information with edge case handling.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        - All identical values (Requirements: 2.2)
        """
        # Safety check
        if not self.data:
            return
        
        try:
            stats_frame = ttk.Frame(self.canvas)
            stats_frame.place(relx=0.05, rely=0.05, anchor='nw')
            
            n = len(self.data)
            mean = sum(self.data) / n
            
            # Calculate median properly
            sorted_data = sorted(self.data)
            if n % 2 == 0:
                median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
            else:
                median = sorted_data[n // 2]
            
            # Calculate mode (handle edge case where all values are unique)
            try:
                mode = max(set(self.data), key=self.data.count)
            except ValueError:
                mode = self.data[0] if self.data else 0
            
            # Calculate standard deviation (handle single data point)
            if n > 1:
                std_dev = math.sqrt(sum((x - mean) ** 2 for x in self.data) / n)
            else:
                std_dev = 0.0
            
            ttk.Label(stats_frame, text=f"Mean: {mean:.2f}").pack(anchor='w')
            ttk.Label(stats_frame, text=f"Median: {median:.2f}").pack(anchor='w')
            ttk.Label(stats_frame, text=f"Mode: {mode:.2f}").pack(anchor='w')
            ttk.Label(stats_frame, text=f"Std Dev: {std_dev:.2f}").pack(anchor='w')
        except tk.TclError:
            pass  # Widget may have been destroyed

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