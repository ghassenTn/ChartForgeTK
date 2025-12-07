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


from typing import List, Optional, Tuple
import tkinter as tk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class HeatMap(Chart):
    """
    Heatmap implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.cell_padding = 2
        self.interactive_cells = {}
        self._hover_tag = None
        self.color_scale = [
            "#053061",  # Dark blue
            "#2166ac",  # Blue
            "#4393c3",  # Light blue
            "#92c5de",  # Very light blue
            "#f7f7f7",  # White
            "#f4a582",  # Light red
            "#d6604d",  # Red
            "#b2182b",  # Dark red
            "#67001f"   # Very dark red
        ]

    def plot(self, data: List[List[float]], 
            row_labels: Optional[List[str]] = None,
            col_labels: Optional[List[str]] = None,
            title: Optional[str] = None):
        """Plot a heatmap.
        
        Args:
            data: 2D list of values to plot
            row_labels: Optional list of row labels
            col_labels: Optional list of column labels
            title: Optional title for the heatmap
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty or has inconsistent row lengths
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 9.1, 9.2, 9.3, 9.4
        """
        # Validate data is not None (Requirements: 1.1)
        if data is None:
            raise TypeError(
                "[ChartForgeTK] Error: data cannot be None. "
                "Please provide a 2D list of numeric values."
            )
        
        # Validate data is a list (Requirements: 1.3)
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: data must be a 2D list, "
                f"got {type(data).__name__}."
            )
        
        # Validate data is not empty (Requirements: 1.2)
        if not data or not data[0]:
            raise ValueError(
                "[ChartForgeTK] Error: data cannot be empty. "
                "Please provide a non-empty 2D list of numeric values."
            )
        
        # Validate each row is a list and has consistent length
        num_cols = len(data[0])
        for i, row in enumerate(data):
            if not isinstance(row, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: data[{i}] must be a list, "
                    f"got {type(row).__name__}."
                )
            if len(row) != num_cols:
                raise ValueError(
                    f"[ChartForgeTK] Error: data[{i}] has {len(row)} columns, "
                    f"expected {num_cols}. All rows must have the same length."
                )
            # Validate each value is numeric
            for j, value in enumerate(row):
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        f"[ChartForgeTK] Error: data[{i}][{j}] must be a number, "
                        f"got {type(value).__name__}."
                    )
                if math.isnan(value):
                    raise ValueError(
                        f"[ChartForgeTK] Error: data[{i}][{j}] is NaN. "
                        f"NaN values are not allowed."
                    )
                if math.isinf(value):
                    raise ValueError(
                        f"[ChartForgeTK] Error: data[{i}][{j}] is infinity. "
                        f"Infinite values are not allowed."
                    )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        self.clear()
        self.interactive_cells.clear()
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        # Store internal copy of data
        self._data = [[float(val) for val in row] for row in data]
        
        num_rows = len(self._data)
        num_cols = len(self._data[0])
        
        # Handle edge case: single data point (Requirements: 2.1)
        if num_rows == 1 and num_cols == 1:
            logger.debug("Single data point detected in heatmap")
        
        # Validate and set labels (Requirements: 9.3)
        if row_labels is not None:
            if not isinstance(row_labels, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: row_labels must be a list, "
                    f"got {type(row_labels).__name__}."
                )
            if len(row_labels) != num_rows:
                raise ValueError(
                    f"[ChartForgeTK] Error: Number of row_labels ({len(row_labels)}) "
                    f"must match number of rows ({num_rows})."
                )
            self._row_labels = [str(label) for label in row_labels]  # Create copy
        else:
            self._row_labels = [str(i) for i in range(num_rows)]
            
        if col_labels is not None:
            if not isinstance(col_labels, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: col_labels must be a list, "
                    f"got {type(col_labels).__name__}."
                )
            if len(col_labels) != num_cols:
                raise ValueError(
                    f"[ChartForgeTK] Error: Number of col_labels ({len(col_labels)}) "
                    f"must match number of columns ({num_cols})."
                )
            self._col_labels = [str(label) for label in col_labels]  # Create copy
        else:
            self._col_labels = [str(i) for i in range(num_cols)]
            
        if title:
            self.title = str(title)
        
        # Find data range for color scaling
        all_values = [val for row in self._data for val in row]
        data_min = min(all_values)
        data_max = max(all_values)
        
        # Handle edge case: all values identical (Requirements: 2.2)
        if data_min == data_max:
            logger.debug(f"All heatmap values identical ({data_min}), using default color range")
        
        # Calculate cell size
        available_width = self.width - 2 * self.padding - 100  # Extra space for labels
        available_height = self.height - 2 * self.padding - 100  # Extra space for labels
        cell_width = available_width / num_cols
        cell_height = available_height / num_rows
        
        # Draw column labels
        for j, label in enumerate(self._col_labels):
            x = self.padding + 100 + j * cell_width + cell_width/2
            y = self.padding + 50
            self.canvas.create_text(
                x, y,
                text=str(label),
                fill=self.style.TEXT,
                font=self.style.LABEL_FONT,
                angle=45 if len(str(label)) > 3 else 0
            )
        
        # Draw row labels
        for i, label in enumerate(self._row_labels):
            x = self.padding + 80
            y = self.padding + 100 + i * cell_height + cell_height/2
            self.canvas.create_text(
                x, y,
                text=str(label),
                fill=self.style.TEXT,
                font=self.style.LABEL_FONT,
                anchor='e'
            )
        
        # Draw cells
        for i in range(num_rows):
            for j in range(num_cols):
                value = self._data[i][j]
                
                # Calculate color based on value
                color_idx = (value - data_min) / (data_max - data_min) if data_max != data_min else 0.5
                color_idx = min(1.0, max(0.0, color_idx))  # Clamp to [0, 1]
                color = self._get_color(color_idx)
                
                # Calculate cell position
                x1 = self.padding + 100 + j * cell_width
                y1 = self.padding + 100 + i * cell_height
                x2 = x1 + cell_width - self.cell_padding
                y2 = y1 + cell_height - self.cell_padding
                
                # Create cell
                cell = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=self.style.BACKGROUND,
                    width=self.cell_padding,
                    tags=('cell', f'cell_{i}_{j}')
                )
                
                # Store cell info for interactivity
                self.interactive_cells[cell] = {
                    'row': i,
                    'col': j,
                    'value': value,
                    'row_label': self._row_labels[i],
                    'col_label': self._col_labels[j],
                    'color': color
                }
        
        # Draw color scale
        self._draw_color_scale(data_min, data_max)
        self._add_interactivity()
    
    def _get_color(self, value: float) -> str:
        """Get color for a value in [0, 1]."""
        if value >= 1.0:
            return self.color_scale[-1]
        elif value <= 0.0:
            return self.color_scale[0]
        
        idx = value * (len(self.color_scale) - 1)
        low_idx = int(idx)
        high_idx = min(low_idx + 1, len(self.color_scale) - 1)
        fraction = idx - low_idx
        
        try:
            # Interpolate between colors
            low_color = self._hex_to_rgb(self.color_scale[low_idx])
            high_color = self._hex_to_rgb(self.color_scale[high_idx])
            
            r = int(low_color[0] + fraction * (high_color[0] - low_color[0]))
            g = int(low_color[1] + fraction * (high_color[1] - low_color[1]))
            b = int(low_color[2] + fraction * (high_color[2] - low_color[2]))
            
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return self.color_scale[0]  # Fallback to first color
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _draw_color_scale(self, min_val: float, max_val: float):
        """Draw color scale legend."""
        scale_width = 20
        scale_height = self.height - 2 * self.padding - 200
        x = self.width - self.padding - scale_width - 20
        y = self.padding + 100
        
        # Draw gradient rectangles
        num_segments = 100
        segment_height = scale_height / num_segments
        for i in range(num_segments):
            value = 1 - (i / num_segments)
            color = self._get_color(value)
            
            self.canvas.create_rectangle(
                x, y + i * segment_height,
                x + scale_width, y + (i + 1) * segment_height,
                fill=color,
                outline='',
                tags='scale'
            )
        
        # Draw scale border
        self.canvas.create_rectangle(
            x, y,
            x + scale_width, y + scale_height,
            outline=self.style.TEXT,
            width=1,
            tags='scale'
        )
        
        # Draw scale labels
        self.canvas.create_text(
            x + scale_width + 10, y,
            text=f'{max_val:.2f}',
            anchor='w',
            fill=self.style.TEXT,
            font=self.style.LABEL_FONT,
            tags='scale'
        )
        
        self.canvas.create_text(
            x + scale_width + 10, y + scale_height,
            text=f'{min_val:.2f}',
            anchor='w',
            fill=self.style.TEXT,
            font=self.style.LABEL_FONT,
            tags='scale'
        )
    
    def _add_interactivity(self):
        """Add hover effects and tooltips to cells.
        
        Requirements: 3.1, 3.5, 7.1, 7.2, 7.6
        """
        def on_enter(event):
            """Handle mouse enter events (Requirements: 7.2)"""
            try:
                # Get the current cell
                item = event.widget.find_closest(event.x, event.y)[0]
                if item not in self.interactive_cells:
                    return
                    
                # Clean up old tooltip
                try:
                    self.canvas.delete('tooltip')
                except tk.TclError:
                    pass
                
                # Reset previous cell if exists
                if self._hover_tag:
                    try:
                        self.canvas.itemconfig(
                            self._hover_tag,
                            outline=self.style.BACKGROUND,
                            width=self.cell_padding
                        )
                    except tk.TclError:
                        pass
                
                # Get cell info
                info = self.interactive_cells[item]
                
                # Highlight current cell
                try:
                    self.canvas.itemconfig(
                        item,
                        outline=self.style.ACCENT,
                        width=2
                    )
                except tk.TclError:
                    return
                
                # Create simple tooltip
                x1, y1, x2, y2 = self.canvas.coords(item)
                tooltip_x = (x1 + x2) / 2
                tooltip_y = y1 - 5
                
                # Create background first
                self.canvas.create_rectangle(
                    tooltip_x - 60, tooltip_y - 40,
                    tooltip_x + 60, tooltip_y - 5,
                    fill=self.style.BACKGROUND,
                    outline=self.style.ACCENT,
                    width=1,
                    tags='tooltip'
                )
                
                # Add text on top
                self.canvas.create_text(
                    tooltip_x, tooltip_y - 22,
                    text=f"Value: {info['value']:.2f}",
                    anchor='center',
                    fill=self.style.TEXT,
                    font=self.style.TOOLTIP_FONT,
                    tags='tooltip'
                )
                
                self._hover_tag = item
                
            except tk.TclError as e:
                logger.debug(f"TclError in heatmap hover: {e}")
                try:
                    self.canvas.delete('tooltip')
                except tk.TclError:
                    pass
                if self._hover_tag:
                    try:
                        self.canvas.itemconfig(
                            self._hover_tag,
                            outline=self.style.BACKGROUND,
                            width=self.cell_padding
                        )
                    except tk.TclError:
                        pass
                self._hover_tag = None
            except Exception as e:
                logger.warning(f"Hover error in heatmap: {e}")
                try:
                    self.canvas.delete('tooltip')
                except tk.TclError:
                    pass
                if self._hover_tag:
                    try:
                        self.canvas.itemconfig(
                            self._hover_tag,
                            outline=self.style.BACKGROUND,
                            width=self.cell_padding
                        )
                    except tk.TclError:
                        pass
                self._hover_tag = None

        def on_leave(event):
            """Handle mouse leave events"""
            # Simple cleanup
            if self._hover_tag:
                try:
                    self.canvas.itemconfig(
                        self._hover_tag,
                        outline=self.style.BACKGROUND,
                        width=self.cell_padding
                    )
                except tk.TclError:
                    pass
            try:
                self.canvas.delete('tooltip')
            except tk.TclError:
                pass
            self._hover_tag = None

        # Only bind enter/leave events
        self.canvas.tag_bind('cell', '<Enter>', on_enter)
        self.canvas.tag_bind('cell', '<Leave>', on_leave)
