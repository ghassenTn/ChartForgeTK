from typing import List, Optional, Union, Tuple
import tkinter as tk
from tkinter import ttk
import math
from .core import Chart, ChartStyle

class PieChart(Chart):
    def __init__(self, parent=None, width: int = 800, height: int = 600, display_mode='frame', is_3d: bool = False):
        super().__init__(parent, width=width, height=height, display_mode=display_mode)
        self.data = []
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

    def plot(self, data: List[float], labels: Optional[List[str]] = None):
        """Plot the pie chart with the given data and optional labels"""
        if not data:
            raise ValueError("Data cannot be empty")
        if not all(isinstance(x, (int, float)) for x in data):
            raise TypeError("All data points must be numbers")
        if any(x < 0 for x in data):
            raise ValueError("Pie chart data cannot contain negative values")
        if labels and len(labels) != len(data):
            raise ValueError("Number of labels must match number of data points")
            
        self.data = data
        self.labels = labels or [f"Slice {i}" for i in range(len(data))]
        self.total = sum(data)
        self._add_title("3D Pie Chart" if self.is_3d else "Pie Chart")
        # Clear previous content
        self.canvas.delete('all')
        
        # Reset stored colors
        self.original_colors = []
        
        # Animate the pie chart drawing
        self._animate_pie()
        self._add_interactive_effects()

    def _animate_pie(self):
        """Draw the pie chart with smooth animation, optionally with 3D effect"""
        def ease(t):
            return t * t * (3 - 2 * t)  # Ease-in-out
        
        self.slices = []  # Reset slices list
        self.slice_angles = []  # Reset slice angles list
        self.label_items = []  # Reset label items list
        self.original_colors = []  # Reset original colors list
        
        def update_animation(frame: int, total_frames: int):
            progress = ease(frame / total_frames)
            current_angle = 0
            
            # Clear previous slices and labels
            for item in self.slices + self.label_items:
                self.canvas.delete(item)
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
                
                # Add label when slice is fully drawn
                if progress == 1:
                    mid_angle = current_angle + angle / 2
                    label_radius = self.radius * 1.2
                    lx = self.center_x + label_radius * math.cos(mid_angle)
                    ly = self.center_y - label_radius * math.sin(mid_angle) - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
                    percentage = (value / self.total) * 100
                    label_text = f"{self.labels[i]}\n{percentage:.1f}%"
                    
                    label = self.canvas.create_text(
                        lx, ly,
                        text=label_text,
                        font=self.style.VALUE_FONT,
                        fill=self.style.TEXT,
                        justify='center',
                        tags=('label', f'slice_{i}')
                    )
                    self.label_items.append(label)
                
                current_angle = end_angle
            
            if frame < total_frames:
                self.canvas.after(16, update_animation, frame + 1, total_frames)
        
        total_frames = self.animation_duration // 16  # ~60 FPS
        update_animation(0, total_frames)

    def _add_interactive_effects(self):
        """Add hover effects and tooltips"""
        tooltip = tk.Toplevel()
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)
        
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
            nonlocal current_highlight
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
                        break
                    current_angle += slice_angle
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
        
        def on_click(event):
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
                        self._enlarge_slice(i)
                        break
                    current_angle += slice_angle
        
        self.canvas.bind('<Motion>', on_motion)
        self.canvas.bind('<Leave>', on_leave)
        self.canvas.bind('<Button-1>', on_click)

    def _enlarge_slice(self, slice_index: int):
        """Enlarge the selected slice with animation, optionally with 3D effect"""
        if self.selected_slice is not None:
            self._reset_slice(self.selected_slice)
        
        self.selected_slice = slice_index
        current_angle, end_angle = self.slice_angles[slice_index]
        slice_angle = end_angle - current_angle
        
        # Change the original slice color to white
        for item in self.canvas.find_withtag(f'slice_{slice_index}'):
            if 'slice' in self.canvas.gettags(item) and 'side' not in self.canvas.gettags(item):
                self.canvas.itemconfig(item, fill='white')
        
        # Animation parameters
        explosion_offset = 20  # Maximum explosion distance
        frames = 5  # Number of animation frames
        delay = 16  # Delay between frames (ms)
        
        def animate_explosion(frame):
            progress = frame / frames
            offset = explosion_offset * progress
            offset_x = offset * math.cos(current_angle + slice_angle / 2)
            offset_y = -offset * math.sin(current_angle + slice_angle / 2)
            color = self.original_colors[slice_index]
            shadow_color = self.style.create_shadow(color)
            
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
            
            # Move the label outward
            label_radius = self.radius * 1.4
            lx = self.center_x + label_radius * math.cos(current_angle + slice_angle / 2) + offset_x
            ly = self.center_y - label_radius * math.sin(current_angle + slice_angle / 2) + offset_y - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
            self.canvas.coords(self.label_items[slice_index], lx, ly)
            
            if frame < frames:
                self.canvas.after(delay, animate_explosion, frame + 1)
        
        animate_explosion(0)

    def _reset_slice(self, slice_index: int):
        """Reset the slice and its label to their original positions and restore original color"""
        self.canvas.delete('enlarged_slice')
        self.canvas.delete('enlarged_side')
        self.selected_slice = None
        current_angle, end_angle = self.slice_angles[slice_index]
        slice_angle = end_angle - current_angle
        
        # Restore the original color of the slice
        color = self.original_colors[slice_index]
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
        
        # Move the label back to its original position
        mid_angle = current_angle + slice_angle / 2
        label_radius = self.radius * 1.2
        lx = self.center_x + label_radius * math.cos(mid_angle)
        ly = self.center_y - label_radius * math.sin(mid_angle) - (self.thickness * self.tilt_factor / 2 if self.is_3d else 0)
        self.canvas.coords(self.label_items[slice_index], lx, ly)

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