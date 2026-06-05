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
            self._tooltip = tk.Toplevel()
            self._tooltip.withdraw()
            self._tooltip.overrideredirect(True)
            
            try:
                self._tooltip.attributes('-topmost', True)
            except tk.TclError:
                logger.debug("Platform does not support -topmost attribute for tooltips")
            
            style = ttk.Style()
            bg = self._chart.style.TOOLTIP_BG
            fg = self._chart.style.TOOLTIP_TEXT
            
            style.configure('Tooltip.TFrame',
                           background=bg,
                           relief='solid',
                           borderwidth=0)
            style.configure('Tooltip.TLabel',
                           background=bg,
                           foreground=fg,
                           font=self._chart.style.TOOLTIP_FONT)
            
            self._tooltip_frame = ttk.Frame(self._tooltip, style='Tooltip.TFrame')
            self._tooltip_frame.pack(fill='both', expand=True)
            
            self._tooltip_label = ttk.Label(
                self._tooltip_frame,
                style='Tooltip.TLabel',
                font=self._chart.style.TOOLTIP_FONT
            )
            self._tooltip_label.pack(padx=10, pady=6)
            
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
             offset_x: int = 12, offset_y: int = -45) -> bool:
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
            if self._tooltip_label:
                self._tooltip_label.config(text=text)
            
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
    THEMES = {
        'light': {
            'BACKGROUND': "#FFFFFF",
            'TEXT': "#1E293B",
            'TEXT_SECONDARY': "#64748B",
            'PRIMARY': "#2563EB",
            'ACCENT': "#FACC15",
            'AXIS_COLOR': "#94A3B8",
            'GRID_COLOR': "#E2E8F0",
            'TICK_COLOR': "#64748B",
            'SECONDARY': "#38BDF8",
            'ACCENT_HOVER': "#FB923C",
            'TOOLTIP_BG': "#1E293B",
            'TOOLTIP_TEXT': "#FFFFFF",
            'HIGHLIGHT_GLOW': "#2563EB",
        },
        'dark': {
            'BACKGROUND': "#0F172A",
            'TEXT': "#E2E8F0",
            'TEXT_SECONDARY': "#94A3B8",
            'PRIMARY': "#3B82F6",
            'ACCENT': "#EAB308",
            'AXIS_COLOR': "#475569",
            'GRID_COLOR': "#1E293B",
            'TICK_COLOR': "#94A3B8",
            'SECONDARY': "#22D3EE",
            'ACCENT_HOVER': "#F87171",
            'TOOLTIP_BG': "#E2E8F0",
            'TOOLTIP_TEXT': "#0F172A",
            'HIGHLIGHT_GLOW': "#3B82F6",
        },
        'corporate': {
            'BACKGROUND': "#F8FAFC",
            'TEXT': "#0F172A",
            'TEXT_SECONDARY': "#475569",
            'PRIMARY': "#1E40AF",
            'ACCENT': "#059669",
            'AXIS_COLOR': "#CBD5E1",
            'GRID_COLOR': "#F1F5F9",
            'TICK_COLOR': "#64748B",
            'SECONDARY': "#0D9488",
            'ACCENT_HOVER': "#DC2626",
            'TOOLTIP_BG': "#0F172A",
            'TOOLTIP_TEXT': "#F8FAFC",
            'HIGHLIGHT_GLOW': "#1E40AF",
        },
        'pastel': {
            'BACKGROUND': "#FDF2F8",
            'TEXT': "#4A1942",
            'TEXT_SECONDARY': "#9D5C8D",
            'PRIMARY': "#A78BFA",
            'ACCENT': "#F9A8D4",
            'AXIS_COLOR': "#E5D5E0",
            'GRID_COLOR': "#F3E8F0",
            'TICK_COLOR': "#9D5C8D",
            'SECONDARY': "#67E8F9",
            'ACCENT_HOVER': "#FDBA74",
            'TOOLTIP_BG': "#4A1942",
            'TOOLTIP_TEXT': "#FDF2F8",
            'HIGHLIGHT_GLOW': "#A78BFA",
        },
        'monochrome': {
            'BACKGROUND': "#FFFFFF",
            'TEXT': "#111111",
            'TEXT_SECONDARY': "#666666",
            'PRIMARY': "#333333",
            'ACCENT': "#000000",
            'AXIS_COLOR': "#CCCCCC",
            'GRID_COLOR': "#E8E8E8",
            'TICK_COLOR': "#888888",
            'SECONDARY': "#555555",
            'ACCENT_HOVER': "#999999",
            'TOOLTIP_BG': "#111111",
            'TOOLTIP_TEXT': "#FFFFFF",
            'HIGHLIGHT_GLOW': "#333333",
        },
        'ocean': {
            'BACKGROUND': "#ECFEFF",
            'TEXT': "#164E63",
            'TEXT_SECONDARY': "#0E7490",
            'PRIMARY': "#0891B2",
            'ACCENT': "#2DD4BF",
            'AXIS_COLOR': "#A5F3FC",
            'GRID_COLOR': "#CFFAFE",
            'TICK_COLOR': "#0E7490",
            'SECONDARY': "#06B6D4",
            'ACCENT_HOVER': "#F59E0B",
            'TOOLTIP_BG': "#164E63",
            'TOOLTIP_TEXT': "#ECFEFF",
            'HIGHLIGHT_GLOW': "#0891B2",
        },
        'sunset': {
            'BACKGROUND': "#FFFBEB",
            'TEXT': "#7C2D12",
            'TEXT_SECONDARY': "#B45309",
            'PRIMARY': "#EA580C",
            'ACCENT': "#FBBF24",
            'AXIS_COLOR': "#FDE68A",
            'GRID_COLOR': "#FEF3C7",
            'TICK_COLOR': "#B45309",
            'SECONDARY': "#EC4899",
            'ACCENT_HOVER': "#EF4444",
            'TOOLTIP_BG': "#7C2D12",
            'TOOLTIP_TEXT': "#FFFBEB",
            'HIGHLIGHT_GLOW': "#EA580C",
        },
        'forest': {
            'BACKGROUND': "#F0FDF4",
            'TEXT': "#14532D",
            'TEXT_SECONDARY': "#166534",
            'PRIMARY': "#16A34A",
            'ACCENT': "#4ADE80",
            'AXIS_COLOR': "#BBF7D0",
            'GRID_COLOR': "#DCFCE7",
            'TICK_COLOR': "#166534",
            'SECONDARY': "#15803D",
            'ACCENT_HOVER': "#EAB308",
            'TOOLTIP_BG': "#14532D",
            'TOOLTIP_TEXT': "#F0FDF4",
            'HIGHLIGHT_GLOW': "#16A34A",
        },
    }

    PALETTES = {
        'modern': [
            "#2563EB", "#FACC15", "#F43F5E", "#10B981", "#8B5CF6",
            "#FB923C", "#06B6D4", "#EC4899", "#84CC16", "#6366F1",
        ],
        'corporate': [
            "#1E40AF", "#047857", "#B91C1C", "#7C3AED", "#B45309",
            "#0F766E", "#831843", "#1E3A5F", "#4A5568", "#2D3748",
        ],
        'pastel': [
            "#A78BFA", "#F9A8D4", "#67E8F9", "#FDBA74", "#86EFAC",
            "#FDE047", "#C4B5FD", "#FDA4AF", "#A7F3D0", "#FCD34D",
        ],
        'vibrant': [
            "#FF006E", "#8338EC", "#3A86FF", "#06D6A0", "#FFBE0B",
            "#FB5607", "#FF006E", "#7209B7", "#4CC9F0", "#F72585",
        ],
        'monochrome': [
            "#1a1a1a", "#333333", "#4d4d4d", "#666666", "#808080",
            "#999999", "#b3b3b3", "#cccccc", "#e6e6e6", "#f2f2f2",
        ],
        'ocean': [
            "#08306B", "#08519C", "#2171B5", "#4292C6", "#6BAED6",
            "#9ECAE1", "#C6DBEF", "#DEEBF7", "#F7FBFF", "#045a8d",
        ],
        'sunset': [
            "#7C2D12", "#9A3412", "#C2410C", "#EA580C", "#F97316",
            "#FB923C", "#FDBA74", "#FED7AA", "#FFEDD5", "#431407",
        ],
        'forest': [
            "#14532D", "#166534", "#15803D", "#16A34A", "#22C55E",
            "#4ADE80", "#86EFAC", "#BBF7D0", "#DCFCE7", "#052E16",
        ],
    }

    def __init__(self, theme='light', palette='modern'):
        self.theme = theme
        self.palette_name = palette
        self._load_theme(theme)
        self._load_palette(palette)

    def _load_theme(self, theme):
        theme_data = self.THEMES.get(theme, self.THEMES['light'])
        for key, value in theme_data.items():
            setattr(self, key, value)

        self.PADDING = 50
        self.AXIS_WIDTH = 1.5
        self.GRID_WIDTH = 1
        self.TICK_LENGTH = 6
        self.TITLE_FONT = ("Helvetica", 14, "bold")
        self.LABEL_FONT = ("Helvetica", 10)
        self.AXIS_FONT = ("Helvetica", 9)
        self.VALUE_FONT = ("Helvetica", 11)
        self.TOOLTIP_FONT = ("Helvetica", 10)
        self.TOOLTIP_PADDING = 8

    def _load_palette(self, palette):
        self._palette = self.PALETTES.get(palette, self.PALETTES['modern'])

    def set_theme(self, theme):
        self.theme = theme
        self._load_theme(theme)

    def set_palette(self, palette):
        self.palette_name = palette
        self._load_palette(palette)

    def get_color(self, index):
        return self._palette[index % len(self._palette)]

    def get_gradient_color(self, index, total):
        return self.get_color(index)

    def get_histogram_color(self, index, total):
        return self._palette[0] if self._palette else "#2563EB"

    def create_shadow(self, color, factor=0.6):
        return self.adjust_brightness(color, factor)

    def create_lighter(self, color, factor=1.3):
        return self.adjust_brightness(color, factor)

    def adjust_brightness(self, color, factor):
        try:
            rgb = DataValidator.parse_hex_color(color)
            if rgb is None:
                try:
                    color = DataValidator.validate_color(color)
                    rgb = DataValidator.parse_hex_color(color)
                except (TypeError, ValueError):
                    pass
            if rgb is None:
                rgb = (37, 99, 235)
            r, g, b = rgb
            r = DataValidator.clamp_rgb_value(r * factor)
            g = DataValidator.clamp_rgb_value(g * factor)
            b = DataValidator.clamp_rgb_value(b * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return "#2563EB"

    def validate_custom_color(self, color, default=None):
        if default is None:
            default = self.PRIMARY
        return DataValidator.validate_color_with_fallback(color, default)

    @staticmethod
    def blend_colors(color1, color2, ratio=0.5):
        c1 = DataValidator.parse_hex_color(color1) or (0, 0, 0)
        c2 = DataValidator.parse_hex_color(color2) or (0, 0, 0)
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class ChartRenderer:
    @staticmethod
    def create_rounded_rect(canvas, x1, y1, x2, y2, radius=8, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    @staticmethod
    def create_drop_shadow(canvas, x1, y1, x2, y2, offset=4, blur=3, color="#000000", alpha=0.15):
        shadow_items = []
        for i in range(blur):
            alpha_step = alpha / blur
            gray = int(255 * (1 - alpha_step * (blur - i)))
            shadow_color = f"#{gray:02x}{gray:02x}{gray:02x}"
            shadow_items.append(
                canvas.create_rectangle(
                    x1 + offset + i, y1 + offset + i,
                    x2 + offset + i, y2 + offset + i,
                    fill=shadow_color, outline="", tags=('shadow',)
                )
            )
        return shadow_items

    @staticmethod
    def create_bar_gradient(canvas, x1, y1, x2, y2, color, steps=20):
        items = []
        step_height = (y2 - y1) / steps
        for i in range(steps):
            ratio = i / steps
            r, g, b = ChartStyle.hex_to_rgb(color)
            factor = 0.85 + 0.15 * (1 - ratio)
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            grad_color = f"#{r:02x}{g:02x}{b:02x}"
            items.append(
                canvas.create_rectangle(
                    x1, y1 + i * step_height,
                    x2, y1 + (i + 1) * step_height + 1,
                    fill=grad_color, outline="", tags=('gradient',)
                )
            )
        return items

    @staticmethod
    def create_tooltip_bg(canvas, x, y, width, height, color, radius=8):
        return ChartRenderer.create_rounded_rect(
            canvas, x, y, x + width, y + height,
            radius=radius, fill=color, outline=color, tags=('tooltip_bg',)
        )

    @staticmethod
    def create_glow_effect(canvas, x1, y1, x2, y2, color, width=4, steps=3):
        items = []
        for i in range(steps):
            alpha = 1.0 - (i / steps)
            items.append(
                canvas.create_rectangle(
                    x1 - width * alpha, y1 - width * alpha,
                    x2 + width * alpha, y2 + width * alpha,
                    outline=color, width=width * alpha * 0.5,
                    fill="", tags=('glow',)
                )
            )
        return items


class Chart(tk.Frame):
    def __init__(self, parent=None, width: int = 400, height: int = 400, display_mode='frame', theme='light', palette='modern'):
        """Initialize chart with modern styling and enhanced features.
        
        Args:
            parent: Parent widget (required for 'frame' mode, optional for 'window' mode)
            width: Chart width in pixels (minimum 100)
            height: Chart height in pixels (minimum 100)
            display_mode: Either 'frame' (embedded) or 'window' (standalone)
            theme: Color theme ('light', 'dark', 'corporate', 'pastel', 'monochrome', 'ocean', 'sunset', 'forest')
            palette: Color palette ('modern', 'corporate', 'pastel', 'vibrant', 'monochrome', 'ocean', 'sunset', 'forest')
            
        Raises:
            TypeError: If parameters have incorrect types
            ValueError: If parameters have invalid values
            
        Requirements: 1.5, 8.3
        """
        # Validate input parameters using DataValidator
        width, height = DataValidator.validate_dimensions(width, height)
        theme = DataValidator.validate_theme(theme)
        display_mode = DataValidator.validate_display_mode(display_mode)

        self.style = ChartStyle(theme=theme, palette=palette)
        self.theme = theme
        self.palette = palette
        self.renderer = ChartRenderer()
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

            new_chart = self.__class__(width=self.width, height=self.height, display_mode='window', theme=self.theme, palette=self.palette)
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
                                      display_mode='frame', theme=self.theme, palette=self.palette)
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

        plot_left = self.padding
        plot_right = self.width - self.padding
        plot_top = self.padding
        plot_bottom = self.height - self.padding

        # Determine Y-axis baseline
        y_zero = 0 if y_min <= 0 <= y_max else y_min
        y_zero_px = self._data_to_pixel_y(y_zero, y_min, y_max)

        # Draw zero-line emphasis if zero is within range
        if y_min <= 0 <= y_max:
            self.canvas.create_line(
                plot_left, y_zero_px, plot_right, y_zero_px,
                fill=self.style.adjust_brightness(self.style.AXIS_COLOR, 0.7),
                width=self.style.AXIS_WIDTH + 0.5, capstyle=tk.ROUND
            )
        else:
            # X-axis at bottom
            self.canvas.create_line(
                plot_left, plot_bottom, plot_right, plot_bottom,
                fill=self.style.AXIS_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND
            )

        # Y-axis (left edge)
        self.canvas.create_line(
            plot_left, plot_top, plot_left, plot_bottom,
            fill=self.style.AXIS_COLOR, width=self.style.AXIS_WIDTH, capstyle=tk.ROUND
        )

        # Subtle top and right border lines for frame effect
        self.canvas.create_line(
            plot_left, plot_top, plot_right, plot_top,
            fill=self.style.GRID_COLOR, width=1
        )
        self.canvas.create_line(
            plot_right, plot_top, plot_right, plot_bottom,
            fill=self.style.GRID_COLOR, width=1
        )

        self._draw_ticks(x_min, x_max, y_min, y_max)

        if self.title:
            self.canvas.create_text(
                self.width / 2, plot_top / 2.5, text=self.title,
                font=self.style.TITLE_FONT, fill=self.style.TEXT, anchor='center'
            )

        if self.x_label:
            self.canvas.create_text(
                self.width / 2, self.height - self.padding / 4, text=self.x_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center'
            )

        if self.y_label:
            self.canvas.create_text(
                plot_left / 3, self.height / 2, text=self.y_label,
                font=self.style.LABEL_FONT, fill=self.style.TEXT_SECONDARY, anchor='center', angle=90
            )

    def _draw_grid(self, x_min, x_max, y_min, y_max):
        """Draw subtle grid lines."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        plot_left = self.padding
        plot_right = self.width - self.padding
        plot_top = self.padding
        plot_bottom = self.height - self.padding

        # Draw horizontal grid lines (subtle)
        y = math.ceil(y_min / y_interval) * y_interval
        while y <= y_max:
            if y == 0:
                y += y_interval
                continue
            py = self._data_to_pixel_y(y, y_min, y_max)
            if plot_top < py < plot_bottom:
                self.canvas.create_line(
                    plot_left, py, plot_right, py,
                    fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(3, 5)
                )
            y += y_interval

        # Draw vertical grid lines (subtle)
        x = math.ceil(x_min / x_interval) * x_interval
        while x <= x_max:
            px = self._data_to_pixel_x(x, x_min, x_max)
            if plot_left < px < plot_right:
                self.canvas.create_line(
                    px, plot_top, px, plot_bottom,
                    fill=self.style.GRID_COLOR, width=self.style.GRID_WIDTH, dash=(3, 5)
                )
            x += x_interval

    def _draw_ticks(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Draw axis ticks and labels with modern styling, preventing duplicates."""
        x_interval = self._calculate_tick_interval(x_max - x_min)
        y_interval = self._calculate_tick_interval(y_max - y_min)

        plot_left = self.padding
        plot_right = self.width - self.padding
        plot_top = self.padding
        plot_bottom = self.height - self.padding

        y_zero = 0 if y_min <= 0 <= y_max else y_min
        y_zero_px = self._data_to_pixel_y(y_zero, y_min, y_max)

        # X-axis ticks and labels
        x = math.ceil(x_min / x_interval) * x_interval
        drawn_x_labels = set()
        while x <= x_max + 1e-10:
            px = self._data_to_pixel_x(x, x_min, x_max)
            if plot_left < px < plot_right:
                self.canvas.create_line(
                    px, y_zero_px, px, y_zero_px + self.style.TICK_LENGTH,
                    fill=self.style.TICK_COLOR, width=1, capstyle=tk.ROUND
                )
                label = f"{x:g}"
                if label not in drawn_x_labels:
                    self.canvas.create_text(
                        px, y_zero_px + self.style.TICK_LENGTH + 6, text=label,
                        font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='n'
                    )
                    drawn_x_labels.add(label)
            x += x_interval

        # Y-axis ticks and labels
        y = math.ceil(y_min / y_interval) * y_interval
        drawn_y_labels = set()
        while y <= y_max + 1e-10:
            py = self._data_to_pixel_y(y, y_min, y_max)
            if plot_top < py < plot_bottom:
                self.canvas.create_line(
                    plot_left - self.style.TICK_LENGTH, py, plot_left, py,
                    fill=self.style.TICK_COLOR, width=1, capstyle=tk.ROUND
                )
                if abs(y) >= 1000:
                    label = f"{y/1000:g}k"
                elif y == int(y):
                    label = f"{int(y):,}"
                else:
                    label = f"{y:g}"
                if label not in drawn_y_labels:
                    self.canvas.create_text(
                        plot_left - self.style.TICK_LENGTH - 6, py, text=label,
                        font=self.style.AXIS_FONT, fill=self.style.TEXT_SECONDARY, anchor='e'
                    )
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
            
            tooltip = tk.Toplevel()
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            
            try:
                tooltip.attributes('-topmost', True)
            except tk.TclError:
                pass
            
            style = ttk.Style()
            bg = self.style.TOOLTIP_BG
            fg = self.style.TOOLTIP_TEXT
            style.configure('Tooltip.TFrame',
                           background=bg,
                           relief='solid',
                           borderwidth=0)
            style.configure('Tooltip.TLabel',
                           background=bg,
                           foreground=fg,
                           font=self.style.TOOLTIP_FONT)
            
            tooltip_frame = ttk.Frame(tooltip, style='Tooltip.TFrame')
            tooltip_frame.pack(fill='both', expand=True)
            
            label = ttk.Label(
                tooltip_frame,
                style='Tooltip.TLabel',
                font=self.style.TOOLTIP_FONT
            )
            label.pack(padx=10, pady=6)
            
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

    
