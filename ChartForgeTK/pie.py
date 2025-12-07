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


from typing import List, Optional, Union, Tuple, Any
import tkinter as tk
from tkinter import ttk
import math
import logging
from .core import Chart, ChartStyle
from .validation import DataValidator

logger = logging.getLogger('ChartForgeTK')


class PieChart(Chart):
    """
    Pie chart implementation with comprehensive input validation and edge case handling.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.5, 3.1, 3.2, 3.6, 9.1, 9.2
    """
    
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', 
                 theme='light', is_3d: bool = False):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []
        self.labels = []
        self.radius = min(width, height) * 0.35  # 70% of smallest dimension
        self.center_x = width / 2
        self.center_y = height / 2
        self.animation_duration = 500  # ms
        self.selected_slice = None  # Track the currently selected slice
        self.slices = []  # Store slice IDs for later reference
        self.slice_angles = []  # Store the angles for each slice
        self.label_items = []  # Store label IDs for later reference
        self.is_3d = is_3d  # New parameter to toggle 3D effect
        self.thickness = 30 if is_3d else 0  # Thickness for 3D effect, 0 for 2D
        self.tilt_factor = 0.5 if is_3d else 1  # Tilt factor for 3D, 1 for flat 2D
        self.original_colors = []  # Store original colors for slices
        self._tooltip = None  # Tooltip window reference

    def plot(
        self,
        data: Any,
        labels: Optional[Union[List[str], str]] = None,
        value_column: Optional[str] = None,
        label_column: Optional[str] = None
    ):
        """
        Plot the pie chart with the given data and optional labels.
        
        Supports pandas DataFrame, Series, or list input. When a DataFrame or Series
        is passed, the data is automatically converted to lists for plotting.
        
        Args:
            data: Data to plot. Can be:
                - List of numeric values (must be non-negative)
                - pandas DataFrame (uses value_column or first numeric column)
                - pandas Series (uses values with index as labels)
            labels: Optional labels for each slice. Can be:
                - List of strings
                - Ignored when data is a pandas object (use label_column instead)
            value_column: Column name for values when data is a DataFrame.
                If not specified, uses the first numeric column.
            label_column: Column name for labels when data is a DataFrame.
                If not specified, uses the DataFrame index.
            
        Raises:
            TypeError: If data is None or contains non-numeric values
            ValueError: If data is empty, contains negative values, labels mismatch,
                       or all values are zero
            ImportError: If pandas DataFrame/Series is passed but pandas is not installed
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 2.5, 4.4, 4.5, 9.1, 9.2
        """
        # Handle pandas DataFrame input (Requirements: 4.4, 4.5)
        if DataValidator.is_pandas_dataframe(data):
            converted_values, converted_labels = DataValidator.convert_dataframe_to_list(
                data,
                value_column=value_column,
                label_column=label_column,
                param_name="data"
            )
            data = converted_values
            # Use converted labels if no explicit labels provided
            if labels is None:
                labels = converted_labels
        # Handle pandas Series input (Requirements: 4.4, 4.5)
        elif DataValidator.is_pandas_series(data):
            converted_values, converted_labels = DataValidator.convert_series_to_list(
                data,
                param_name="data"
            )
            data = converted_values
            # Use converted labels if no explicit labels provided
            if labels is None:
                labels = converted_labels
        # When column parameters are provided with non-DataFrame data, ignore them (Requirements: 4.5)
        # This maintains backward compatibility - no action needed, just proceed with list validation
        
        # Validate data using DataValidator (Requirements: 1.1, 1.2, 1.3)
        validated_data = DataValidator.validate_numeric_list(
            data,
            allow_empty=False,
            allow_negative=False,  # Pie charts don't support negative values
            allow_nan=False,
            allow_inf=False,
            param_name="data"
        )
        
        # Validate labels (Requirements: 1.4)
        validated_labels = DataValidator.validate_labels(labels, len(validated_data), param_name="labels")
        
        # Check for all-zero data (Requirements: 2.5)
        total = sum(validated_data)
        if total == 0:
            raise ValueError(
                "[PieChart] Error: All data values are zero. "
                "Pie chart requires at least one non-zero value to display proportions."
            )
        
        # Create copies for immutability (Requirements: 9.1, 9.2)
        self.data = validated_data.copy()
        self.labels = validated_labels.copy()
        self.total = total
        
        # Cancel pending animations before redrawing (Requirements: 3.2, 3.6)
        self.resource_manager.cancel_animations()
        
        # Clean up previous tooltips (Requirements: 3.1)
        self.resource_manager.cleanup_tooltips()
        
        # Clear previous content
        self.canvas.delete('all')
        
        # Reset stored colors
        self.original_colors = []
        
        # Add title
        self._add_title("3D Pie Chart" if self.is_3d else "Pie Chart")
        
        # Animate the pie chart drawing
        self._animate_pie()
        self._add_interactive_effects()

    def _animate_pie(self):
        """
        Draw the pie chart with smooth animation, optionally with 3D effect.
        
        Handles edge cases:
        - Single data point (Requirements: 2.1)
        
        Requirements: 3.2, 3.6
        """
        def ease(t):
            return t * t * (3 - 2 * t)  # Ease-in-out
        
        self.slices = []  # Reset slices list
        self.slice_angles = []  # Reset slice angles list
        self.label_items = []  # Reset label items list
        self.original_colors = []  # Reset original colors list
        
        # Handle edge case: single data point (Requirements: 2.1)
        is_single_point = len(self.data) == 1
        if is_single_point:
            logger.debug("Single data point detected, rendering full circle")
        
        def update_animation(frame: int, total_frames: int):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = ease(frame / total_frames)
            current_angle = 0
            
            # Clear previous slices and labels
            for item in self.slices + self.label_items:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.slices.clear()
            self.slice_angles.clear()
            self.label_items.clear()
            
            # Draw the "sides" of the pie chart (only if 3D)
            if self.is_3d:
                for i, value in enumerate(self.data):
                    angle = (value / self.total) * 2 * math.pi * progress
                    end_angle = current_angle + angle
                    color = self.style.get_gradient_color(i, len(self.data))
                    if frame == 0:  # Store original colors only once
                        self.original_colors.append(color)
                    
                    # Draw the side of the slice (darker shade for depth)
                    if progress > 0:  # Only draw sides when there's an angle
                        shadow_color = self.style.create_shadow(color)
                        for depth in range(self.thickness):
                            y_offset = depth * self.tilt_factor
                            try:
                                side = self.canvas.create_arc(
                                    self.center_x - self.radius,
                                    self.center_y - self.radius + y_offset,
                                    self.center_x + self.radius,
                                    self.center_y + self.radius + y_offset,
                                    start=math.degrees(current_angle),
                                    extent=math.degrees(angle),
                                    fill=shadow_color,
                                    outline="",
                                    style=tk.PIESLICE,
                                    tags=('side', f'slice_{i}')
                                )
                                self.slices.append(side)
                            except tk.TclError:
                                pass
                    
                    current_angle = end_angle
            
            # Draw the top of the slices (over the sides if 3D, flat if 2D)
            current_angle = 0
            for i, value in enumerate(self.data):
                angle = (value / self.total) * 2 * math.pi * progress
                end_angle = current_angle + angle
                self.slice_angles.append((current_angle, end_angle))  # Store slice angles
                color = self.style.get_gradient_color(i, len(self.data))
                if frame == 0 and not self.is_3d:  # Store colors for 2D case
                    self.original_colors.append(color)
                
                # Draw the top surface (elliptical for 3D, circular for 2D)
                try:
                    slice_item = self.canvas.create_arc(
                        self.center_x - self.radius,
                        self.center_y - self.radius,
                        self.center_x + self.radius,
                        self.center_y + self.radius - (self.thickness * self.tilt_factor if self.is_3d else 0),
                        start=math.degrees(current_angle),
                        extent=math.degrees(angle),
                        fill=color,
                        outline=self.style.adjust_brightness(color, 1.1),
                        width=1,
                        style=tk.PIESLICE,
                        tags=('slice', f'slice_{i}')
                    )
                    self.slices.append(slice_item)
                except tk.TclError:
                    pass
                
                # Add label when slice is fully drawn
                if progress == 1:
                    mid_angle = current_angle + angle / 2
                    label_radius = self.radius * 1.2
                    lx = self.center_x + label_radius * math.cos(mid_angle)
                    ly = self.center_y - label_radius * math.sin(mid_angle) - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
                    percentage = (value / self.total) * 100
                    label_text = f"{self.labels[i]}\n{percentage:.1f}%"
                    
                    try:
                        label = self.canvas.create_text(
                            lx, ly,
                            text=label_text,
                            font=self.style.VALUE_FONT,
                            fill=self.style.TEXT,
                            justify='center',
                            tags=('label', f'slice_{i}')
                        )
                        self.label_items.append(label)
                    except tk.TclError:
                        pass
                
                current_angle = end_angle
            
            if frame < total_frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                try:
                    after_id = self.canvas.after(16, update_animation, frame + 1, total_frames)
                    self.resource_manager.register_animation(after_id)
                except tk.TclError:
                    pass
        
        total_frames = self.animation_duration // 16  # ~60 FPS
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
            
            # Calculate angle from center
            dx = x - self.center_x
            dy = -(y - self.center_y)  # Invert y for canvas coordinates
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= self.radius:
                angle = math.atan2(dy, dx) % (2 * math.pi)
                current_angle = 0
                
                for i, value in enumerate(self.data):
                    slice_angle = (value / self.total) * 2 * math.pi
                    if current_angle <= angle < current_angle + slice_angle:
                        try:
                            if current_highlight:
                                self.canvas.delete(current_highlight)
                            
                            highlight = self.canvas.create_arc(
                                self.center_x - self.radius * 1.1,
                                self.center_y - self.radius * 1.1,
                                self.center_x + self.radius * 1.1,
                                self.center_y + self.radius * 1.1 - (self.thickness * self.tilt_factor if self.is_3d else 0),
                                start=math.degrees(current_angle),
                                extent=math.degrees(slice_angle),
                                outline=self.style.ACCENT,
                                width=2,
                                style=tk.PIESLICE,
                                tags=('highlight',)
                            )
                            current_highlight = highlight
                            
                            percentage = (value / self.total) * 100
                            tooltip_text = f"{self.labels[i]}\nValue: {value:,.2f}\n{percentage:.1f}%"
                            label.config(text=tooltip_text)
                            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-40}")
                            tooltip.deiconify()
                            tooltip.lift()
                        except tk.TclError:
                            pass  # Widget may have been destroyed
                        break
                    current_angle += slice_angle
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
        
        def on_click(event):
            """Handle mouse click events (Requirements: 7.3)"""
            # Safety check - ensure data exists
            if not self.data:
                return
            
            x, y = event.x, event.y
            dx = x - self.center_x
            dy = -(y - self.center_y)  # Invert y for canvas coordinates
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= self.radius:
                angle = math.atan2(dy, dx) % (2 * math.pi)
                current_angle = 0
                
                for i, value in enumerate(self.data):
                    slice_angle = (value / self.total) * 2 * math.pi
                    if current_angle <= angle < current_angle + slice_angle:
                        try:
                            self._enlarge_slice(i)
                        except Exception as e:
                            logger.warning(f"Error enlarging slice: {e}")
                        break
                    current_angle += slice_angle
        
        # Bind events and register with resource manager (Requirements: 3.5)
        motion_id = self.canvas.bind('<Motion>', on_motion)
        leave_id = self.canvas.bind('<Leave>', on_leave)
        click_id = self.canvas.bind('<Button-1>', on_click)
        self.resource_manager.register_binding(self.canvas, '<Motion>', motion_id)
        self.resource_manager.register_binding(self.canvas, '<Leave>', leave_id)
        self.resource_manager.register_binding(self.canvas, '<Button-1>', click_id)

    def _enlarge_slice(self, slice_index: int):
        """
        Enlarge the selected slice with animation, optionally with 3D effect.
        
        Requirements: 3.2, 3.6
        """
        # Safety check - ensure slice_angles is populated
        if not self.slice_angles or slice_index >= len(self.slice_angles):
            return
        
        if self.selected_slice is not None:
            self._reset_slice(self.selected_slice)
        
        self.selected_slice = slice_index
        current_angle, end_angle = self.slice_angles[slice_index]
        slice_angle = end_angle - current_angle
        
        # Change the original slice color to white
        try:
            for item in self.canvas.find_withtag(f'slice_{slice_index}'):
                if 'slice' in self.canvas.gettags(item) and 'side' not in self.canvas.gettags(item):
                    self.canvas.itemconfig(item, fill='white')
        except tk.TclError:
            pass
        
        # Animation parameters
        explosion_offset = 20  # Maximum explosion distance
        frames = 5  # Number of animation frames
        delay = 16  # Delay between frames (ms)
        
        def animate_explosion(frame):
            # Check if widget still exists before updating (Requirements: 6.3)
            try:
                if not self.canvas.winfo_exists():
                    return
            except tk.TclError:
                return
            
            progress = frame / frames
            offset = explosion_offset * progress
            offset_x = offset * math.cos(current_angle + slice_angle / 2)
            offset_y = -offset * math.sin(current_angle + slice_angle / 2)
            
            # Safety check for original_colors
            if slice_index >= len(self.original_colors):
                return
            
            color = self.original_colors[slice_index]
            shadow_color = self.style.create_shadow(color)
            
            try:
                # Clear previous enlarged slice
                self.canvas.delete('enlarged_slice')
                self.canvas.delete('enlarged_side')
                
                # Draw the sides of the enlarged slice (only if 3D)
                if self.is_3d:
                    for depth in range(self.thickness):
                        y_offset = depth * self.tilt_factor
                        enlarged_side = self.canvas.create_arc(
                            self.center_x - self.radius * 1.2 + offset_x,
                            self.center_y - self.radius * 1.2 + offset_y + y_offset,
                            self.center_x + self.radius * 1.2 + offset_x,
                            self.center_y + self.radius * 1.2 + offset_y + y_offset,
                            start=math.degrees(current_angle),
                            extent=math.degrees(slice_angle),
                            fill=shadow_color,
                            outline="",
                            style=tk.PIESLICE,
                            tags=('enlarged_side',)
                        )
                
                # Draw the top of the enlarged slice (elliptical for 3D, circular for 2D)
                enlarged_slice = self.canvas.create_arc(
                    self.center_x - self.radius * 1.2 + offset_x,
                    self.center_y - self.radius * 1.2 + offset_y,
                    self.center_x + self.radius * 1.2 + offset_x,
                    self.center_y + self.radius * 1.2 + offset_y - (self.thickness * self.tilt_factor if self.is_3d else 0),
                    start=math.degrees(current_angle),
                    extent=math.degrees(slice_angle),
                    fill=color,
                    outline=self.style.adjust_brightness(color, 1.1),
                    width=1,
                    style=tk.PIESLICE,
                    tags=('enlarged_slice',)
                )
                
                # Move the label outward (with safety check)
                if slice_index < len(self.label_items):
                    label_radius = self.radius * 1.4
                    lx = self.center_x + label_radius * math.cos(current_angle + slice_angle / 2) + offset_x
                    ly = self.center_y - label_radius * math.sin(current_angle + slice_angle / 2) + offset_y - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
                    self.canvas.coords(self.label_items[slice_index], lx, ly)
            except tk.TclError:
                pass  # Widget may have been destroyed
            
            if frame < frames:
                # Register animation callback with resource manager (Requirements: 3.2, 3.6)
                try:
                    after_id = self.canvas.after(delay, animate_explosion, frame + 1)
                    self.resource_manager.register_animation(after_id)
                except tk.TclError:
                    pass
        
        animate_explosion(0)

    def _reset_slice(self, slice_index: int):
        """Reset the slice and its label to their original positions and restore original color."""
        # Safety checks
        if not self.slice_angles or slice_index >= len(self.slice_angles):
            return
        if not self.original_colors or slice_index >= len(self.original_colors):
            return
        
        try:
            self.canvas.delete('enlarged_slice')
            self.canvas.delete('enlarged_side')
        except tk.TclError:
            pass
        
        self.selected_slice = None
        current_angle, end_angle = self.slice_angles[slice_index]
        slice_angle = end_angle - current_angle
        
        # Restore the original color of the slice
        color = self.original_colors[slice_index]
        try:
            for item in self.canvas.find_withtag(f'slice_{slice_index}'):
                if 'slice' in self.canvas.gettags(item) and 'side' not in self.canvas.gettags(item):
                    self.canvas.itemconfig(item, fill=color)
            
            # Redraw the slice at its original size (elliptical for 3D, circular for 2D)
            self.canvas.create_arc(
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.center_x + self.radius,
                self.center_y + self.radius - (self.thickness * self.tilt_factor if self.is_3d else 0),
                start=math.degrees(current_angle),
                extent=math.degrees(slice_angle),
                fill=color,
                outline=self.style.adjust_brightness(color, 1.1),
                width=1,
                style=tk.PIESLICE,
                tags=('slice', f'slice_{slice_index}')
            )
            
            # Move the label back to its original position (with safety check)
            if slice_index < len(self.label_items):
                mid_angle = current_angle + slice_angle / 2
                label_radius = self.radius * 1.2
                lx = self.center_x + label_radius * math.cos(mid_angle)
                ly = self.center_y - label_radius * math.sin(mid_angle) - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
                self.canvas.coords(self.label_items[slice_index], lx, ly)
        except tk.TclError:
            pass  # Widget may have been destroyed

    def _add_title(self, title: str):
        """Add a title to the pie chart"""
        self.canvas.create_text(
            self.center_x, 20,
            text=title,
            font=("Arial", 16, "bold"),
            fill=self.style.TEXT,
            anchor='center'
        )

# Usage example:
"""
# 3D Pie Chart
chart_3d = PieChart(is_3d=True)
chart_3d.style = ChartStyle(theme='light')  # Ensure you have the modern ChartStyle from previous response
data = [30, 20, 15, 35]
labels = ["A", "B", "C", "D"]
chart_3d.plot(data, labels)

# 2D Pie Chart
chart_2d = PieChart(is_3d=False)
chart_2d.style = ChartStyle(theme='light')
chart_2d.plot(data, labels)
"""