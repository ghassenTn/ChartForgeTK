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
from tkinter import ttk
import math
import statistics
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class BoxPlot(Chart):
    """
    Box plot implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.7, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of lists (each sublist is a dataset)
        self.labels = []
        self.box_width_factor = 0.6  # Width of boxes relative to spacing
        self.animation_duration = 500
        self.elements = []  # Store canvas items
        self._tooltip = None  # Tooltip window reference
        
    def _convert_dataframe_to_datasets(
        self,
        df: Any,
        columns: Optional[List[str]] = None
    ) -> tuple:
        """
        Convert a pandas DataFrame to a list of datasets for box plotting.
        
        Args:
            df: pandas DataFrame to convert
            columns: Optional list of column names to use. If not specified,
                uses all numeric columns.
            
        Returns:
            Tuple of (list of datasets, list of column names as labels)
            
        Raises:
            TypeError: If df is not a DataFrame or columns contain non-numeric data
            ValueError: If DataFrame is empty or columns don't exist
            
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
        
        # Determine which columns to use
        if columns is not None:
            # Validate specified columns exist
            for col in columns:
                if col not in df.columns:
                    raise ValueError(
                        f"[ChartForgeTK] Error: Column '{col}' not found in DataFrame. "
                        f"Available columns: {available_columns}"
                    )
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise TypeError(
                        f"[ChartForgeTK] Error: Column '{col}' contains non-numeric data. "
                        f"Expected numeric values for plotting."
                    )
            cols_to_use = columns
        else:
            # Use all numeric columns
            cols_to_use = df.select_dtypes(include=['number']).columns.tolist()
            if not cols_to_use:
                raise TypeError(
                    "[ChartForgeTK] Error: data DataFrame contains no numeric columns. "
                    f"Expected at least one numeric column for box plot. "
                    f"Available columns: {available_columns}"
                )
        
        # Extract data from each column, filtering NaN and infinity values
        datasets = []
        labels = []
        
        for col in cols_to_use:
            col_values = []
            nan_count = 0
            inf_count = 0
            
            for value in df[col]:
                float_val = float(value)
                
                if math.isnan(float_val):
                    nan_count += 1
                    continue
                
                if math.isinf(float_val):
                    inf_count += 1
                    continue
                
                col_values.append(float_val)
            
            # Log warnings for filtered values
            if nan_count > 0:
                logger.warning(
                    f"[ChartForgeTK] Warning: {nan_count} NaN value(s) filtered from column '{col}'."
                )
            
            if inf_count > 0:
                logger.warning(
                    f"[ChartForgeTK] Warning: {inf_count} infinity value(s) filtered from column '{col}'."
                )
            
            # Only add column if it has valid values
            if col_values:
                datasets.append(col_values)
                labels.append(str(col))
        
        if not datasets:
            raise ValueError(
                "[ChartForgeTK] Error: data is empty after filtering NaN/infinity values. "
                "Please provide valid numeric data."
            )
        
        return (datasets, labels)

    def plot(
        self,
        data: Any,
        labels: Optional[List[str]] = None,
        columns: Optional[List[str]] = None
    ):
        """
        Plot the box plot with multiple datasets.
        
        Supports pandas DataFrame or list of lists input. When a DataFrame
        is passed, each numeric column becomes a separate box plot.
        
        Args:
            data: Data to plot. Can be:
                - List of lists of numeric values (each sublist is a dataset)
                - pandas DataFrame (each numeric column becomes a dataset)
            labels: Optional list of labels for each dataset.
                Ignored when data is a DataFrame (column names are used).
            columns: Optional list of column names when data is a DataFrame.
                If not specified, uses all numeric columns.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty, datasets are too small, or labels mismatch
            ImportError: If pandas DataFrame is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.5)
        if DataValidator.is_pandas_dataframe(data):
            converted_data, converted_labels = self._convert_dataframe_to_datasets(
                data,
                columns=columns
            )
            data = converted_data
            # Use converted labels (column names) if no explicit labels provided
            if labels is None:
                labels = converted_labels
        # When column parameters are provided with non-DataFrame data, ignore them
        # This maintains backward compatibility
        
        # Validate data is not None (Requirements: 1.1)
        if data is None:
            raise TypeError(
                "[BoxPlot] Error: data cannot be None. "
                "Please provide a list of lists of numeric values."
            )
        
        # Validate data is a list (Requirements: 1.3)
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[BoxPlot] Error: data must be a list of lists, "
                f"got {type(data).__name__}. Please provide a list of lists of numeric values."
            )
        
        # Validate data is not empty (Requirements: 1.2)
        if not data:
            raise ValueError(
                "[BoxPlot] Error: data cannot be empty. "
                "Please provide at least one dataset."
            )
        
        # Validate each dataset (Requirements: 1.3, 2.7)
        validated_data = []
        for i, dataset in enumerate(data):
            # Validate each dataset using DataValidator
            validated_dataset = DataValidator.validate_numeric_list(
                dataset,
                allow_empty=False,
                allow_negative=True,  # Box plots support negative values
                allow_nan=False,
                allow_inf=False,
                param_name=f"data[{i}]"
            )
            
            # Edge case: dataset with fewer than 2 values (Requirements: 2.7)
            if len(validated_dataset) < 2:
                raise ValueError(
                    f"[BoxPlot] Error: data[{i}] has only {len(validated_dataset)} value(s). "
                    f"BoxPlot requires at least 2 values per dataset to compute statistics. "
                    f"Please provide datasets with at least 2 values."
                )
            
            validated_data.append(validated_dataset)
        
        # Validate labels (Requirements: 1.4)
        validated_labels = DataValidator.validate_labels(labels, len(validated_data), param_name="labels")
        
        # If labels were None, generate default labels
        if labels is None:
            validated_labels = [f"Group {i+1}" for i in range(len(validated_data))]
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        self.data = [dataset.copy() for dataset in validated_data]
        self.labels = validated_labels.copy()
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Calculate ranges with edge case handling
        all_values = [x for sublist in self.data for x in sublist]
        self.x_min, self.x_max = -0.5, len(self.data) - 0.5
        self.y_min, self.y_max = min(all_values), max(all_values)
        
        # Handle edge case: all values are identical (Requirements: 2.2)
        if self.y_max == self.y_min:
            # All values are identical - create meaningful range
            value = self.y_min
            if value == 0:
                self.y_min = -1
                self.y_max = 1
            else:
                # Use 20% padding above and below the value
                padding = abs(value) * 0.2
                self.y_min = value - padding
                self.y_max = value + padding
            logger.debug(f"All data values identical ({value}), adjusted y-axis range")
        else:
            # Normal case: add 10% padding
            y_padding = (self.y_max - self.y_min) * 0.1
            self.y_min -= y_padding
            self.y_max += y_padding
        
        # Set labels
        self.title = "Box Plot"
        self.x_label = "Groups"
        self.y_label = "Values"
        
        # Clear previous content
        self.canvas.delete('all')
        self.elements.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_boxes()
        self._add_interactive_effects()

    def _calculate_box_statistics(self, dataset: List[float]) -> dict:
        """
        Calculate box plot statistics for a dataset.
        
        Handles edge cases:
        - Small datasets (2-4 values) (Requirements: 2.7)
        - Identical values (Requirements: 2.2)
        
        Args:
            dataset: List of numeric values (must have at least 2 values)
            
        Returns:
            dict with keys: q1, median, q3, iqr, lower_whisker, upper_whisker, outliers
        """
        n = len(dataset)
        sorted_data = sorted(dataset)
        
        # Calculate median
        median = statistics.median(sorted_data)
        
        # Handle small datasets (Requirements: 2.7)
        if n == 2:
            # With 2 values, use min as Q1, max as Q3
            q1 = sorted_data[0]
            q3 = sorted_data[1]
        elif n == 3:
            # With 3 values, Q1 = min, Q3 = max
            q1 = sorted_data[0]
            q3 = sorted_data[2]
        elif n == 4:
            # With 4 values, Q1 = avg of first two, Q3 = avg of last two
            q1 = (sorted_data[0] + sorted_data[1]) / 2
            q3 = (sorted_data[2] + sorted_data[3]) / 2
        else:
            # Standard quartile calculation for n >= 5
            quantiles = statistics.quantiles(sorted_data, n=4)
            q1 = quantiles[0]
            q3 = quantiles[2]
        
        iqr = q3 - q1
        
        # Handle identical values case (Requirements: 2.2)
        if iqr == 0:
            # All values in IQR range are identical
            lower_whisker = min(sorted_data)
            upper_whisker = max(sorted_data)
            outliers = []
        else:
            # Standard whisker calculation
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            lower_whisker = max(min(sorted_data), lower_bound)
            upper_whisker = min(max(sorted_data), upper_bound)
            
            # Find actual whisker values (closest data points within bounds)
            lower_whisker = min([x for x in sorted_data if x >= lower_bound], default=min(sorted_data))
            upper_whisker = max([x for x in sorted_data if x <= upper_bound], default=max(sorted_data))
            
            # Identify outliers
            outliers = [y for y in sorted_data if y < lower_bound or y > upper_bound]
        
        return {
            'q1': q1,
            'median': median,
            'q3': q3,
            'iqr': iqr,
            'lower_whisker': lower_whisker,
            'upper_whisker': upper_whisker,
            'outliers': outliers,
            'min': min(sorted_data),
            'max': max(sorted_data)
        }

    def _animate_boxes(self):
        """
        Draw box plots with smooth height animation.
        
        Handles edge cases:
        - Single dataset (Requirements: 2.1)
        - Small datasets (Requirements: 2.7)
        - Identical values (Requirements: 2.2)
        
        Requirements: 3.2, 3.6
        """
        def ease(t):
            return t * t * (3 - 2 * t)
        
        # Handle edge case: single dataset (Requirements: 2.1)
        if len(self.data) == 1:
            box_spacing = (self.width - 2 * self.padding) / 2  # Center the single box
            box_width = box_spacing * self.box_width_factor
        else:
            box_spacing = (self.width - 2 * self.padding) / len(self.data)
            box_width = box_spacing * self.box_width_factor
        
        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            
            # Clear previous elements
            for item in self.elements:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.elements.clear()
            
            for i, dataset in enumerate(self.data):
                x = self._data_to_pixel_x(i, self.x_min, self.x_max)
                color = self.style.get_gradient_color(i, len(self.data))
                
                # Calculate box plot statistics with edge case handling
                stats = self._calculate_box_statistics(dataset)
                q1 = stats['q1']
                median = stats['median']
                q3 = stats['q3']
                iqr = stats['iqr']
                lower_whisker = stats['lower_whisker']
                upper_whisker = stats['upper_whisker']
                outliers = stats['outliers']
                
                # Convert to pixel coordinates
                y_q1 = self._data_to_pixel_y(q1, self.y_min, self.y_max)
                y_q3 = self._data_to_pixel_y(q3, self.y_min, self.y_max)
                y_median = self._data_to_pixel_y(median, self.y_min, self.y_max)
                y_lower = self._data_to_pixel_y(lower_whisker, self.y_min, self.y_max)
                y_upper = self._data_to_pixel_y(upper_whisker, self.y_min, self.y_max)
                
                # Handle identical values case - ensure box has minimum height (Requirements: 2.2)
                if iqr == 0:
                    # Create a thin box for identical values
                    box_height_pixels = 4  # Minimum visible height
                    y_q1 = y_median + box_height_pixels / 2
                    y_q3 = y_median - box_height_pixels / 2
                    box_height = 0  # No animation needed for height
                else:
                    box_height = (y_q1 - y_q3) * progress
                
                # Shadow (only if box has height)
                if y_q1 > y_q3:
                    shadow = self.canvas.create_rectangle(
                        x - box_width/2 + 2, y_q3 + 2,
                        x + box_width/2 + 2, y_q1 + 2,
                        fill=self.style.create_shadow(color),
                        outline="",
                        tags=('shadow', f'box_{i}')
                    )
                    self.elements.append(shadow)
                
                # Box (Requirements: 2.2 - handles identical values)
                if iqr == 0:
                    # Draw thin box for identical values
                    box = self.canvas.create_rectangle(
                        x - box_width/2, y_q3,
                        x + box_width/2, y_q1,
                        fill=color,
                        outline=self.style.adjust_brightness(color, 0.8),
                        tags=('box', f'box_{i}')
                    )
                else:
                    # Animate box height
                    animated_y_q3 = y_q3 + (y_q1 - y_q3) * (1 - progress) / 2
                    animated_y_q1 = y_q1 - (y_q1 - y_q3) * (1 - progress) / 2
                    box = self.canvas.create_rectangle(
                        x - box_width/2, animated_y_q3,
                        x + box_width/2, animated_y_q1,
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
                
                # Lower whisker
                lower_whisker_item = self.canvas.create_line(
                    x, y_q1, x, y_q1 + (y_lower - y_q1) * whisker_progress,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('whisker', f'box_{i}')
                )
                self.elements.append(lower_whisker_item)
                
                # Upper whisker
                upper_whisker_item = self.canvas.create_line(
                    x, y_q3, x, y_q3 - (y_q3 - y_upper) * whisker_progress,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('whisker', f'box_{i}')
                )
                self.elements.append(upper_whisker_item)
                
                # Whisker caps
                lower_cap = self.canvas.create_line(
                    x - box_width/4, y_lower,
                    x + box_width/4, y_lower,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('cap', f'box_{i}')
                )
                self.elements.append(lower_cap)
                
                upper_cap = self.canvas.create_line(
                    x - box_width/4, y_upper,
                    x + box_width/4, y_upper,
                    fill=self.style.TEXT,
                    width=1,
                    tags=('cap', f'box_{i}')
                )
                self.elements.append(upper_cap)
                
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
                # Handle single dataset case
                if len(self.data) == 1:
                    box_spacing = (self.width - 2 * self.padding) / 2
                else:
                    box_spacing = (self.width - 2 * self.padding) / len(self.data)
                box_width = box_spacing * self.box_width_factor
                box_index = int((x - self.padding) / box_spacing)
                
                if 0 <= box_index < len(self.data):
                    dataset = self.data[box_index]
                    px = self._data_to_pixel_x(box_index, self.x_min, self.x_max)
                    
                    # Use the same statistics calculation method
                    stats = self._calculate_box_statistics(dataset)
                    q1 = stats['q1']
                    median = stats['median']
                    q3 = stats['q3']
                    
                    y_q1 = self._data_to_pixel_y(q1, self.y_min, self.y_max)
                    y_q3 = self._data_to_pixel_y(q3, self.y_min, self.y_max)
                    
                    # Remove previous highlight
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                    
                    # Create highlight effect
                    try:
                        highlight = self.canvas.create_rectangle(
                            px - box_width/2 - 2, y_q3 - 2,
                            px + box_width/2 + 2, y_q1 + 2,
                            outline=self.style.ACCENT,
                            width=2,
                            tags=('highlight',)
                        )
                        current_highlight = highlight
                    except tk.TclError:
                        current_highlight = None
                    
                    # Update tooltip with statistics
                    try:
                        label.config(text=f"{self.labels[box_index]}\n"
                                        f"Min: {stats['min']:.1f}\n"
                                        f"Q1: {q1:.1f}\n"
                                        f"Median: {median:.1f}\n"
                                        f"Q3: {stats['q3']:.1f}\n"
                                        f"Max: {stats['max']:.1f}")
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