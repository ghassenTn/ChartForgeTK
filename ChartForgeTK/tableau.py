from typing import List, Dict, Union, Optional
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle
class TableauChart(Chart):
    """
    A Tableau-style chart for displaying tabular data with interactive features like sorting and filtering.
    
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
            ValueError: If data is empty or not a list of dictionaries, or if specified columns do not exist in data.
        """
        if not data or not all(isinstance(d, dict) for d in data):
            raise ValueError("Data must be a non-empty list of dictionaries")
        
        self.data = data
        available_columns = list(data[0].keys())
        self.columns = columns if columns else available_columns
        
        if not all(col in available_columns for col in self.columns):
            raise ValueError("Specified columns must exist in data")
        
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
        """Draw rows with smooth animation."""
        def ease(t):
            return t * t * (3 - 2 * t)
        
        row_height = 60
        max_rows = (self.height - self.padding * 3 - 40) // row_height
        filtered_data = self._apply_filters_and_sort()
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            y_start = self.padding + 60
            
            self._clear_rows()
            self._draw_rows(filtered_data, max_rows, y_start, row_height, progress)
            
            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)
        
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
        """Add sorting and filtering interactivity."""
        def on_header_click(event):
            col = self._get_clicked_column(event)
            if col:
                self._update_sort_column(col)
                self._redraw_table()

        def on_hover(event):
            for item in self.canvas.find_withtag('header'):
                if item in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
                    self.canvas.itemconfig(item, fill=self.style.ACCENT_HOVER)
                else:
                    col = self._get_column_from_item(item)
                    self.canvas.itemconfig(item, fill=self.style.ACCENT if col == self.sort_column else self.style.PRIMARY)
        
        self.canvas.bind('<Button-1>', on_header_click)
        self.canvas.bind('<Motion>', on_hover)
        self.canvas.bind('<Leave>', lambda e: [self.canvas.itemconfig(item, fill=self.style.ACCENT if col == self.sort_column else self.style.PRIMARY) 
                                              for item in self.canvas.find_withtag('header') 
                                              for col in [self._get_column_from_item(item)]])

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