from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle
class CandlestickChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []  # List of (index, open, high, low, close) tuples
        self.candle_width_factor = 0.7  # Slightly wider candles
        self.wick_width = 2  # Thicker wicks for visibility
        self.animation_duration = 600  # Smoother animation
        self.elements = []
        
    def plot(self, data: List[Tuple[float, float, float, float, float]]):
        """Plot an improved candlestick chart with (index, open, high, low, close) data"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(d, tuple) and len(d) == 5 and 
                  all(isinstance(v, (int, float)) for v in d) for d in data):
            raise TypeError("Data must be a list of (index, open, high, low, close) number tuples")
            
        self.data = sorted(data, key=lambda x: x[0])  # Sort by index
        
        # Calculate ranges
        indices, opens, highs, lows, closes = zip(*self.data)
        self.x_min, self.x_max = min(indices), max(indices)
        self.y_min, self.y_max = min(lows), max(highs)
        x_padding = (self.x_max - self.x_min) * 0.1 or 1
        y_padding = (self.y_max - self.y_min) * 0.1 or 1
        self.x_min -= x_padding
        self.x_max += x_padding
        self.y_min -= y_padding
        self.y_max += y_padding
        
        self.title = "Candlestick Chart"
        self.x_label = "Time/Index"
        self.y_label = "Price"
        
        self.canvas.delete('all')
        self.elements.clear()
        
        self._draw_axes(self.x_min, self.x_max, self.y_min, self.y_max)
        self._animate_candles()
        self._add_interactive_effects()

    def _animate_candles(self):
        """Draw candlesticks with improved animation from midpoint"""
        def ease(t):
            return t * t * (3 - 2 * t)
        
        candle_spacing = (self.width - 2 * self.padding) / (len(self.data) if len(self.data) > 1 else 1)
        candle_width = candle_spacing * self.candle_width_factor
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            
            for item in self.elements:
                self.canvas.delete(item)
            self.elements.clear()
            
            for i, (index, open_price, high, low, close_price) in enumerate(self.data):
                x = self._data_to_pixel_x(index, self.x_min, self.x_max)
                y_open = self._data_to_pixel_y(open_price, self.y_min, self.y_max)
                y_high = self._data_to_pixel_y(high, self.y_min, self.y_max)
                y_low = self._data_to_pixel_y(low, self.y_min, self.y_max)
                y_close = self._data_to_pixel_y(close_price, self.y_min, self.y_max)
                
                # Colors: Bullish (green), Bearish (red)
                fill_color = "#4CAF50" if close_price >= open_price else "#F44336"
                outline_color = self.style.adjust_brightness(fill_color, 0.8)
                
                # Animate from midpoint of open/close
                y_mid = (y_open + y_close) / 2
                candle_height = abs(y_close - y_open) * progress
                y_top = y_mid - candle_height / 2 if close_price >= open_price else y_mid - candle_height / 2
                y_bottom = y_mid + candle_height / 2 if close_price >= open_price else y_mid + candle_height / 2
                
                # Wick
                wick = self.canvas.create_line(
                    x, y_high - (y_high - y_low) * progress,
                    x, y_low + (y_low - y_high) * progress,
                    fill=self.style.TEXT_SECONDARY,
                    width=self.wick_width,
                    tags=('wick', f'candle_{i}')
                )
                self.elements.append(wick)
                
                # Candle body (minimum 1px height for flat candles)
                if candle_height < 1:
                    candle_height = 1
                shadow = self.canvas.create_rectangle(
                    x - candle_width/2 + 2, y_top + 2,
                    x + candle_width/2 + 2, y_bottom + 2,
                    fill=self.style.create_shadow(fill_color),
                    outline="",
                    tags=('shadow', f'candle_{i}')
                )
                self.elements.append(shadow)
                
                candle = self.canvas.create_rectangle(
                    x - candle_width/2, y_top,
                    x + candle_width/2, y_bottom,
                    fill=fill_color,
                    outline=outline_color,
                    width=1,
                    tags=('candle', f'candle_{i}')
                )
                self.elements.append(candle)
                
                if progress == 1:
                    # High label above wick
                    high_label = self.canvas.create_text(
                        x, y_high - 10,
                        text=f"{high:.1f}",
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='s',
                        tags=('label', f'candle_{i}')
                    )
                    self.elements.append(high_label)
                    # Low label below wick
                    low_label = self.canvas.create_text(
                        x, y_low + 10,
                        text=f"{low:.1f}",
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        anchor='n',
                        tags=('label', f'candle_{i}')
                    )
                    self.elements.append(low_label)
            
            if frame < total_frames:
                self.canvas.after(20, update_animation, frame + 1, total_frames)
        
        total_frames = self.animation_duration // 20  # ~50 FPS
        update_animation(0, total_frames)

    def _add_interactive_effects(self):
        """Add enhanced hover effects and tooltips"""
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)
        
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
            nonlocal current_highlight
            x, y = event.x, event.y
            
            if self.padding <= x <= self.width - self.padding and self.padding <= y <= self.height - self.padding:
                candle_spacing = (self.width - 2 * self.padding) / (len(self.data) if len(self.data) > 1 else 1)
                candle_width = candle_spacing * self.candle_width_factor
                candle_index = int((x - self.padding) / candle_spacing)
                
                if 0 <= candle_index < len(self.data):
                    index, open_price, high, low, close_price = self.data[candle_index]
                    px = self._data_to_pixel_x(index, self.x_min, self.x_max)
                    y_high = self._data_to_pixel_y(high, self.y_min, self.y_max)
                    y_low = self._data_to_pixel_y(low, self.y_min, self.y_max)
                    y_open = self._data_to_pixel_y(open_price, self.y_min, self.y_max)
                    y_close = self._data_to_pixel_y(close_price, self.y_min, self.y_max)
                    y_top = min(y_open, y_close)
                    y_bottom = max(y_open, y_close)
                    
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                    
                    # Highlight entire candlestick
                    highlight = self.canvas.create_rectangle(
                        px - candle_width/2 - 3, y_high - 3,
                        px + candle_width/2 + 3, y_low + 3,
                        outline=self.style.ACCENT,
                        width=2,
                        dash=(4, 2),  # Dashed outline for subtlety
                        tags=('highlight',)
                    )
                    current_highlight = highlight
                    
                    # Detailed tooltip
                    change = close_price - open_price
                    label.config(text=f"Index: {index:.1f}\nOpen: {open_price:.2f}\nHigh: {high:.2f}\nLow: {low:.2f}\nClose: {close_price:.2f}\nChange: {change:.2f} ({(change/open_price*100):.1f}%)")
                    tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root-50}")
                    tooltip.deiconify()
                    tooltip.lift()
                else:
                    if current_highlight:
                        self.canvas.delete(current_highlight)
                        current_highlight = None
                    tooltip.withdraw()
        
        def on_leave(event):
            nonlocal current_highlight
            if current_highlight:
                self.canvas.delete(current_highlight)
                current_highlight = None
            tooltip.withdraw()
        
        self.canvas.bind('<Motion>', on_motion)
        self.canvas.bind('<Leave>', on_leave)