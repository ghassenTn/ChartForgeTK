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


from typing import List, Dict, Union, Optional
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class TableauChart(Chart):
    """
    A Tableau-style chart for displaying tabular data with interactive features like sorting and filtering.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.6, 9.1, 9.2
    
    Attributes:
        parent (tk.Widget): The parent widget.
        width (int): The width of the chart.
        height (int): The height of the chart.
        display_mode (str): The display mode ('frame' or 'canvas').
        theme (str): The theme of the chart ('dark' or 'light').
        data (List[Dict[str, Union[str, float, int]]]): The data to be displayed.
        columns (List[str]): The columns to be displayed.
        sort_column (Optional[str]): The column currently used for sorting.
        sort_ascending (bool): The sorting order (ascending or descending).
        filters (Dict[str, str]): The filters applied to the data.
        animation_duration (int): The duration of the animation in milliseconds.
        elements (List[int]): The canvas elements.
        column_widths (Dict[str, int]): The calculated widths of the columns.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None, width: int = 800, height: int = 600, 
                 display_mode: str = 'frame', theme: str = 'dark'):
        """
        Initialize the TableauChart.

        Args:
            parent (Optional[tk.Widget]): The parent widget.
            width (int): The width of the chart.
            height (int): The height of the chart.
            display_mode (str): The display mode ('frame' or 'canvas').
            theme (str): The theme of the chart ('dark' or 'light').
        """
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.parent = parent
        self.data = []
        self.columns = []
        self.sort_column = None
        self.sort_ascending = True
        self.filters = {}
        self.animation_duration = 300
        self.elements = []
        self.column_widths = {}
        
    def plot(self, data: List[Dict[str, Union[str, float, int]]], columns: Optional[List[str]] = None):
        """
        Plot a Tableau-style table with given data and optional column subset.

        Args:
            data (List[Dict[str, Union[str, float, int]]]): The data to be displayed.
            columns (Optional[List[str]]): The columns to be displayed.

        Raises:
            TypeError: If data is None or not a list of dictionaries
            ValueError: If data is empty or if specified columns do not exist in data.
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.6, 9.1, 9.2, 9.3, 9.4
        """
        # Validate data is not None (Requirements: 1.1)
        if data is None:
            raise TypeError(
                "[ChartForgeTK] Error: data cannot be None. "
                "Please provide a list of dictionaries."
            )
        
        # Validate data is a list (Requirements: 1.3)
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: data must be a list, "
                f"got {type(data).__name__}."
            )
        
        # Validate data is not empty (Requirements: 1.2)
        if not data:
            raise ValueError(
                "[ChartForgeTK] Error: data cannot be empty. "
                "Please provide at least one row of data."
            )
        
        # Validate all items are dictionaries
        for i, row in enumerate(data):
            if not isinstance(row, dict):
                raise TypeError(
                    f"[ChartForgeTK] Error: data[{i}] must be a dictionary, "
                    f"got {type(row).__name__}."
                )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Create deep copy for immutability (Requirements: 9.1, 9.2)
        self.data = [dict(row) for row in data]
        available_columns = list(self.data[0].keys())
        
        # Validate and copy columns list (Requirements: 9.3)
        if columns is not None:
            if not isinstance(columns, (list, tuple)):
                raise TypeError(
                    f"[ChartForgeTK] Error: columns must be a list, "
                    f"got {type(columns).__name__}."
                )
            self.columns = [str(col) for col in columns]
            
            # Validate all specified columns exist
            for col in self.columns:
                if col not in available_columns:
                    raise ValueError(
                        f"[ChartForgeTK] Error: Column '{col}' does not exist in data. "
                        f"Available columns: {available_columns}"
                    )
        else:
            self.columns = available_columns
        
        # Handle edge case: single row (Requirements: 2.1)
        if len(self.data) == 1:
            logger.debug("Single row detected in TableauChart")
        
        self._clear_canvas()
        self._calculate_column_widths()
        self._draw_table_header()
        self._animate_rows()
        self._add_interactive_effects()

    def _clear_canvas(self):
        """Clear the canvas and reset elements."""
        self.canvas.delete('all')
        self.elements.clear()
        self.filters.clear()

    def _calculate_column_widths(self):
        """Calculate dynamic column widths based on content."""
        self.column_widths = {}
        for col in self.columns:
            max_len = max(len(str(col)), max([len(str(row.get(col, ''))) for row in self.data]) + 2)
            self.column_widths[col] = min(max_len * 8, (self.width - 2 * self.padding) // len(self.columns))

    def _draw_table_header(self):
        """Draw the table header with sortable columns."""
        x_start = self.padding
        header_height = 60
        
        for col in self.columns:
            width = self.column_widths[col] + 40
            self._draw_header_background(x_start, header_height, width, col)
            self._draw_header_text(x_start, header_height, width, col)
            x_start += width

    def _draw_header_background(self, x_start: int, header_height: int, width: int, col: str):
        """Draw the background of the header."""
        header_bg = self.canvas.create_rectangle(
            x_start, self.padding, x_start + width, self.padding + header_height,
            fill=self.style.ACCENT if col == self.sort_column else self.style.PRIMARY,
            outline=self.style.BACKGROUND,
            tags=('header', f'col_{col}')
        )
        self.elements.append(header_bg)

    def _draw_header_text(self, x_start: int, header_height: int, width: int, col: str):
        """Draw the text of the header."""
        header_text = self.canvas.create_text(
            x_start + width / 2, self.padding + header_height / 2,
            text=f"{col} {'↑' if self.sort_ascending and col == self.sort_column else '↓' if col == self.sort_column else ''}",
            font=self.style.TITLE_FONT,
            fill=self.style.TEXT,
            anchor='center',
            tags=('header_text', f'col_{col}')
        )
        self.elements.append(header_text)

    def _animate_rows(self):
        """Draw rows with smooth animation.
        
        Requirements: 3.2, 3.6, 6.3
        """
        def ease(t):
            return t * t * (3 - 2 * t)
        
        row_height = 60
        max_rows = (self.height - self.padding * 3 - 40) // row_height
        filtered_data = self._apply_filters_and_sort()
        
        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            y_start = self.padding + 60
            
            self._clear_rows()
            self._draw_rows(filtered_data, max_rows, y_start, row_height, progress)
            
            if frame < total_frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
        total_frames = self.animation_duration // 16
        update_animation(0, total_frames)

    def _clear_rows(self):
        """Clear existing rows."""
        for item in self.elements:
            if 'row' in self.canvas.gettags(item):
                self.canvas.delete(item)

    def _draw_rows(self, filtered_data: List[Dict[str, Union[str, float, int]]], max_rows: int, y_start: int, row_height: int, progress: float):
        """Draw rows with animation."""
        for i, row in enumerate(filtered_data[:max_rows]):
            x_start = self.padding
            y_pos = y_start + i * row_height * progress
            
            for col in self.columns:
                width = self.column_widths[col] + 40
                value = row.get(col, '')
                self._draw_row_background(x_start, y_pos, width, row_height, i)
                self._draw_row_text(x_start, y_pos, width, row_height, value, i)  # Pass row_index here
                x_start += width

    def _draw_row_background(self, x_start: int, y_pos: int, width: int, row_height: int, row_index: int):
        """Draw the background of a row."""
        bg_color = self.style.BACKGROUND if row_index % 2 == 0 else self.style.SECONDARY
        row_bg = self.canvas.create_rectangle(
            x_start, y_pos, x_start + width, y_pos + row_height,
            fill=bg_color,
            outline=self.style.BACKGROUND,
            tags=('row', f'row_{row_index}')
        )
        self.elements.append(row_bg)

    def _draw_row_text(self, x_start: int, y_pos: int, width: int, row_height: int, value: str, row_index: int):
        """Draw the text of a row."""
        row_text = self.canvas.create_text(
            x_start + width / 2, y_pos + row_height / 2,
            text=str(value),
            font=self.style.VALUE_FONT,
            fill=self.style.TEXT,
            anchor='center',
            tags=('row', f'row_{row_index}')
        )
        self.elements.append(row_text)

    def _apply_filters_and_sort(self) -> List[Dict[str, Union[str, float, int]]]:
        """Apply filters and sorting to the data."""
        filtered_data = self.data[:]
        
        for col, filter_val in self.filters.items():
            if filter_val:
                filtered_data = [row for row in filtered_data if str(row.get(col, '')).lower().startswith(filter_val.lower())]
        
        if self.sort_column:
            filtered_data.sort(key=lambda x: x.get(self.sort_column, ''), reverse=not self.sort_ascending)
        
        return filtered_data

    def _add_interactive_effects(self):
        """Add sorting and filtering interactivity.
        
        Requirements: 3.5, 7.2, 7.3
        """
        def on_header_click(event):
            """Handle header click events (Requirements: 7.3)"""
            try:
                col = self._get_clicked_column(event)
                if col:
                    self._update_sort_column(col)
                    self._redraw_table()
            except tk.TclError as e:
                logger.debug(f"TclError in header click: {e}")
            except Exception as e:
                logger.warning(f"Error in header click: {e}")

        def on_hover(event):
            """Handle hover events (Requirements: 7.2)"""
            try:
                for item in self.canvas.find_withtag('header'):
                    if item in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
                        self.canvas.itemconfig(item, fill=self.style.ACCENT_HOVER)
                    else:
                        col = self._get_column_from_item(item)
                        self.canvas.itemconfig(item, fill=self.style.ACCENT if col == self.sort_column else self.style.PRIMARY)
            except tk.TclError as e:
                logger.debug(f"TclError in hover: {e}")
            except Exception as e:
                logger.warning(f"Error in hover: {e}")
        
        def on_leave(event):
            """Handle leave events"""
            try:
                for item in self.canvas.find_withtag('header'):
                    col = self._get_column_from_item(item)
                    self.canvas.itemconfig(item, fill=self.style.ACCENT if col == self.sort_column else self.style.PRIMARY)
            except tk.TclError:
                pass
            except Exception:
                pass
        
        # Bind events and register with resource manager (Requirements: 3.5)
        click_id = self.canvas.bind('<Button-1>', on_header_click)
        motion_id = self.canvas.bind('<Motion>', on_hover)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        self.resource_manager.register_binding(self.canvas, '<Button-1>', click_id)
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)

    def _get_clicked_column(self, event) -> Optional[str]:
        """Get the column clicked by the user."""
        for item in self.canvas.find_withtag('header'):
            if item in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
                tags = self.canvas.gettags(item)
                return next(tag.split('_')[1] for tag in tags if tag.startswith('col_'))
        return None

    def _update_sort_column(self, col: str):
        """Update the sort column and order."""
        if self.sort_column == col:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = col
            self.sort_ascending = True

    def _redraw_table(self):
        """Redraw the table with updated data."""
        self.canvas.delete('all')
        self.elements.clear()
        self._draw_table_header()
        self._animate_rows()

    def _get_column_from_item(self, item) -> Optional[str]:
        """Get the column from the canvas item."""
        tags = self.canvas.gettags(item)
        return next((tag.split('_')[1] for tag in tags if tag.startswith('col_')), None)

    def _update_filter(self, column: str, value: str):
        """Update filter value and redraw table."""
        self.filters[column] = value.strip()
        self._redraw_table()