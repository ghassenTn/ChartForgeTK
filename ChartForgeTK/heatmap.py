from typing import List, Optional, Tuple
import tkinter as tk
import math
from .core import Chart, ChartStyle

class HeatMap(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
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
        """
        if not data or not data[0]:
            raise ValueError("Data must be a non-empty 2D list")
        
        self.clear()
        self.interactive_cells.clear()
        
        num_rows = len(data)
        num_cols = len(data[0])
        
        # Set default labels if not provided
        if row_labels is None:
            row_labels = [str(i) for i in range(num_rows)]
        if col_labels is None:
            col_labels = [str(i) for i in range(num_cols)]
            
        if title:
            self.title = title
        
        # Find data range for color scaling
        all_values = [val for row in data for val in row]
        data_min = min(all_values)
        data_max = max(all_values)
        
        # Calculate cell size
        available_width = self.width - 2 * self.padding - 100  # Extra space for labels
        available_height = self.height - 2 * self.padding - 100  # Extra space for labels
        cell_width = available_width / num_cols
        cell_height = available_height / num_rows
        
        # Draw column labels
        for j, label in enumerate(col_labels):
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
        for i, label in enumerate(row_labels):
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
                value = data[i][j]
                
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
                    'row_label': row_labels[i],
                    'col_label': col_labels[j],
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
        """Add hover effects and tooltips to cells."""
        def on_enter(event):
            try:
                # Get the current cell
                item = event.widget.find_closest(event.x, event.y)[0]
                if not item in self.interactive_cells:
                    return
                    
                # Clean up old tooltip
                self.canvas.delete('tooltip')
                
                # Reset previous cell if exists
                if self._hover_tag:
                    self.canvas.itemconfig(
                        self._hover_tag,
                        outline=self.style.BACKGROUND,
                        width=self.cell_padding
                    )
                
                # Get cell info
                info = self.interactive_cells[item]
                
                # Highlight current cell
                self.canvas.itemconfig(
                    item,
                    outline=self.style.ACCENT,
                    width=2
                )
                
                # Create simple tooltip
                x1, y1, x2, y2 = self.canvas.coords(item)
                tooltip_x = (x1 + x2) / 2
                tooltip_y = y1 - 5
                
                # Create background first
                background = self.canvas.create_rectangle(
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
                
            except Exception as e:
                print(f"Hover error: {e}")
                self.canvas.delete('tooltip')
                if self._hover_tag:
                    self.canvas.itemconfig(
                        self._hover_tag,
                        outline=self.style.BACKGROUND,
                        width=self.cell_padding
                    )
                self._hover_tag = None

        def on_leave(event):
            # Simple cleanup
            if self._hover_tag:
                self.canvas.itemconfig(
                    self._hover_tag,
                    outline=self.style.BACKGROUND,
                    width=self.cell_padding
                )
            self.canvas.delete('tooltip')
            self._hover_tag = None

        # Only bind enter/leave events
        self.canvas.tag_bind('cell', '<Enter>', on_enter)
        self.canvas.tag_bind('cell', '<Leave>', on_leave)
