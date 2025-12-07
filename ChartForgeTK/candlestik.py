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


from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class CandlestickChart(Chart):
    """
    Candlestick chart implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, show_labels=True, width: int = 800, height: int = 600, display_mode='frame', theme='light'):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.show_labels = show_labels
        self.data = []  # List of (index, open, high, low, close) tuples
        self.candle_width_factor = 0.7  # Slightly wider candles
        self.wick_width = 2  # Thicker wicks for visibility
        self.animation_duration = 600  # Smoother animation
        self.elements = []
        self._tooltip = None  # Tooltip window reference
        
    def plot(self, data: List[Tuple[float, float, float, float, float]]):
        """Plot an improved candlestick chart with (index, open, high, low, close) data
        
        Args:
            data: List of (index, open, high, low, close) tuples
            
        Raises:
            ValueError: If data is empty or contains invalid OHLC values
            TypeError: If data is not a list of (index, open, high, low, close) number tuples
            
        Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.6, 9.1, 9.2, 9.3, 9.4
        """
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_tuple_list(
            data,
            expected_length=5,
            allow_empty=False,
            param_name="data"
        )
        
        # Additional validation: high >= low for each candle
        for i, (index, open_price, high, low, close_price) in enumerate(validated_data):
            if high < low:
                raise ValueError(
                    f"[ChartForgeTK] Error: data[{i}] has high ({high}) < low ({low}). "
                    f"High must be greater than or equal to low."
                )
            if high < open_price or high < close_price:
                raise ValueError(
                    f"[ChartForgeTK] Error: data[{i}] has high ({high}) less than open ({open_price}) or close ({close_price}). "
                    f"High must be the maximum value."
                )
            if low > open_price or low > close_price:
                raise ValueError(
                    f"[ChartForgeTK] Error: data[{i}] has low ({low}) greater than open ({open_price}) or close ({close_price}). "
                    f"Low must be the minimum value."
                )
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Create copy for immutability and sort by index (Requirements: 9.1, 9.2, 9.4)
        self.data = sorted([tuple(d) for d in validated_data], key=lambda x: x[0])
        
        # Handle edge case: single data point (Requirements: 2.1)
        if len(self.data) == 1:
            logger.debug("Single candlestick detected, adjusting layout")
        
        # Calculate ranges
        indices, opens, highs, lows, closes = zip(*self.data)
        self.x_min, self.x_max = min(indices), max(indices)
        self.y_min, self.y_max = min(lows), max(highs)
        
        # Handle edge case: identical x values (Requirements: 2.2)
        x_range = self.x_max - self.x_min
        if x_range == 0:
            x_padding = abs(self.x_max) * 0.1 if self.x_max != 0 else 1
            logger.debug(f"All x values identical ({self.x_max}), using default padding")
        else:
            x_padding = x_range * 0.1
        
        # Handle edge case: identical y values (Requirements: 2.2)
        y_range = self.y_max - self.y_min
        if y_range == 0:
            y_padding = abs(self.y_max) * 0.1 if self.y_max != 0 else 1
            logger.debug(f"All y values identical ({self.y_max}), using default padding")
        else:
            y_padding = y_range * 0.1
        
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
        """Draw candlesticks with improved animation from midpoint.
        
        Requirements: 3.2, 3.6, 6.3
        """
        def ease(t):
            return t * t * (3 - 2 * t)
        
        candle_spacing = (self.width - 2 * self.padding) / (len(self.data) if len(self.data) > 1 else 1)
        candle_width = candle_spacing * self.candle_width_factor
        
        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            
            for item in self.elements:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
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
                # Calculate midpoint and animate wick from center outwards
                y_mid_wick = (y_high + y_low) / 2
                half_wick_length = (y_low - y_high) / 2 * progress

                wick = self.canvas.create_line(
                    x, y_mid_wick - half_wick_length,
                    x, y_mid_wick + half_wick_length,
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
                
                if self.show_labels and progress == 1:
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
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                after_id = self.canvas.after(20, update_animation, frame + 1, total_frames)
                self.resource_manager.register_animation(after_id)
        
        total_frames = self.animation_duration // 20  # ~50 FPS
        update_animation(0, total_frames)

    def _add_interactive_effects(self):
        """Add enhanced hover effects and tooltips with proper resource management.
        
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
                candle_spacing = (self.width - 2 * self.padding) / (len(self.data) if len(self.data) > 1 else 1)
                candle_width = candle_spacing * self.candle_width_factor
                candle_index = int((x - self.padding) / candle_spacing)
                
                if 0 <= candle_index < len(self.data):
                    index, open_price, high, low, close_price = self.data[candle_index]
                    px = self._data_to_pixel_x(index, self.x_min, self.x_max)
                    y_high = self._data_to_pixel_y(high, self.y_min, self.y_max)
                    y_low = self._data_to_pixel_y(low, self.y_min, self.y_max)
                    
                    if current_highlight:
                        try:
                            self.canvas.delete(current_highlight)
                        except tk.TclError:
                            pass
                    
                    # Highlight entire candlestick
                    try:
                        highlight = self.canvas.create_rectangle(
                            px - candle_width/2 - 3, y_high - 3,
                            px + candle_width/2 + 3, y_low + 3,
                            outline=self.style.ACCENT,
                            width=2,
                            dash=(4, 2),  # Dashed outline for subtlety
                            tags=('highlight',)
                        )
                        current_highlight = highlight
                    except tk.TclError:
                        current_highlight = None
                    
                    # Detailed tooltip - handle division by zero
                    change = close_price - open_price
                    if open_price != 0:
                        pct_change = (change / open_price * 100)
                        tooltip_text = f"Index: {index:.1f}\nOpen: {open_price:.2f}\nHigh: {high:.2f}\nLow: {low:.2f}\nClose: {close_price:.2f}\nChange: {change:.2f} ({pct_change:.1f}%)"
                    else:
                        tooltip_text = f"Index: {index:.1f}\nOpen: {open_price:.2f}\nHigh: {high:.2f}\nLow: {low:.2f}\nClose: {close_price:.2f}\nChange: {change:.2f}"
                    
                    try:
                        label.config(text=tooltip_text)
                        tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root-50}")
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
