import colorsys
from typing import List, Tuple

class Theme:
    def __init__(self):
        self.background_color = "#ffffff"
        self.border_color = "#ffffff"
        self.outline_color = "#e0e0e0"
        self.primary_color = "#2196F3"
        self.secondary_color = "#FF4081"
        self.text_color = "#333333"
        self.grid_color = "#f5f5f5"
        
        # Font settings
        self.font_family = "Helvetica"
        self.title_font_size = "16px"
        self.axis_font_size = "12px"
        self.label_font_size = "10px"

class ModernStyle:
    """Modern theme with vibrant colors and clean design"""
    
    def __init__(self):
        # Color palette
        self.PRIMARY = "#1A237E"  # Deep indigo
        self.ACCENT = "#304FFE"   # Bright indigo
        self.TEXT = "#1E293B"     # Slate 800
        self.BACKGROUND = "#FFFFFF"
        self.GRID = "#E2E8F0"     # Slate 200
        self.SHADOW = "#94A3B8"   # Slate 400
        
        # Chart colors - Modern, vibrant palette
        self.CHART_COLORS = [
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
        
        # Typography
        self.TITLE_FONT = ("Inter", 16, "bold")
        self.AXIS_FONT = ("Inter", 11)
        self.VALUE_FONT = ("Inter", 10)
        self.LABEL_FONT = ("Inter", 10)
        self.TOOLTIP_FONT = ("Inter", 10)
        
        # Layout
        self.PADDING = 40
        self.TICK_LENGTH = 6
        self.GRID_WIDTH = 1
        self.AXIS_WIDTH = 1.5
        
        # Animation
        self.ANIMATION_DURATION = 300  # milliseconds
        self.HOVER_ANIMATION_DURATION = 150  # milliseconds
        
    def get_gradient_color(self, index: int, total: int) -> str:
        """Get a beautiful color from the palette with proper distribution."""
        if total <= 1:
            return self.CHART_COLORS[0]
        color_index = int((index / (total - 1)) * (len(self.CHART_COLORS) - 1))
        return self.CHART_COLORS[color_index]
    
    def create_gradient(self, color: str, alpha_start: float = 0.15, alpha_end: float = 0.02) -> List[str]:
        """Create a smooth gradient from a color."""
        gradient_steps = 20
        base_rgb = self._hex_to_rgb(color)
        gradient = []
        
        for i in range(gradient_steps):
            alpha = alpha_start - (alpha_start - alpha_end) * (i / gradient_steps)
            gradient_color = self._create_rgba(*base_rgb, alpha)
            gradient.append(gradient_color)
        
        return gradient
    
    def create_shadow(self, color: str = None, opacity: float = 0.15) -> str:
        """Create a beautiful shadow with proper opacity."""
        if color is None:
            return self.SHADOW
        rgb = self._hex_to_rgb(color)
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"
    
    def create_glow(self, color: str, size: int = 15) -> List[str]:
        """Create a beautiful glow effect."""
        rgb = self._hex_to_rgb(color)
        return [
            f"0 0 {size}px rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.3)",
            f"0 0 {size//2}px rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"
        ]
    
    def adjust_brightness(self, color: str, factor: float) -> str:
        """Adjust color brightness while maintaining its character."""
        rgb = self._hex_to_rgb(color)
        hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], min(1, hsv[2] * factor))
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_rgba(self, r: int, g: int, b: int, a: float) -> str:
        """Create RGBA color string."""
        return f"rgba({r}, {g}, {b}, {a})"

class LightTheme(Theme):
    def __init__(self):
        super().__init__()
        # Modern light theme colors
        self.background_color = "#ffffff"
        self.border_color = "#ffffff"
        self.outline_color = "#e0e0e0"
        self.primary_color = "#2196F3"
        self.secondary_color = "#FF4081"
        self.text_color = "#333333"
        self.grid_color = "#f5f5f5"

class DarkTheme(Theme):
    def __init__(self):
        super().__init__()
        # Modern dark theme colors
        self.background_color = "#2c2c2c"
        self.border_color = "#2c2c2c"
        self.outline_color = "#404040"
        self.primary_color = "#64B5F6"
        self.secondary_color = "#FF80AB"
        self.text_color = "#ffffff"
        self.grid_color = "#404040"
