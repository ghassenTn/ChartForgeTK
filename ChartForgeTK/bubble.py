from typing import List, Optional, Tuple
import math
import tkinter as tk
from .core import Chart, ChartStyle

class BubbleChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.min_bubble_size = 10
        self.max_bubble_size = 50
        self.interactive_bubbles = {}
        self._hover_tag = None
        self.x_label = 'X'
        self.y_label = 'Y'

    def plot(self, x_values: List[float], y_values: List[float], sizes: List[float], 
            labels: Optional[List[str]] = None,
            colors: Optional[List[str]] = None):
        """Plot a bubble chart.
        
        Args:
            x_values: List of x-coordinates
            y_values: List of y-coordinates
            sizes: List of bubble sizes (will be scaled between min_bubble_size and max_bubble_size)
            labels: Optional list of labels for each bubble
            colors: Optional list of colors for each bubble
        """
        if len(x_values) != len(y_values) or len(x_values) != len(sizes):
            raise ValueError("x_values, y_values, and sizes must have the same length")
        
        if labels is None:
            labels = [str(i) for i in range(len(x_values))]
        
        if colors is None:
            colors = [
                "#3B82F6",  # Blue
                "#10B981",  # Emerald
                "#F59E0B",  # Amber
                "#8B5CF6",  # Purple
                "#EF4444",  # Red
                "#06B6D4",  # Cyan
                "#EC4899",  # Pink
                "#14B8A6",  # Teal
                "#F97316",  # Orange
                "#6366F1"   # Indigo
            ]
            colors = [colors[i % len(colors)] for i in range(len(x_values))]
        
        self.clear()
        self.interactive_bubbles.clear()
        
        # Scale values to fit the chart
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        size_min, size_max = min(sizes), max(sizes)
        
        # Add padding to axis ranges
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1
        x_min -= x_padding
        x_max += x_padding
        y_min -= y_padding
        y_max += y_padding
        
        # Draw axes
        self._draw_axes(x_min, x_max, y_min, y_max)
        
        # Plot bubbles
        for i, (x, y, size, label, color) in enumerate(zip(x_values, y_values, sizes, labels, colors)):
            # Scale coordinates to canvas
            canvas_x = self._scale_x(x, x_min, x_max)
            canvas_y = self._scale_y(y, y_min, y_max)
            
            # Scale bubble size
            if size_max == size_min:
                scaled_size = (self.max_bubble_size + self.min_bubble_size) / 2
            else:
                scale_factor = (size - size_min) / (size_max - size_min)
                scaled_size = self.min_bubble_size + scale_factor * (self.max_bubble_size - self.min_bubble_size)
            
            # Create bubble
            bubble = self.canvas.create_oval(
                canvas_x - scaled_size, canvas_y - scaled_size,
                canvas_x + scaled_size, canvas_y + scaled_size,
                fill=color, outline=self.style.PRIMARY,
                stipple='gray50', tags=('bubble', f'bubble_{i}')
            )
            
            # Store bubble info for interactivity
            self.interactive_bubbles[bubble] = {
                'x': x, 'y': y, 'size': size,
                'label': label, 'color': color
            }
        
        self._add_interactivity()
    
    def _scale_x(self, x: float, x_min: float, x_max: float) -> float:
        """Scale x value to canvas coordinates."""
        return self.padding + (x - x_min) * (self.width - 2 * self.padding) / (x_max - x_min)
    
    def _scale_y(self, y: float, y_min: float, y_max: float) -> float:
        """Scale y value to canvas coordinates."""
        return self.height - self.padding - (y - y_min) * (self.height - 2 * self.padding) / (y_max - y_min)
    
    def _draw_axes(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw x and y axes with labels."""
        # X-axis
        x_axis_y = self.height - self.padding
        self.canvas.create_line(
            self.padding, x_axis_y,
            self.width - self.padding, x_axis_y,
            fill=self.style.TEXT
        )
        
        # Y-axis
        self.canvas.create_line(
            self.padding, self.padding,
            self.padding, self.height - self.padding,
            fill=self.style.TEXT
        )
        
        # X-axis labels
        for i in range(5):
            x = x_min + i * (x_max - x_min) / 4
            canvas_x = self._scale_x(x, x_min, x_max)
            self.canvas.create_text(
                canvas_x, self.height - self.padding + 20,
                text=f'{x:.1f}', fill=self.style.TEXT,
                font=self.style.LABEL_FONT
            )
        
        # Y-axis labels
        for i in range(5):
            y = y_min + i * (y_max - y_min) / 4
            canvas_y = self._scale_y(y, y_min, y_max)
            self.canvas.create_text(
                self.padding - 30, canvas_y,
                text=f'{y:.1f}', fill=self.style.TEXT,
                font=self.style.LABEL_FONT
            )
    
    def _add_interactivity(self):
        """Add hover effects and tooltips to bubbles."""
        def on_enter(event):
            item = event.widget.find_closest(event.x, event.y)[0]
            if item in self.interactive_bubbles and item != self._hover_tag:
                # Clean up any existing tooltips first
                self.canvas.delete('tooltip')
                
                info = self.interactive_bubbles[item]
                
                # Get bubble center coordinates for fixed tooltip position
                x1, y1, x2, y2 = self.canvas.coords(item)
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Highlight bubble
                self.canvas.itemconfig(
                    item,
                    stipple='',  # Remove stipple for solid fill
                    width=3,     # Increase border width
                    outline=self.style.ACCENT  # Change border color
                )
                
                # Create glow effect
                glow = self.canvas.create_oval(
                    x1-2, y1-2, x2+2, y2+2,
                    fill='',
                    outline=self.style.ACCENT,
                    width=2,
                    tags='tooltip'
                )
                self.canvas.tag_lower(glow, item)
                
                # Format values for tooltip
                if 'GDP' in info['label']:
                    x_format = f"${info['x']:,.0f}"
                else:
                    x_format = f"{info['x']:.1f}"
                
                if 'Population' in str(info['size']):
                    size_format = f"{info['size']:,.0f}M"
                else:
                    size_format = f"{info['size']:.1f}"
                
                # Show enhanced tooltip
                tooltip_text = f"""
{info['label']}
{self.x_label}: {x_format}
{self.y_label}: {info['y']:.1f}
Size: {size_format}"""
                
                # Position tooltip to the right of the bubble
                tooltip_x = center_x + (x2 - x1) / 2 + 20
                tooltip_y = center_y
                
                tooltip = self.canvas.create_text(
                    tooltip_x, tooltip_y,
                    text=tooltip_text.strip(),
                    anchor='w',
                    fill=self.style.TEXT,
                    font=self.style.TOOLTIP_FONT,
                    tags='tooltip'
                )
                
                # Add tooltip background with shadow
                bbox = self.canvas.bbox(tooltip)
                padding = 8
                # Shadow
                shadow = self.canvas.create_rectangle(
                    bbox[0] - padding + 2, bbox[1] - padding + 2,
                    bbox[2] + padding + 2, bbox[3] + padding + 2,
                    fill=self.style.SHADOW,
                    outline='',
                    tags='tooltip'
                )
                # Background
                background = self.canvas.create_rectangle(
                    bbox[0] - padding, bbox[1] - padding,
                    bbox[2] + padding, bbox[3] + padding,
                    fill=self.style.BACKGROUND,
                    outline=self.style.ACCENT,
                    width=2,
                    tags='tooltip'
                )
                
                # Arrange layers
                self.canvas.tag_lower(background, tooltip)
                self.canvas.tag_lower(shadow, background)
                
                # Reset old hover tag if exists
                if self._hover_tag and self._hover_tag != item:
                    self.canvas.itemconfig(
                        self._hover_tag,
                        stipple='gray50',
                        width=1,
                        outline=self.style.PRIMARY
                    )
                
                self._hover_tag = item

        def on_leave(event):
            if self._hover_tag:
                # Reset bubble appearance
                self.canvas.itemconfig(
                    self._hover_tag,
                    stipple='gray50',
                    width=1,
                    outline=self.style.PRIMARY
                )
                # Remove tooltip and effects
                self.canvas.delete('tooltip')
                self._hover_tag = None

        # Only bind enter and leave events, remove motion binding
        self.canvas.tag_bind('bubble', '<Enter>', on_enter)
        self.canvas.tag_bind('bubble', '<Leave>', on_leave)
