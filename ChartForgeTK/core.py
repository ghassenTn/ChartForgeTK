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


import math
import logging
from typing import List, Optional, Union, Tuple, Callable
import colorsys
import tkinter as tk
from tkinter import ttk, font

from .validation import DataValidator
from .resources import ResourceManager

logger = logging.getLogger('ChartForgeTK')


class TooltipManager:
    """
    Manages tooltip creation, display, and cleanup for charts.
    
    This class provides a centralized way to handle tooltips with:
    - Proper error handling for tooltip rendering failures (Requirements: 4.2)
    - Automatic cleanup when chart is destroyed (Requirements: 3.1, 7.6)
    - Graceful degradation if tooltip creation fails
    
    Requirements: 3.1, 4.2, 7.6
    """
    
    def __init__(self, chart: 'Chart'):
        """
        Initialize the TooltipManager.
        
        Args:
            chart: The Chart instance this manager is associated with
        """
        self._chart = chart
        self._tooltip: Optional[tk.Toplevel] = None
        self._tooltip_label: Optional[tk.Label] = None
        self._tooltip_frame: Optional[tk.Frame] = None
        self._is_visible = False
        self._creation_failed = False
    
    @property
    def tooltip(self) -> Optional[tk.Toplevel]:
        """Get the tooltip window, creating it if necessary."""
        if self._creation_failed:
            return None
        if self._tooltip is None:
            self._create_tooltip()
        return self._tooltip
    
    @property
    def is_visible(self) -> bool:
        """Check if the tooltip is currently visible."""
        return self._is_visible
    
    def _create_tooltip(self) -> bool:
        """
        Create the tooltip window with error handling.
        
        Returns:
            bool: True if tooltip was created successfully, False otherwise
            
        Requirements: 4.2
        """
        try:
            # Create tooltip window
            self._tooltip = tk.Toplevel()
            self._tooltip.withdraw()
            self._tooltip.overrideredirect(True)
            
            # Try to set topmost attribute (may not be supported on all platforms)
            try:
                self._tooltip.attributes('-topmost', True)
            except tk.TclError:
                logger.debug("Platform does not support -topmost attribute for tooltips")
            
            # Create tooltip frame and label
            from tkinter import ttk
            
            # Configure styles
            style = ttk.Style()
            style.configure('Tooltip.TFrame',
                           background=self._chart.style.TEXT,
                           relief='solid',
                           borderwidth=0)
            style.configure('Tooltip.TLabel',
                           background=self._chart.style.TEXT,
                           foreground=self._chart.style.BACKGROUND,
                           font=self._chart.style.TOOLTIP_FONT)
            
            self._tooltip_frame = ttk.Frame(self._tooltip, style='Tooltip.TFrame')
            self._tooltip_frame.pack(fill='both', expand=True)
            
            self._tooltip_label = ttk.Label(
                self._tooltip_frame,
                style='Tooltip.TLabel',
                font=self._chart.style.TOOLTIP_FONT
            )
            self._tooltip_label.pack(padx=8, pady=4)
            
            # Register with resource manager for cleanup (Requirements: 3.1, 7.6)
            if hasattr(self._chart, 'resource_manager') and self._chart.resource_manager:
                self._chart.resource_manager.register_tooltip(self._tooltip)
            
            logger.debug("Tooltip created successfully")
            return True
            
        except tk.TclError as e:
            logger.warning(f"Failed to create tooltip (TclError): {e}")
            self._creation_failed = True
            self._cleanup_partial()
            return False
        except Exception as e:
            logger.warning(f"Failed to create tooltip: {e}")
            self._creation_failed = True
            self._cleanup_partial()
            return False
    
    def _cleanup_partial(self) -> None:
        """Clean up partially created tooltip resources."""
        if self._tooltip:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
        self._tooltip = None
        self._tooltip_label = None
        self._tooltip_frame = None
    
    def show(self, x_root: int, y_root: int, text: str, 
             offset_x: int = 10, offset_y: int = -40) -> bool:
        """
        Show the tooltip at the specified position with the given text.
        
        Args:
            x_root: X coordinate in screen coordinates
            y_root: Y coordinate in screen coordinates
            text: Text to display in the tooltip
            offset_x: Horizontal offset from cursor position
            offset_y: Vertical offset from cursor position
            
        Returns:
            bool: True if tooltip was shown successfully, False otherwise
            
        Requirements: 4.2
        """
        if self._creation_failed:
            return False
        
        tooltip = self.tooltip
        if tooltip is None:
            return False
        
        try:
            # Update tooltip text
            if self._tooltip_label:
                self._tooltip_label.config(text=text)
            
            # Position and show tooltip
            tooltip.wm_geometry(f"+{x_root + offset_x}+{y_root + offset_y}")
            tooltip.deiconify()
            tooltip.lift()
            self._is_visible = True
            return True
            
        except tk.TclError as e:
            logger.debug(f"Failed to show tooltip (TclError): {e}")
            return False
        except Exception as e:
            logger.warning(f"Failed to show tooltip: {e}")
            return False
    
    def hide(self) -> bool:
        """
        Hide the tooltip.
        
        Returns:
            bool: True if tooltip was hidden successfully, False otherwise
            
        Requirements: 4.2
        """
        if self._tooltip is None:
            self._is_visible = False
            return True
        
        try:
            self._tooltip.withdraw()
            self._is_visible = False
            return True
        except tk.TclError as e:
            logger.debug(f"Failed to hide tooltip (TclError): {e}")
            self._is_visible = False
            return False
        except Exception as e:
            logger.warning(f"Failed to hide tooltip: {e}")
            self._is_visible = False
            return False
    
    def update_text(self, text: str) -> bool:
        """
        Update the tooltip text without changing visibility.
        
        Args:
            text: New text to display
            
        Returns:
            bool: True if text was updated successfully, False otherwise
        """
        if self._tooltip_label is None:
            return False
        
        try:
            self._tooltip_label.config(text=text)
            return True
        except tk.TclError:
            return False
        except Exception:
            return False
    
    def destroy(self) -> None:
        """
        Destroy the tooltip and clean up resources.
        
        Requirements: 3.1, 7.6
        """
        self._is_visible = False
        
        if self._tooltip is not None:
            try:
                # Unregister from resource manager first
                if hasattr(self._chart, 'resource_manager') and self._chart.resource_manager:
                    self._chart.resource_manager.unregister_tooltip(self._tooltip)
                
                self._tooltip.destroy()
                logger.debug("Tooltip destroyed successfully")
            except tk.TclError:
                logger.debug("Tooltip already destroyed")
            except Exception as e:
                logger.warning(f"Error destroying tooltip: {e}")
            finally:
                self._tooltip = None
                self._tooltip_label = None
                self._tooltip_frame = None
    
    def reset(self) -> None:
        """
        Reset the tooltip manager, allowing tooltip creation to be retried.
        
        This is useful after a failed creation attempt if conditions have changed.
        """
        self.destroy()
        self._creation_failed = False
    
    def __repr__(self) -> str:
        """Return a string representation of the TooltipManager."""
        return (
            f"TooltipManager(visible={self._is_visible}, "
            f"created={self._tooltip is not None}, "
            f"failed={self._creation_failed})"
        )

class ChartStyle:
    def __init__(self, theme='light'):
        self.theme = theme
        if theme == 'light':
            self.BACKGROUND = "#FFFFFF"  # Clean, crisp white
            self.TEXT = "#1E293B"        # Deep slate gray for strong contrast
            self.TEXT_SECONDARY = "#64748B"  # Soft gray-blue for secondary text
            self.PRIMARY = "#2563EB"     # Bold modern blue
            self.ACCENT = "#FACC15"      # Bright yellow-gold for highlights
            self.AXIS_COLOR = "#94A3B8"  # Muted blue-gray for axes
            self.GRID_COLOR = "#E2E8F0"  # Soft light gray for subtle grids
            self.TICK_COLOR = "#64748B"  # Subtle gray-blue for ticks
            self.SECONDARY = "#38BDF8"   # Fresh cyan-blue for contrast
            self.ACCENT_HOVER = "#FB923C"  # Soft orange for interactive elements
            
        else:  # dark
            self.BACKGROUND = "#0F172A"  # Deep navy for a sleek dark theme
            self.TEXT = "#E2E8F0"        # Light gray for text clarity
            self.TEXT_SECONDARY = "#94A3B8"  # Muted blue-gray for balance
            self.PRIMARY = "#3B82F6"     # Bright blue with a modern touch
            self.ACCENT = "#EAB308"      # Neon gold for highlights
            self.AXIS_COLOR = "#475569"  # Darker gray-blue for soft contrast
            self.GRID_COLOR = "#334155"  # Dark gray-blue for subtle grid lines
            self.TICK_COLOR = "#94A3B8"  # Muted blue-gray for balance
            self.SECONDARY = "#22D3EE"   # Vibrant cyan for secondary elements
            self.ACCENT_HOVER = "#F87171"  # Coral red for hover interactions
        
        self.PADDING = 50
        self.AXIS_WIDTH = 2
        self.GRID_WIDTH = 1
        self.TICK_LENGTH = 5
        self.TITLE_FONT = ("Helvetica", 14, "bold")
        self.LABEL_FONT = ("Helvetica", 10)
        self.AXIS_FONT = ("Helvetica", 10)
        self.VALUE_FONT = ("Helvetica", 12)
        self.TOOLTIP_FONT = ("Helvetica", 10)
        self.TOOLTIP_PADDING = 5

    def get_gradient_color(self, index, total):
        # Updated modern gradient with bold yet refined colors
        colors = [
            "#2563EB",  # Deep blue
            "#FACC15",  # Vivid gold
            "#F43F5E",  # Bold pinkish red
            "#10B981",  # Bright green
            "#8B5CF6",  # Elegant violet
        ]
        return colors[index % len(colors)]

    def get_histogram_color(self, index, total):
        # Modernized, vibrant but deep blue
        colors = ["#2563EB"]  
        return colors[index % len(colors)]

    def create_shadow(self, color):
        return self.adjust_brightness(color, 0.7)

    def adjust_brightness(self, color, factor):
        """
        Adjust the brightness of a color by a factor.
        
        This method includes error handling for invalid colors, falling back
        to a default color if parsing fails.
        
        Args:
            color: Hex color string (#RRGGBB or #RGB)
            factor: Brightness factor (0.0 to 2.0, where 1.0 is unchanged)
            
        Returns:
            str: Adjusted hex color string
            
        Requirements: 4.3, 8.2
        """
        try:
            # Parse the color
            rgb = DataValidator.parse_hex_color(color)
            if rgb is None:
                # Try to validate and normalize the color first
                try:
                    color = DataValidator.validate_color(color)
                    rgb = DataValidator.parse_hex_color(color)
                except (TypeError, ValueError):
                    pass
            
            if rgb is None:
                # Fall back to default color
                logger.warning(
                    f"Failed to parse color '{color}' for brightness adjustment. "
                    f"Using default color."
                )
                rgb = (37, 99, 235)  # Default blue
            
            r, g, b = rgb
            
            # Apply brightness factor with clamping
            r = DataValidator.clamp_rgb_value(r * factor)
            g = DataValidator.clamp_rgb_value(g * factor)
            b = DataValidator.clamp_rgb_value(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except Exception as e:
            logger.warning(f"Error adjusting brightness: {e}. Using default color.")
            return DataValidator.DEFAULT_FALLBACK_COLOR

    def validate_custom_color(self, color: str, default: str = None) -> str:
        """
        Validate a custom color with fallback to default.
        
        This method provides graceful degradation when custom colors are invalid.
        
        Args:
            color: Color string to validate
            default: Default color to use if validation fails
            
        Returns:
            str: Validated color or default
            
        Requirements: 4.3, 8.2
        """
        if default is None:
            default = self.PRIMARY
        return DataValidator.validate_color_with_fallback(color, default)


class Chart(tk.Frame):
    def __init__(self, parent=None, width: int = 400, height: int = 400, display_mode='frame', theme='light'):
        """Initialize chart with modern styling and enhanced features.
        
        Args:
            parent: Parent widget (required for 'frame' mode, optional for 'window' mode)
            width: Chart width in pixels (minimum 100)
            height: Chart height in pixels (minimum 100)
            display_mode: Either 'frame' (embedded) or 'window' (standalone)
            theme: Either 'light' or 'dark'
            
        Raises:
            TypeError: If parameters have incorrect types
            ValueError: If parameters have invalid values
            
        Requirements: 1.5, 8.3
        """
        # Validate input parameters using DataValidator
        width, height = DataValidator.validate_dimensions(width, height)
        theme = DataValidator.validate_theme(theme)
        display_mode = DataValidator.validate_display_mode(display_mode)

        self.style = ChartStyle(theme=theme)  # Pass theme to ChartStyle
        self.theme = theme
        self.display_mode = display_mode
        self.width = width
        self.height = height
        self.padding = self.style.PADDING
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.is_maximized = False
        self.original_geometry = None
        self._tooltip = None
        self._tooltip_label = None
        self._hover_tag = None
        self._click_callback = None
        # Add range variables for interactivity
        self.x_min = self.x_max = self.y_min = self.y_max = 0

        # Animation state tracking (Requirements: 6.1, 6.3)
        self._animation_in_progress = False

        if display_mode == 'window':
            self._initialize_window()

        super().__init__(parent)
        self._initialize_canvas()
        
        # Initialize ResourceManager for lifecycle management (Requirements: 3.1, 3.2, 3.6)
        self.resource_manager = ResourceManager(self)
        
        # Initialize TooltipManager for centralized tooltip handling (Requirements: 3.1, 4.2, 7.6)
        self.tooltip_manager = TooltipManager(self)

    def _initialize_window(self):
        """Initialize window mode with modern controls and proper event handling.
        
        This method sets up the window with:
        - Control buttons (minimize, maximize, close)
        - Proper event bindings for resize, maximize, and close
        - Error handling for window events
        
        Requirements: 7.5
        """
        try:
            self.window = tk.Toplevel()
            self.window.title("Chart View")
            self.window.configure(background=self.style.BACKGROUND)
            
            # Track window state
            self._window_closing = False

            control_frame = ttk.Frame(self.window)
            control_frame.pack(fill='x', padx=1, pady=1)

            style = ttk.Style()
            style.configure('WindowControl.TButton',
                           padding=4,
                           relief='flat',
                           background=self.style.BACKGROUND,
                           foreground=self.style.TEXT,
                           font=('Helvetica', 12))
            style.map('WindowControl.TButton',
                     background=[('active', self.style.PRIMARY)],
                     foreground=[('active', self.style.BACKGROUND)])

            close_btn = ttk.Button(control_frame, text="×", width=3,
                                  style='WindowControl.TButton', command=self._on_window_close)
            close_btn.pack(side='right', padx=1)

            self.maximize_btn = ttk.Button(control_frame, text="□", width=3,
                                          style='WindowControl.TButton', command=self._toggle_maximize)
            self.maximize_btn.pack(side='right', padx=1)

            minimize_btn = ttk.Button(control_frame, text="_", width=3,
                                     style='WindowControl.TButton', command=self._on_window_minimize)
            minimize_btn.pack(side='right', padx=1)

            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
            self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

            # Bind window events with error handling (Requirements: 7.5)
            self.window.bind("<Configure>", self._on_window_configure)
            self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            logger.debug("Window mode initialized successfully")
            
        except tk.TclError as e:
            logger.error(f"Failed to initialize window mode: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing window mode: {e}")
            raise

    def _initialize_canvas(self):
        """Initialize the canvas with modern styling."""
        self.canvas = tk.Canvas(self, width=self.width, height=self.height,
                               background=self.style.BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Button-1>", self._on_mouse_click)

    def _toggle_maximize(self):
        """Toggle between maximized and normal window state.
        
        This method handles maximize/restore with proper error handling.
        
        Requirements: 7.5
        """
        try:
            if not self.is_maximized:
                self.original_geometry = self.window.geometry()
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                self.window.geometry(f"{screen_width}x{screen_height}+0+0")
                self.maximize_btn.configure(text="❐")
                self.is_maximized = True
                logger.debug("Window maximized")
            else:
                if self.original_geometry:
                    self.window.geometry(self.original_geometry)
                self.maximize_btn.configure(text="□")
                self.is_maximized = False
                logger.debug("Window restored")
        except tk.TclError as e:
            logger.warning(f"Error toggling maximize state: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error toggling maximize: {e}")

    def _on_window_configure(self, event):
        """Handle window resize events with error handling.
        
        This method handles window resize events and redraws the chart
        appropriately, with proper error handling.
        
        Requirements: 7.5
        """
        try:
            # Only handle events from the window itself, not child widgets
            if event.widget != self.window:
                return
            
            # Check if window is being closed
            if hasattr(self, '_window_closing') and self._window_closing:
                return
            
            # Calculate new dimensions (accounting for control frame)
            new_width = max(100, event.width - 20)  # Enforce minimum
            new_height = max(100, event.height - 20)  # Enforce minimum
            
            # Only redraw if dimensions actually changed
            if new_width != self.width or new_height != self.height:
                self.width = new_width
                self.height = new_height
                
                # Update canvas size
                if hasattr(self, 'canvas') and self.canvas:
                    try:
                        self.canvas.configure(width=self.width, height=self.height)
                    except tk.TclError:
                        return  # Canvas may have been destroyed
                
                # Redraw the chart
                self.redraw()
                
        except tk.TclError as e:
            logger.debug(f"TclError in window configure handler: {e}")
        except Exception as e:
            logger.warning(f"Error in window configure handler: {e}")
    
    def _on_window_close(self):
        """Handle window close event with proper cleanup.
        
        This method ensures all resources are properly cleaned up
        when the window is closed.
        
        Requirements: 7.5
        """
        try:
            # Mark window as closing to prevent further event handling
            self._window_closing = True
            
            # Cancel any pending animations
            self.cancel_all_animations()
            
            # Clean up tooltip manager
            if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
                self.tooltip_manager.destroy()
            
            # Clean up resources
            if hasattr(self, 'resource_manager'):
                self.resource_manager.cleanup()
            
            # Destroy the window
            if hasattr(self, 'window') and self.window:
                try:
                    self.window.destroy()
                except tk.TclError:
                    pass
            
            logger.debug("Window closed and resources cleaned up")
            
        except tk.TclError as e:
            logger.debug(f"TclError during window close: {e}")
        except Exception as e:
            logger.warning(f"Error during window close: {e}")
    
    def _on_window_minimize(self):
        """Handle window minimize event.
        
        This method handles the minimize button click with proper error handling.
        
        Requirements: 7.5
        """
        try:
            if hasattr(self, 'window') and self.window:
                self.window.iconify()
                logger.debug("Window minimized")
        except tk.TclError as e:
            logger.warning(f"Error minimizing window: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error minimizing window: {e}")

    def _on_mouse_move(self, event):
        """Handle mouse move events for hover effects.
        
        This method includes error handling to ensure rapid mouse movements
        don't cause errors or crashes.
        
        Requirements: 7.2
        """
        try:
            # Hide tooltip using the manager or legacy approach
            if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
                self.tooltip_manager.hide()
            elif self._tooltip:
                try:
                    self._tooltip.withdraw()
                except tk.TclError:
                    pass
            
            self._hover_tag = self._get_hovered_element(event.x, event.y)
            if self._hover_tag:
                self._show_tooltip(event.x_root, event.y_root, self._hover_tag)
        except tk.TclError as e:
            # Widget may have been destroyed during event handling
            logger.debug(f"TclError in mouse move handler: {e}")
        except Exception as e:
            # Log error but don't crash (Requirements: 7.2)
            logger.warning(f"Error in mouse move handler: {e}")

    def _on_mouse_leave(self, event):
        """Handle mouse leave events.
        
        This method includes error handling to ensure mouse leave events
        don't cause errors.
        
        Requirements: 7.2
        """
        try:
            # Hide tooltip using the manager or legacy approach
            if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
                self.tooltip_manager.hide()
            elif self._tooltip:
                try:
                    self._tooltip.withdraw()
                except tk.TclError:
                    pass
            
            self._hover_tag = None
        except tk.TclError as e:
            logger.debug(f"TclError in mouse leave handler: {e}")
        except Exception as e:
            logger.warning(f"Error in mouse leave handler: {e}")

    def _on_mouse_click(self, event):
        """Handle mouse click events.
        
        This method includes error handling to ensure click events
        don't raise exceptions.
        
        Requirements: 7.3
        """
        try:
            if self._click_callback and self._hover_tag:
                self._click_callback(self._hover_tag)
        except tk.TclError as e:
            logger.debug(f"TclError in mouse click handler: {e}")
        except Exception as e:
            # Log error but don't crash (Requirements: 7.3)
            logger.warning(f"Error in mouse click handler: {e}")

    def _get_hovered_element(self, x: int, y: int) -> Optional[str]:
        """Get the hovered chart element (e.g., bar, point)."""
        return None  # Child classes override this


    def redraw(self):
        """Redraw the chart with current data."""
        self.clear()
        if hasattr(self, 'data'):
            if hasattr(self, 'redraw_chart'):
                self.redraw_chart()
            else:
                self.plot(self.data)

    def clear(self):
        """Clear the canvas and cancel pending animations.
        
        Requirements: 3.2, 3.6
        """
        # Cancel pending animations before clearing (Requirements: 3.2, 3.6, 6.1)
        self.cancel_all_animations()
        self.canvas.delete("all")
    
    def destroy(self):
        """Destroy the chart and clean up all resources.
        
        This method ensures proper cleanup of:
        - Tooltip windows (via TooltipManager and ResourceManager)
        - Animation callbacks
        - Event bindings
        
        Requirements: 3.1, 3.2, 3.6, 7.6
        """
        # Mark animation as stopped (Requirements: 6.1)
        self._animation_in_progress = False
        
        # Clean up tooltip manager first (Requirements: 3.1, 7.6)
        if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
            self.tooltip_manager.destroy()
        
        # Clean up all resources before destroying (Requirements: 3.1, 3.2, 3.6)
        if hasattr(self, 'resource_manager'):
            self.resource_manager.cleanup()
        
        # Clean up the legacy tooltip if it exists (for backward compatibility)
        if hasattr(self, '_tooltip') and self._tooltip:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
            self._tooltip = None
        
        # Destroy window if in window mode
        if hasattr(self, 'window') and self.display_mode == 'window':
            try:
                self.window.destroy()
            except Exception:
                pass
        
        # Call parent destroy
        super().destroy()

    def show(self):
        """Display the chart in window mode."""
        if self.display_mode == 'window':
            self.window.mainloop()

    def to_window(self):
        """Convert the chart to a separate window."""
        if self.display_mode != 'window':
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)

            new_chart = self.__class__(width=self.width, height=self.height, display_mode='window', theme=self.theme)
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label

            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            return new_chart

    def to_frame(self, parent):
        """Convert the chart to an embedded frame."""
        if self.display_mode != 'frame':
            current_data = getattr(self, 'data', None)
            current_labels = getattr(self, 'labels', None)

            new_chart = self.__class__(parent=parent, width=self.width, height=self.height, 
                                      display_mode='frame', theme=self.theme)
            new_chart.title = self.title
            new_chart.x_label = self.x_label
            new_chart.y_label = self.y_label

            if current_data is not None:
                if current_labels is not None:
                    new_chart.plot(current_data, current_labels)
                else:
                    new_chart.plot(current_data)
            return new_chart

    def _draw_axes(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw beautiful axes with grid lines, storing ranges for interactivity."""
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

        self._draw_grid(x_min, x_max, y_min, y_max)

        # Y-axis (left edge)
        self.canvas.create_line(
            self.padding, self.padding,
            self.padding, self.height - self.padding,
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )

        # X-axis (at y=0 or bottom if no zero)
        y_zero = 0 if y_min <= 0 <= y_max else y_min
        self.canvas.create_line(
            self.padding, self._data_to_pixel_y(y_zero, y_min, y_max),
            self.width - self.padding, self._data_to_pixel_y(y_zero, y_min, y_max),
            fill=self.style.AXIS_COLOR,
            width=self.style.AXIS_WIDTH,
            capstyle=tk.ROUND
        )

        self._draw_ticks(x_min, x_max, y_min, y_max)

        if self.title:
            self.canvas.create_text(
                self.width / 2, self.padding / 2, text=self.title,
                font=self.style.TITLE_FONT, fill=self.style.TEXT, anchor='center'
            )

        if self.x_label:
            self.canvas.create_text(
                self.width / 2, self.height - self.padding / 3, text=self.x_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center'
            )

        if self.y_label:
            self.canvas.create_text(
                self.padding / 3, self.height / 2, text=self.y_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center', angle=90
            )

    def _draw_grid(self, x_min, x_max, y_min, y_max):
        """Draw subtle grid lines."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        x = math.ceil(x_min / x_interval) * x_interval
        while x <= x_max:
            px = self._data_to_pixel_x(x, x_min, x_max)
            self.canvas.create_line(px, self.padding, px, self.height - self.padding,
                                   fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(2, 4))
            x += x_interval

        y = math.ceil(y_min / y_interval) * y_interval
        while y <= y_max:
            py = self._data_to_pixel_y(y, y_min, y_max)
            self.canvas.create_line(self.padding, py, self.width - self.padding, py,
                                   fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(2, 4))
            y += y_interval

    def _draw_ticks(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw axis ticks and labels with modern styling, preventing duplicates."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        # X-axis ticks and labels
        x = math.ceil(x_min / x_interval) * x_interval
        y_zero = 0 if y_min <= 0 <= y_max else y_min
        drawn_x_labels = set()  # Track drawn X labels to avoid duplicates
        while x <= x_max + 1e-10:  # Add small epsilon to handle floating-point edge cases
            px = self._data_to_pixel_x(x, x_min, x_max)
            py = self._data_to_pixel_y(y_zero, y_min, y_max)
            self.canvas.create_line(px, py, px, py + self.style.TICK_LENGTH,
                                   fill=self.style.TICK_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND)
            label = f"{x:g}"
            if label not in drawn_x_labels:
                self.canvas.create_text(px, py + self.style.TICK_LENGTH + 5, text=label,
                                       font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='n')
                drawn_x_labels.add(label)
            x += x_interval

        # Y-axis ticks and labels
        y = math.ceil(y_min / y_interval) * y_interval
        drawn_y_labels = set()  # Track drawn Y labels to avoid duplicates
        while y <= y_max + 1e-10:  # Add small epsilon to handle floating-point edge cases
            px = self.padding
            py = self._data_to_pixel_y(y, y_min, y_max)
            self.canvas.create_line(px - self.style.TICK_LENGTH, py, px, py,
                                   fill=self.style.TICK_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND)
            label = f"{y/1000:g}k" if abs(y) >= 1000 else f"{y:g}"
            if label not in drawn_y_labels and abs(py - self.height / 2) > 10:  # Avoid overlap near center
                self.canvas.create_text(px - self.style.TICK_LENGTH - 5, py, text=label,
                                       font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='e')
                drawn_y_labels.add(label)
            y += y_interval

    def _data_to_pixel_x(self, x: float, x_min: float, x_max: float) -> float:
        """Convert data coordinate to pixel coordinate for x-axis."""
        if x_max == x_min:
            return self.padding
        return self.padding + (x - x_min) * (self.width - 2 * self.padding) / (x_max - x_min)

    def _data_to_pixel_y(self, y: float, y_min: float, y_max: float) -> float:
        """Convert data coordinate to pixel coordinate for y-axis."""
        if y_max == y_min:
            return self.height - self.padding
        return self.height - self.padding - (y - y_min) * (self.height - 2 * self.padding) / (y_max - y_min)

    def _calculate_tick_interval(self, range: float) -> float:
        """Calculate a nice tick interval based on the range, aiming for 5-10 ticks."""
        if range == 0:
            return 1
        # Target 5-10 ticks across the range
        magnitude = math.pow(10, math.floor(math.log10(range)))
        normalized_range = range / magnitude
        if normalized_range <= 2:
            interval = magnitude / 5  # e.g., 0.2 for range 1-2
        elif normalized_range <= 5:
            interval = magnitude / 2  # e.g., 0.5 for range 2-5
        else:
            interval = magnitude      # e.g., 1 for range 5-10+
        return interval

    # Animation Management Methods (Requirements: 3.2, 3.6, 6.1, 6.3)
    
    @property
    def is_animating(self) -> bool:
        """Check if an animation is currently in progress.
        
        Returns:
            bool: True if animation is in progress, False otherwise
            
        Requirements: 6.1
        """
        return self._animation_in_progress
    
    def _widget_exists(self) -> bool:
        """Check if the chart widget and canvas still exist.
        
        This method safely checks if the widget is still valid and can be used
        for rendering. It's used to prevent callbacks from executing on
        destroyed widgets.
        
        Returns:
            bool: True if widget exists and is valid, False otherwise
            
        Requirements: 6.3
        """
        try:
            # Check if the canvas exists and is valid
            if not hasattr(self, 'canvas') or self.canvas is None:
                return False
            return self.canvas.winfo_exists()
        except tk.TclError:
            return False
        except Exception:
            return False
    
    def schedule_animation(
        self, 
        callback: Callable[[], None], 
        delay_ms: int = 16
    ) -> Optional[str]:
        """Schedule an animation callback with automatic widget existence check.
        
        This method wraps the callback to verify the widget still exists before
        executing. It also registers the callback with the resource manager for
        proper cleanup.
        
        Args:
            callback: The function to call after the delay
            delay_ms: Delay in milliseconds (default 16ms for ~60 FPS)
            
        Returns:
            str: The after ID if scheduled successfully, None if widget doesn't exist
            
        Requirements: 3.2, 3.6, 6.1, 6.3
        """
        # Check if widget exists before scheduling
        if not self._widget_exists():
            logger.debug("Widget does not exist, skipping animation schedule")
            return None
        
        def safe_callback():
            """Wrapper that checks widget existence before executing callback.
            
            Requirements: 6.3
            """
            # Verify widget still exists before executing
            if not self._widget_exists():
                logger.debug("Widget destroyed before animation callback executed")
                return
            
            try:
                callback()
            except tk.TclError as e:
                # Widget may have been destroyed during callback
                logger.debug(f"TclError during animation callback: {e}")
            except Exception as e:
                # Log error but don't crash (Requirements: 4.1)
                logger.error(f"Error in animation callback: {e}", exc_info=True)
        
        try:
            after_id = self.canvas.after(delay_ms, safe_callback)
            # Register with resource manager for cleanup (Requirements: 3.2, 3.6)
            self.resource_manager.register_animation(after_id)
            return after_id
        except tk.TclError as e:
            logger.debug(f"Failed to schedule animation: {e}")
            return None
    
    def cancel_all_animations(self) -> int:
        """Cancel all pending animations for this chart.
        
        This method should be called before starting a new animation or
        when the chart is being destroyed/redrawn.
        
        Returns:
            int: Number of animations cancelled
            
        Requirements: 3.2, 3.6, 6.1
        """
        self._animation_in_progress = False
        if hasattr(self, 'resource_manager'):
            return self.resource_manager.cancel_animations()
        return 0
    
    def start_animation(self) -> None:
        """Mark that an animation is starting.
        
        This method should be called at the beginning of an animation sequence.
        It cancels any existing animations before starting.
        
        Requirements: 6.1
        """
        # Cancel any existing animations first (Requirements: 6.1)
        self.cancel_all_animations()
        self._animation_in_progress = True
        logger.debug("Animation started")
    
    def end_animation(self) -> None:
        """Mark that an animation has completed.
        
        This method should be called when an animation sequence finishes.
        
        Requirements: 6.1
        """
        self._animation_in_progress = False
        logger.debug("Animation ended")
    
    # Tooltip Helper Methods (Requirements: 3.1, 4.2, 7.6)
    
    def show_tooltip(self, x_root: int, y_root: int, text: str,
                     offset_x: int = 10, offset_y: int = -40) -> bool:
        """
        Show a tooltip at the specified position.
        
        This method provides a convenient way to show tooltips with automatic
        error handling and graceful degradation.
        
        Args:
            x_root: X coordinate in screen coordinates
            y_root: Y coordinate in screen coordinates
            text: Text to display in the tooltip
            offset_x: Horizontal offset from cursor position
            offset_y: Vertical offset from cursor position
            
        Returns:
            bool: True if tooltip was shown successfully, False otherwise
            
        Requirements: 4.2
        """
        if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
            return self.tooltip_manager.show(x_root, y_root, text, offset_x, offset_y)
        return False
    
    def hide_tooltip(self) -> bool:
        """
        Hide the tooltip.
        
        Returns:
            bool: True if tooltip was hidden successfully, False otherwise
            
        Requirements: 4.2
        """
        if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
            return self.tooltip_manager.hide()
        return False
    
    def create_standalone_tooltip(self) -> Optional[Tuple[tk.Toplevel, tk.Label]]:
        """
        Create a standalone tooltip window for custom tooltip handling.
        
        This method creates a tooltip window that is automatically registered
        with the resource manager for cleanup. It provides graceful degradation
        if tooltip creation fails.
        
        Returns:
            Tuple of (tooltip_window, label) if successful, None if creation failed
            
        Requirements: 3.1, 4.2, 7.6
        """
        try:
            from tkinter import ttk
            
            # Create tooltip window
            tooltip = tk.Toplevel()
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            
            # Try to set topmost attribute
            try:
                tooltip.attributes('-topmost', True)
            except tk.TclError:
                pass  # Some platforms may not support this
            
            # Configure styles
            style = ttk.Style()
            style.configure('Tooltip.TFrame',
                           background=self.style.TEXT,
                           relief='solid',
                           borderwidth=0)
            style.configure('Tooltip.TLabel',
                           background=self.style.TEXT,
                           foreground=self.style.BACKGROUND,
                           font=self.style.TOOLTIP_FONT)
            
            # Create frame and label
            tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
            tooltip_frame.pack(fill='both', expand=True)
            
            label = ttk.Label(
                tooltip_frame,
                style='Tooltip.TLabel',
                font=self.style.TOOLTIP_FONT
            )
            label.pack(padx=8, pady=4)
            
            # Register with resource manager for cleanup (Requirements: 3.1, 7.6)
            self.resource_manager.register_tooltip(tooltip)
            
            return (tooltip, label)
            
        except tk.TclError as e:
            logger.warning(f"Failed to create standalone tooltip (TclError): {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to create standalone tooltip: {e}")
            return None
    
    # Event Callback Helper Methods (Requirements: 7.2, 7.3)
    
    def create_safe_event_handler(
        self, 
        handler: Callable[[tk.Event], None],
        event_name: str = "event"
    ) -> Callable[[tk.Event], None]:
        """
        Create a safe event handler wrapper with error handling.
        
        This method wraps an event handler to catch and log any errors,
        preventing crashes from rapid mouse movements or other events.
        
        Args:
            handler: The original event handler function
            event_name: Name of the event for logging purposes
            
        Returns:
            A wrapped handler function with error handling
            
        Requirements: 7.2, 7.3
        """
        def safe_handler(event: tk.Event) -> None:
            try:
                # Check if widget still exists
                if not self._widget_exists():
                    return
                handler(event)
            except tk.TclError as e:
                logger.debug(f"TclError in {event_name} handler: {e}")
            except Exception as e:
                logger.warning(f"Error in {event_name} handler: {e}")
        
        return safe_handler
    
    def bind_safe_event(
        self, 
        sequence: str, 
        handler: Callable[[tk.Event], None],
        widget: Optional[tk.Widget] = None
    ) -> Optional[str]:
        """
        Bind an event with automatic error handling and resource registration.
        
        This method binds an event handler with automatic error handling
        and registers the binding with the resource manager for cleanup.
        
        Args:
            sequence: The event sequence (e.g., '<Motion>', '<Button-1>')
            handler: The event handler function
            widget: The widget to bind to (defaults to canvas)
            
        Returns:
            The function ID if binding was successful, None otherwise
            
        Requirements: 3.5, 7.2, 7.3
        """
        target_widget = widget if widget is not None else self.canvas
        
        try:
            # Create safe handler wrapper
            safe_handler = self.create_safe_event_handler(handler, sequence)
            
            # Bind the event
            func_id = target_widget.bind(sequence, safe_handler)
            
            # Register with resource manager for cleanup (Requirements: 3.5)
            self.resource_manager.register_binding(target_widget, sequence, func_id)
            
            return func_id
        except tk.TclError as e:
            logger.warning(f"Failed to bind {sequence} event: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error binding {sequence} event: {e}")
            return None

    
