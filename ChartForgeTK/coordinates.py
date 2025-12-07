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

"""
Coordinate transformation module for ChartForgeTK.

Provides robust coordinate transformations with edge case handling
for zero ranges, floating-point precision issues, and extreme values.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import math
import logging
from typing import Tuple, Optional

logger = logging.getLogger('ChartForgeTK')


class CoordinateTransformer:
    """
    Handles coordinate transformations with edge case safety.
    
    This class provides robust methods for converting between data coordinates
    and pixel coordinates, handling edge cases like:
    - Zero range (x_max == x_min or y_max == y_min)
    - Floating-point precision issues
    - Very small and very large values
    - Negative values and axis positioning
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    
    # Epsilon for floating-point comparisons
    EPSILON = 1e-10
    
    # Default range to use when data range is zero
    DEFAULT_RANGE = 1.0
    
    # Target number of ticks for axis
    TARGET_TICKS_MIN = 5
    TARGET_TICKS_MAX = 15
    
    def __init__(self, width: int, height: int, padding: int):
        """
        Initialize the CoordinateTransformer.
        
        Args:
            width: Total chart width in pixels
            height: Total chart height in pixels
            padding: Padding around the chart area in pixels
        """
        self.width = width
        self.height = height
        self.padding = padding
        
        # Calculate drawable area
        self.drawable_width = max(1, width - 2 * padding)
        self.drawable_height = max(1, height - 2 * padding)
        
        # Store current ranges
        self.x_min = 0.0
        self.x_max = 1.0
        self.y_min = 0.0
        self.y_max = 1.0
    
    def calculate_safe_range(
        self,
        data_min: float,
        data_max: float,
        padding_factor: float = 0.1
    ) -> Tuple[float, float]:
        """
        Calculate a safe range with padding, handling zero-range edge cases.
        
        Args:
            data_min: Minimum data value
            data_max: Maximum data value
            padding_factor: Factor to add as padding (0.1 = 10%)
            
        Returns:
            Tuple[float, float]: (safe_min, safe_max) with guaranteed non-zero range
            
        Requirements: 5.1
        """
        # Handle NaN or infinity
        if math.isnan(data_min) or math.isinf(data_min):
            data_min = 0.0
            logger.warning("Invalid data_min value, using 0.0")
        if math.isnan(data_max) or math.isinf(data_max):
            data_max = 1.0
            logger.warning("Invalid data_max value, using 1.0")
        
        # Ensure min <= max
        if data_min > data_max:
            data_min, data_max = data_max, data_min
        
        data_range = data_max - data_min
        
        # Handle zero range (all values identical)
        if abs(data_range) < self.EPSILON:
            # Use a default range centered on the value
            if abs(data_min) < self.EPSILON:
                # Value is zero, use default range
                return (-self.DEFAULT_RANGE / 2, self.DEFAULT_RANGE / 2)
            else:
                # Use a range proportional to the value
                magnitude = abs(data_min)
                half_range = magnitude * 0.5 if magnitude > 0 else self.DEFAULT_RANGE / 2
                return (data_min - half_range, data_max + half_range)
        
        # Add padding
        padding_amount = data_range * padding_factor
        safe_min = data_min - padding_amount
        safe_max = data_max + padding_amount
        
        return (safe_min, safe_max)
    
    def calculate_ranges(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        x_padding_factor: float = 0.1,
        y_padding_factor: float = 0.1
    ) -> Tuple[float, float, float, float]:
        """
        Calculate safe ranges for both axes with padding.
        
        Args:
            x_min: Minimum x data value
            x_max: Maximum x data value
            y_min: Minimum y data value
            y_max: Maximum y data value
            x_padding_factor: Padding factor for x-axis
            y_padding_factor: Padding factor for y-axis
            
        Returns:
            Tuple[float, float, float, float]: (x_min, x_max, y_min, y_max)
            
        Requirements: 5.1
        """
        safe_x_min, safe_x_max = self.calculate_safe_range(x_min, x_max, x_padding_factor)
        safe_y_min, safe_y_max = self.calculate_safe_range(y_min, y_max, y_padding_factor)
        
        # Store for later use
        self.x_min = safe_x_min
        self.x_max = safe_x_max
        self.y_min = safe_y_min
        self.y_max = safe_y_max
        
        return (safe_x_min, safe_x_max, safe_y_min, safe_y_max)
    
    def data_to_pixel_x(self, x: float, x_min: Optional[float] = None, x_max: Optional[float] = None) -> float:
        """
        Convert data x-coordinate to pixel coordinate.
        
        Args:
            x: Data x-coordinate
            x_min: Minimum x range (uses stored value if None)
            x_max: Maximum x range (uses stored value if None)
            
        Returns:
            float: Pixel x-coordinate
            
        Requirements: 5.1, 5.2
        """
        if x_min is None:
            x_min = self.x_min
        if x_max is None:
            x_max = self.x_max
        
        # Handle zero range
        x_range = x_max - x_min
        if abs(x_range) < self.EPSILON:
            # Return center of drawable area
            return self.padding + self.drawable_width / 2
        
        # Handle NaN or infinity in input
        if math.isnan(x) or math.isinf(x):
            logger.warning(f"Invalid x value: {x}, returning center")
            return self.padding + self.drawable_width / 2
        
        # Calculate normalized position (0 to 1)
        normalized = (x - x_min) / x_range
        
        # Clamp to prevent drawing outside bounds (with small margin)
        normalized = max(-0.1, min(1.1, normalized))
        
        # Convert to pixel coordinate
        pixel_x = self.padding + normalized * self.drawable_width
        
        return pixel_x
    
    def data_to_pixel_y(self, y: float, y_min: Optional[float] = None, y_max: Optional[float] = None) -> float:
        """
        Convert data y-coordinate to pixel coordinate.
        
        Note: Y-axis is inverted (0 at top in pixel coordinates)
        
        Args:
            y: Data y-coordinate
            y_min: Minimum y range (uses stored value if None)
            y_max: Maximum y range (uses stored value if None)
            
        Returns:
            float: Pixel y-coordinate
            
        Requirements: 5.1, 5.2
        """
        if y_min is None:
            y_min = self.y_min
        if y_max is None:
            y_max = self.y_max
        
        # Handle zero range
        y_range = y_max - y_min
        if abs(y_range) < self.EPSILON:
            # Return center of drawable area
            return self.padding + self.drawable_height / 2
        
        # Handle NaN or infinity in input
        if math.isnan(y) or math.isinf(y):
            logger.warning(f"Invalid y value: {y}, returning center")
            return self.padding + self.drawable_height / 2
        
        # Calculate normalized position (0 to 1)
        normalized = (y - y_min) / y_range
        
        # Clamp to prevent drawing outside bounds (with small margin)
        normalized = max(-0.1, min(1.1, normalized))
        
        # Convert to pixel coordinate (inverted for screen coordinates)
        pixel_y = self.height - self.padding - normalized * self.drawable_height
        
        return pixel_y
    
    def pixel_to_data_x(self, pixel_x: float, x_min: Optional[float] = None, x_max: Optional[float] = None) -> float:
        """
        Convert pixel x-coordinate to data coordinate.
        
        Args:
            pixel_x: Pixel x-coordinate
            x_min: Minimum x range (uses stored value if None)
            x_max: Maximum x range (uses stored value if None)
            
        Returns:
            float: Data x-coordinate
            
        Requirements: 5.2
        """
        if x_min is None:
            x_min = self.x_min
        if x_max is None:
            x_max = self.x_max
        
        # Handle zero drawable width
        if self.drawable_width < self.EPSILON:
            return (x_min + x_max) / 2
        
        # Calculate normalized position
        normalized = (pixel_x - self.padding) / self.drawable_width
        
        # Convert to data coordinate
        x_range = x_max - x_min
        data_x = x_min + normalized * x_range
        
        return data_x
    
    def pixel_to_data_y(self, pixel_y: float, y_min: Optional[float] = None, y_max: Optional[float] = None) -> float:
        """
        Convert pixel y-coordinate to data coordinate.
        
        Args:
            pixel_y: Pixel y-coordinate
            y_min: Minimum y range (uses stored value if None)
            y_max: Maximum y range (uses stored value if None)
            
        Returns:
            float: Data y-coordinate
            
        Requirements: 5.2
        """
        if y_min is None:
            y_min = self.y_min
        if y_max is None:
            y_max = self.y_max
        
        # Handle zero drawable height
        if self.drawable_height < self.EPSILON:
            return (y_min + y_max) / 2
        
        # Calculate normalized position (inverted)
        normalized = (self.height - self.padding - pixel_y) / self.drawable_height
        
        # Convert to data coordinate
        y_range = y_max - y_min
        data_y = y_min + normalized * y_range
        
        return data_y
    
    def calculate_tick_interval(self, data_range: float, target_ticks: int = 10) -> float:
        """
        Calculate appropriate tick interval for axis.
        
        Produces reasonable intervals that result in 5-15 ticks for any data range.
        
        Args:
            data_range: The range of data (max - min)
            target_ticks: Target number of ticks (default 10)
            
        Returns:
            float: Tick interval that produces reasonable number of ticks
            
        Requirements: 5.3
        """
        # Handle zero or negative range
        if data_range <= 0:
            return 1.0
        
        # Handle very small ranges
        if data_range < self.EPSILON:
            return self.EPSILON
        
        # Calculate rough interval
        rough_interval = data_range / target_ticks
        
        # Find the magnitude (power of 10)
        if rough_interval > 0:
            magnitude = math.pow(10, math.floor(math.log10(rough_interval)))
        else:
            magnitude = 1.0
        
        # Normalize to get a value between 1 and 10
        normalized = rough_interval / magnitude
        
        # Choose a "nice" interval
        if normalized <= 1.0:
            nice_interval = 1.0
        elif normalized <= 2.0:
            nice_interval = 2.0
        elif normalized <= 2.5:
            nice_interval = 2.5
        elif normalized <= 5.0:
            nice_interval = 5.0
        else:
            nice_interval = 10.0
        
        interval = nice_interval * magnitude
        
        # Verify we get reasonable number of ticks
        num_ticks = data_range / interval
        
        # Adjust if too few or too many ticks
        if num_ticks < self.TARGET_TICKS_MIN:
            # Too few ticks, use smaller interval
            interval = interval / 2
        elif num_ticks > self.TARGET_TICKS_MAX:
            # Too many ticks, use larger interval
            interval = interval * 2
        
        return interval
    
    def get_axis_zero_position(self, y_min: float, y_max: float) -> float:
        """
        Get the pixel y-coordinate for the x-axis (at y=0 or bottom).
        
        If the data range includes zero, the x-axis is positioned at y=0.
        Otherwise, it's positioned at the bottom of the chart.
        
        Args:
            y_min: Minimum y value
            y_max: Maximum y value
            
        Returns:
            float: Pixel y-coordinate for x-axis
            
        Requirements: 5.4
        """
        # Check if zero is within the range
        if y_min <= 0 <= y_max:
            # Position axis at y=0
            return self.data_to_pixel_y(0, y_min, y_max)
        else:
            # Position axis at bottom (y_min)
            return self.data_to_pixel_y(y_min, y_min, y_max)
    
    def update_dimensions(self, width: int, height: int, padding: Optional[int] = None) -> None:
        """
        Update the transformer dimensions.
        
        Args:
            width: New chart width
            height: New chart height
            padding: New padding (optional, keeps current if None)
        """
        self.width = width
        self.height = height
        if padding is not None:
            self.padding = padding
        
        self.drawable_width = max(1, width - 2 * self.padding)
        self.drawable_height = max(1, height - 2 * self.padding)
    
    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"CoordinateTransformer("
            f"width={self.width}, height={self.height}, padding={self.padding}, "
            f"x_range=[{self.x_min:.2f}, {self.x_max:.2f}], "
            f"y_range=[{self.y_min:.2f}, {self.y_max:.2f}])"
        )
