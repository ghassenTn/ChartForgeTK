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
Validation module for ChartForgeTK.

Provides comprehensive input validation utilities for chart data,
ensuring type safety and proper error handling.
"""

import math
import re
import logging
from typing import List, Optional, Tuple, Any, Union

logger = logging.getLogger('ChartForgeTK')


class DataValidator:
    """Validates chart data inputs with comprehensive type and value checking."""

    # Constants for validation
    MIN_DIMENSION = 100
    MAX_DIMENSION = 10000
    MAX_REASONABLE_VALUE = 1e15
    MIN_REASONABLE_VALUE = -1e15

    @staticmethod
    def validate_numeric_list(
        data: Any,
        allow_empty: bool = False,
        allow_negative: bool = True,
        allow_nan: bool = False,
        allow_inf: bool = False,
        param_name: str = "data"
    ) -> List[float]:
        """
        Validate and sanitize a list of numeric values.

        Args:
            data: Input data to validate
            allow_empty: Whether empty lists are allowed
            allow_negative: Whether negative values are allowed
            allow_nan: Whether NaN values are allowed
            allow_inf: Whether infinity values are allowed
            param_name: Name of the parameter for error messages

        Returns:
            List[float]: Validated and sanitized list of floats

        Raises:
            TypeError: If data is not a list or contains non-numeric values
            ValueError: If data violates validation rules
        """
        # Check for None
        if data is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide a list of numeric values."
            )

        # Check if it's a list or tuple
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a list or tuple, "
                f"got {type(data).__name__}. Please provide a list of numeric values."
            )

        # Convert to list if tuple
        data = list(data)

        # Check for empty
        if not data and not allow_empty:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} cannot be empty. "
                f"Please provide at least one data point."
            )

        # Validate each element
        result = []
        for i, value in enumerate(data):
            # Type check
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"[ChartForgeTK] Error: {param_name}[{i}] must be a number, "
                    f"got {type(value).__name__}. All data points must be numeric."
                )

            # Convert to float
            value = float(value)

            # Check for NaN
            if math.isnan(value):
                if not allow_nan:
                    raise ValueError(
                        f"[ChartForgeTK] Error: {param_name}[{i}] is NaN. "
                        f"NaN values are not allowed. Please filter or replace NaN values."
                    )
                logger.warning(f"NaN value found at {param_name}[{i}], filtering out")
                continue

            # Check for infinity
            if math.isinf(value):
                if not allow_inf:
                    raise ValueError(
                        f"[ChartForgeTK] Error: {param_name}[{i}] is infinity. "
                        f"Infinite values are not allowed. Please use finite values."
                    )
                logger.warning(f"Infinite value found at {param_name}[{i}], filtering out")
                continue

            # Check for negative values
            if value < 0 and not allow_negative:
                raise ValueError(
                    f"[ChartForgeTK] Error: {param_name}[{i}] is negative ({value}). "
                    f"Negative values are not allowed for this chart type."
                )

            # Check for extreme values (handle gracefully)
            if value > DataValidator.MAX_REASONABLE_VALUE:
                logger.warning(
                    f"Extremely large value at {param_name}[{i}]: {value}. "
                    f"This may cause rendering issues."
                )
            elif value < DataValidator.MIN_REASONABLE_VALUE:
                logger.warning(
                    f"Extremely small value at {param_name}[{i}]: {value}. "
                    f"This may cause rendering issues."
                )

            result.append(value)

        # Final empty check after filtering
        if not result and not allow_empty:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} is empty after filtering invalid values. "
                f"Please provide valid numeric data."
            )

        return result


    @staticmethod
    def validate_tuple_list(
        data: Any,
        expected_length: int,
        allow_empty: bool = False,
        param_name: str = "data"
    ) -> List[Tuple[float, ...]]:
        """
        Validate a list of tuples with expected length.

        Args:
            data: Input data to validate
            expected_length: Expected length of each tuple
            allow_empty: Whether empty lists are allowed
            param_name: Name of the parameter for error messages

        Returns:
            List[Tuple[float, ...]]: Validated list of tuples

        Raises:
            TypeError: If data is not a list or contains invalid tuples
            ValueError: If tuples have incorrect length or invalid values
        """
        # Check for None
        if data is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide a list of tuples."
            )

        # Check if it's a list or tuple
        if not isinstance(data, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a list, "
                f"got {type(data).__name__}. Please provide a list of tuples."
            )

        # Convert to list
        data = list(data)

        # Check for empty
        if not data and not allow_empty:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} cannot be empty. "
                f"Please provide at least one data point."
            )

        result = []
        for i, item in enumerate(data):
            # Check if item is a tuple or list
            if not isinstance(item, (tuple, list)):
                raise TypeError(
                    f"[ChartForgeTK] Error: {param_name}[{i}] must be a tuple or list, "
                    f"got {type(item).__name__}."
                )

            # Check length
            if len(item) != expected_length:
                raise ValueError(
                    f"[ChartForgeTK] Error: {param_name}[{i}] has length {len(item)}, "
                    f"expected {expected_length}. Each tuple must have exactly "
                    f"{expected_length} elements."
                )

            # Validate each element in the tuple
            validated_tuple = []
            for j, value in enumerate(item):
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        f"[ChartForgeTK] Error: {param_name}[{i}][{j}] must be a number, "
                        f"got {type(value).__name__}."
                    )

                value = float(value)

                if math.isnan(value):
                    raise ValueError(
                        f"[ChartForgeTK] Error: {param_name}[{i}][{j}] is NaN. "
                        f"NaN values are not allowed."
                    )

                if math.isinf(value):
                    raise ValueError(
                        f"[ChartForgeTK] Error: {param_name}[{i}][{j}] is infinity. "
                        f"Infinite values are not allowed."
                    )

                validated_tuple.append(value)

            result.append(tuple(validated_tuple))

        return result

    @staticmethod
    def validate_labels(
        labels: Any,
        data_length: int,
        param_name: str = "labels"
    ) -> List[str]:
        """
        Validate labels match data length or generate defaults.

        Args:
            labels: Input labels to validate (can be None for auto-generation)
            data_length: Expected number of labels
            param_name: Name of the parameter for error messages

        Returns:
            List[str]: Validated or generated labels

        Raises:
            TypeError: If labels is not a list of strings
            ValueError: If labels length doesn't match data length
        """
        # Generate default labels if None
        if labels is None:
            return [str(i) for i in range(data_length)]

        # Check if it's a list or tuple
        if not isinstance(labels, (list, tuple)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a list, "
                f"got {type(labels).__name__}. Please provide a list of strings."
            )

        # Convert to list
        labels = list(labels)

        # Check length match
        if len(labels) != data_length:
            raise ValueError(
                f"[ChartForgeTK] Error: Number of {param_name} ({len(labels)}) "
                f"must match number of data points ({data_length})."
            )

        # Validate and convert each label to string
        result = []
        for i, label in enumerate(labels):
            if label is None:
                result.append(str(i))
            else:
                result.append(str(label))

        return result

    @staticmethod
    def validate_dimensions(
        width: Any,
        height: Any,
        min_width: int = 100,
        min_height: int = 100
    ) -> Tuple[int, int]:
        """
        Validate chart dimensions.

        Args:
            width: Chart width to validate
            height: Chart height to validate
            min_width: Minimum allowed width
            min_height: Minimum allowed height

        Returns:
            Tuple[int, int]: Validated (width, height)

        Raises:
            TypeError: If dimensions are not integers
            ValueError: If dimensions are invalid
        """
        # Validate width
        if width is None:
            raise TypeError(
                "[ChartForgeTK] Error: width cannot be None. "
                "Please provide a positive integer."
            )

        if not isinstance(width, (int, float)):
            raise TypeError(
                f"[ChartForgeTK] Error: width must be a number, "
                f"got {type(width).__name__}."
            )

        width = int(width)

        if width < min_width:
            raise ValueError(
                f"[ChartForgeTK] Error: width ({width}) must be at least {min_width}. "
                f"Please provide a larger width value."
            )

        if width > DataValidator.MAX_DIMENSION:
            raise ValueError(
                f"[ChartForgeTK] Error: width ({width}) exceeds maximum allowed "
                f"({DataValidator.MAX_DIMENSION}). Please use a smaller width."
            )

        # Validate height
        if height is None:
            raise TypeError(
                "[ChartForgeTK] Error: height cannot be None. "
                "Please provide a positive integer."
            )

        if not isinstance(height, (int, float)):
            raise TypeError(
                f"[ChartForgeTK] Error: height must be a number, "
                f"got {type(height).__name__}."
            )

        height = int(height)

        if height < min_height:
            raise ValueError(
                f"[ChartForgeTK] Error: height ({height}) must be at least {min_height}. "
                f"Please provide a larger height value."
            )

        if height > DataValidator.MAX_DIMENSION:
            raise ValueError(
                f"[ChartForgeTK] Error: height ({height}) exceeds maximum allowed "
                f"({DataValidator.MAX_DIMENSION}). Please use a smaller height."
            )

        return (width, height)


    # Default fallback color for when color parsing fails
    DEFAULT_FALLBACK_COLOR = "#2563EB"  # Modern blue

    @staticmethod
    def validate_color(color: Any, param_name: str = "color") -> str:
        """
        Validate and normalize color strings.

        Supports:
        - Hex colors: #RGB, #RRGGBB
        - Named colors: 'red', 'blue', etc.

        Args:
            color: Color string to validate
            param_name: Name of the parameter for error messages

        Returns:
            str: Validated color string

        Raises:
            TypeError: If color is not a string
            ValueError: If color format is invalid
        """
        if color is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide a valid color string."
            )

        if not isinstance(color, str):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a string, "
                f"got {type(color).__name__}."
            )

        color = color.strip()

        if not color:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} cannot be empty. "
                f"Please provide a valid color string."
            )

        # Hex color validation
        if color.startswith('#'):
            hex_part = color[1:]

            # Support #RGB shorthand
            if len(hex_part) == 3:
                if not all(c in '0123456789abcdefABCDEF' for c in hex_part):
                    raise ValueError(
                        f"[ChartForgeTK] Error: Invalid hex color '{color}'. "
                        f"Hex colors must contain only 0-9 and A-F characters."
                    )
                # Expand to #RRGGBB
                color = '#' + ''.join(c * 2 for c in hex_part)
                return color.lower()

            # Standard #RRGGBB
            if len(hex_part) == 6:
                if not all(c in '0123456789abcdefABCDEF' for c in hex_part):
                    raise ValueError(
                        f"[ChartForgeTK] Error: Invalid hex color '{color}'. "
                        f"Hex colors must contain only 0-9 and A-F characters."
                    )
                return color.lower()

            raise ValueError(
                f"[ChartForgeTK] Error: Invalid hex color '{color}'. "
                f"Hex colors must be in #RGB or #RRGGBB format."
            )

        # Named color validation (basic set of common colors)
        valid_named_colors = {
            'white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'gray', 'grey', 'orange', 'pink', 'purple', 'brown', 'navy', 'teal',
            'olive', 'maroon', 'aqua', 'lime', 'silver', 'fuchsia',
            'lightgray', 'lightgrey', 'darkgray', 'darkgrey',
            'lightblue', 'darkblue', 'lightgreen', 'darkgreen',
            'lightred', 'darkred', 'lightyellow', 'darkyellow',
        }

        if color.lower() in valid_named_colors:
            return color.lower()

        # If not a recognized named color, log warning but allow it
        # (Tkinter may support additional colors)
        logger.warning(
            f"Color '{color}' is not a recognized named color. "
            f"Tkinter may or may not support it."
        )
        return color

    @staticmethod
    def validate_color_with_fallback(
        color: Any,
        default_color: str = None,
        param_name: str = "color"
    ) -> str:
        """
        Validate a color string with fallback to default on failure.

        This method provides graceful degradation when color parsing fails,
        returning a default color instead of raising an exception.

        Args:
            color: Color string to validate
            default_color: Fallback color if validation fails (defaults to DEFAULT_FALLBACK_COLOR)
            param_name: Name of the parameter for logging

        Returns:
            str: Validated color string or default color on failure

        Requirements: 4.3
        """
        if default_color is None:
            default_color = DataValidator.DEFAULT_FALLBACK_COLOR

        try:
            return DataValidator.validate_color(color, param_name)
        except (TypeError, ValueError) as e:
            logger.warning(
                f"Color parsing failed for {param_name}: {e}. "
                f"Falling back to default color '{default_color}'."
            )
            return default_color

    @staticmethod
    def parse_hex_color(color: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse a hex color string into RGB components.

        Args:
            color: Hex color string (#RGB or #RRGGBB)

        Returns:
            Tuple of (r, g, b) values (0-255) or None if parsing fails
        """
        if not isinstance(color, str) or not color.startswith('#'):
            return None

        hex_part = color[1:]

        try:
            if len(hex_part) == 3:
                # #RGB format
                r = int(hex_part[0] * 2, 16)
                g = int(hex_part[1] * 2, 16)
                b = int(hex_part[2] * 2, 16)
                return (r, g, b)
            elif len(hex_part) == 6:
                # #RRGGBB format
                r = int(hex_part[0:2], 16)
                g = int(hex_part[2:4], 16)
                b = int(hex_part[4:6], 16)
                return (r, g, b)
        except ValueError:
            pass

        return None

    @staticmethod
    def validate_theme(theme: Any) -> str:
        """
        Validate theme parameter.

        Args:
            theme: Theme to validate

        Returns:
            str: Validated theme string

        Raises:
            TypeError: If theme is not a string
            ValueError: If theme is not 'light' or 'dark'
        """
        if theme is None:
            raise TypeError(
                "[ChartForgeTK] Error: theme cannot be None. "
                "Please provide 'light' or 'dark'."
            )

        if not isinstance(theme, str):
            raise TypeError(
                f"[ChartForgeTK] Error: theme must be a string, "
                f"got {type(theme).__name__}."
            )

        theme = theme.strip().lower()

        if theme not in ('light', 'dark'):
            raise ValueError(
                f"[ChartForgeTK] Error: theme must be 'light' or 'dark', "
                f"got '{theme}'."
            )

        return theme

    @staticmethod
    def validate_display_mode(display_mode: Any) -> str:
        """
        Validate display_mode parameter.

        Args:
            display_mode: Display mode to validate

        Returns:
            str: Validated display mode string

        Raises:
            TypeError: If display_mode is not a string
            ValueError: If display_mode is not 'frame' or 'window'
        """
        if display_mode is None:
            raise TypeError(
                "[ChartForgeTK] Error: display_mode cannot be None. "
                "Please provide 'frame' or 'window'."
            )

        if not isinstance(display_mode, str):
            raise TypeError(
                f"[ChartForgeTK] Error: display_mode must be a string, "
                f"got {type(display_mode).__name__}."
            )

        display_mode = display_mode.strip().lower()

        if display_mode not in ('frame', 'window'):
            raise ValueError(
                f"[ChartForgeTK] Error: display_mode must be 'frame' or 'window', "
                f"got '{display_mode}'."
            )

        return display_mode

    @staticmethod
    def clamp_rgb_value(value: Union[int, float]) -> int:
        """
        Clamp an RGB value to valid range (0-255).

        Args:
            value: RGB component value

        Returns:
            int: Clamped value between 0 and 255

        Requirements: 8.2
        """
        if not isinstance(value, (int, float)):
            return 0
        return max(0, min(255, int(value)))

    @staticmethod
    def rgb_to_hex(r: Union[int, float], g: Union[int, float], b: Union[int, float]) -> str:
        """
        Convert RGB values to hex color string with clamping.

        Automatically clamps RGB values to valid range (0-255).

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)

        Returns:
            str: Hex color string (#RRGGBB)

        Requirements: 8.2
        """
        r = DataValidator.clamp_rgb_value(r)
        g = DataValidator.clamp_rgb_value(g)
        b = DataValidator.clamp_rgb_value(b)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def validate_rgb_tuple(
        rgb: Any,
        param_name: str = "rgb"
    ) -> Tuple[int, int, int]:
        """
        Validate and clamp an RGB tuple to valid ranges.

        Args:
            rgb: Tuple or list of (r, g, b) values
            param_name: Name of the parameter for error messages

        Returns:
            Tuple[int, int, int]: Validated and clamped (r, g, b) values

        Raises:
            TypeError: If rgb is not a tuple/list or contains non-numeric values
            ValueError: If rgb doesn't have exactly 3 components

        Requirements: 8.2
        """
        if rgb is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide an (r, g, b) tuple."
            )

        if not isinstance(rgb, (tuple, list)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a tuple or list, "
                f"got {type(rgb).__name__}."
            )

        if len(rgb) != 3:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} must have exactly 3 components (r, g, b), "
                f"got {len(rgb)} components."
            )

        result = []
        for i, component in enumerate(rgb):
            if not isinstance(component, (int, float)):
                raise TypeError(
                    f"[ChartForgeTK] Error: {param_name}[{i}] must be a number, "
                    f"got {type(component).__name__}."
                )
            # Clamp to valid range
            clamped = DataValidator.clamp_rgb_value(component)
            if clamped != int(component):
                logger.warning(
                    f"RGB component {param_name}[{i}] value {component} "
                    f"clamped to {clamped} (valid range: 0-255)."
                )
            result.append(clamped)

        return tuple(result)

    @staticmethod
    def validate_rgb_with_fallback(
        rgb: Any,
        default_rgb: Tuple[int, int, int] = (37, 99, 235),  # Default blue
        param_name: str = "rgb"
    ) -> Tuple[int, int, int]:
        """
        Validate an RGB tuple with fallback to default on failure.

        This method provides graceful degradation when RGB validation fails,
        returning a default RGB tuple instead of raising an exception.

        Args:
            rgb: Tuple or list of (r, g, b) values
            default_rgb: Fallback RGB tuple if validation fails
            param_name: Name of the parameter for logging

        Returns:
            Tuple[int, int, int]: Validated RGB tuple or default on failure

        Requirements: 4.3, 8.2
        """
        try:
            return DataValidator.validate_rgb_tuple(rgb, param_name)
        except (TypeError, ValueError) as e:
            logger.warning(
                f"RGB validation failed for {param_name}: {e}. "
                f"Falling back to default RGB {default_rgb}."
            )
            return default_rgb

    @staticmethod
    def validate_padding(
        padding: Any,
        width: int,
        height: int,
        min_padding: int = 0,
        param_name: str = "padding"
    ) -> int:
        """
        Validate padding value ensuring it doesn't cause negative chart dimensions.

        Args:
            padding: Padding value to validate
            width: Chart width
            height: Chart height
            min_padding: Minimum allowed padding value
            param_name: Name of the parameter for error messages

        Returns:
            int: Validated padding value

        Raises:
            TypeError: If padding is not a number
            ValueError: If padding would cause negative dimensions

        Requirements: 8.4
        """
        if padding is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide a non-negative integer."
            )

        if not isinstance(padding, (int, float)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a number, "
                f"got {type(padding).__name__}."
            )

        padding = int(padding)

        if padding < min_padding:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} ({padding}) must be at least {min_padding}."
            )

        # Calculate maximum allowed padding (must leave at least 20 pixels for content)
        min_content_size = 20
        max_padding_for_width = (width - min_content_size) // 2
        max_padding_for_height = (height - min_content_size) // 2
        max_padding = min(max_padding_for_width, max_padding_for_height)

        if padding > max_padding:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} ({padding}) is too large for chart dimensions "
                f"({width}x{height}). Maximum allowed padding is {max_padding} to ensure "
                f"at least {min_content_size} pixels of content area."
            )

        return padding

    @staticmethod
    def validate_spacing(
        spacing: Any,
        available_space: int,
        num_items: int,
        min_spacing: int = 0,
        param_name: str = "spacing"
    ) -> int:
        """
        Validate spacing value ensuring items fit within available space.

        Args:
            spacing: Spacing value to validate
            available_space: Total available space for items and spacing
            num_items: Number of items that need spacing
            min_spacing: Minimum allowed spacing value
            param_name: Name of the parameter for error messages

        Returns:
            int: Validated spacing value

        Raises:
            TypeError: If spacing is not a number
            ValueError: If spacing would cause items to not fit

        Requirements: 8.4
        """
        if spacing is None:
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} cannot be None. "
                f"Please provide a non-negative integer."
            )

        if not isinstance(spacing, (int, float)):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a number, "
                f"got {type(spacing).__name__}."
            )

        spacing = int(spacing)

        if spacing < min_spacing:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} ({spacing}) must be at least {min_spacing}."
            )

        if num_items > 0:
            # Calculate total spacing needed
            total_spacing = spacing * (num_items - 1) if num_items > 1 else 0
            min_item_size = 1  # Minimum 1 pixel per item
            min_space_for_items = num_items * min_item_size

            if total_spacing + min_space_for_items > available_space:
                max_spacing = (available_space - min_space_for_items) // max(1, num_items - 1)
                raise ValueError(
                    f"[ChartForgeTK] Error: {param_name} ({spacing}) is too large. "
                    f"With {num_items} items in {available_space} pixels, "
                    f"maximum spacing is {max(0, max_spacing)}."
                )

        return spacing

    @staticmethod
    def validate_layout_params(
        width: int,
        height: int,
        padding: int,
        min_content_width: int = 20,
        min_content_height: int = 20
    ) -> Tuple[int, int, int, int]:
        """
        Validate layout parameters and calculate usable content area.

        This method ensures that padding doesn't cause negative content dimensions
        and returns the validated content area dimensions.

        Args:
            width: Total chart width
            height: Total chart height
            padding: Padding around the content area
            min_content_width: Minimum required content width
            min_content_height: Minimum required content height

        Returns:
            Tuple of (content_x, content_y, content_width, content_height)

        Raises:
            ValueError: If layout parameters would cause invalid dimensions

        Requirements: 8.3, 8.4
        """
        # Calculate content area
        content_width = width - 2 * padding
        content_height = height - 2 * padding

        if content_width < min_content_width:
            raise ValueError(
                f"[ChartForgeTK] Error: Content width ({content_width}) is less than "
                f"minimum required ({min_content_width}). Reduce padding or increase chart width."
            )

        if content_height < min_content_height:
            raise ValueError(
                f"[ChartForgeTK] Error: Content height ({content_height}) is less than "
                f"minimum required ({min_content_height}). Reduce padding or increase chart height."
            )

        return (padding, padding, content_width, content_height)

    @staticmethod
    def validate_dimensions_with_padding(
        width: Any,
        height: Any,
        padding: Any,
        min_width: int = 100,
        min_height: int = 100,
        min_content_size: int = 20
    ) -> Tuple[int, int, int]:
        """
        Validate chart dimensions and padding together.

        This method validates both dimensions and padding, ensuring they work
        together to provide a valid content area.

        Args:
            width: Chart width to validate
            height: Chart height to validate
            padding: Padding value to validate
            min_width: Minimum allowed width
            min_height: Minimum allowed height
            min_content_size: Minimum content area size after padding

        Returns:
            Tuple[int, int, int]: Validated (width, height, padding)

        Raises:
            TypeError: If parameters have incorrect types
            ValueError: If parameters would cause invalid layout

        Requirements: 8.3, 8.4
        """
        # First validate dimensions
        width, height = DataValidator.validate_dimensions(width, height, min_width, min_height)

        # Then validate padding against dimensions
        padding = DataValidator.validate_padding(padding, width, height, 0, "padding")

        return (width, height, padding)

    # ==================== Pandas Support Methods ====================
    # These methods provide pandas DataFrame/Series detection and conversion
    # without requiring pandas as a mandatory dependency.

    @staticmethod
    def is_pandas_dataframe(obj: Any) -> bool:
        """
        Check if object is a pandas DataFrame without requiring pandas import.

        Uses string-based type checking to avoid import dependency.

        Args:
            obj: Object to check

        Returns:
            bool: True if object is a pandas DataFrame, False otherwise

        Requirements: 7.2, 5.1, 5.3
        """
        obj_type = type(obj)
        module = getattr(obj_type, '__module__', '')
        name = getattr(obj_type, '__name__', '')
        return module.startswith('pandas') and name == 'DataFrame'

    @staticmethod
    def is_pandas_series(obj: Any) -> bool:
        """
        Check if object is a pandas Series without requiring pandas import.

        Uses string-based type checking to avoid import dependency.

        Args:
            obj: Object to check

        Returns:
            bool: True if object is a pandas Series, False otherwise

        Requirements: 7.2, 5.1, 5.3
        """
        obj_type = type(obj)
        module = getattr(obj_type, '__module__', '')
        name = getattr(obj_type, '__name__', '')
        return module.startswith('pandas') and name == 'Series'

    @staticmethod
    def is_pandas_object(obj: Any) -> bool:
        """
        Check if object is any pandas data structure (DataFrame or Series).

        Args:
            obj: Object to check

        Returns:
            bool: True if object is a pandas DataFrame or Series, False otherwise

        Requirements: 7.2, 5.1, 5.3
        """
        return DataValidator.is_pandas_dataframe(obj) or DataValidator.is_pandas_series(obj)

    @staticmethod
    def _get_pandas():
        """
        Lazily import pandas if available.

        Returns:
            pandas module

        Raises:
            ImportError: When pandas is needed but not installed (with install instructions)

        Requirements: 5.2
        """
        try:
            import pandas as pd
            return pd
        except ImportError:
            raise ImportError(
                "[ChartForgeTK] Error: pandas is required for DataFrame support. "
                "Install with: pip install pandas"
            )


    @staticmethod
    def convert_series_to_list(
        series: Any,
        param_name: str = "data"
    ) -> Tuple[List[float], List[str]]:
        """
        Convert a pandas Series to a list with index as labels.

        Extracts values as list and index as labels. Handles NaN and infinity
        filtering with warnings, and converts datetime index to strings.

        Args:
            series: pandas Series to convert
            param_name: Name of the parameter for error messages

        Returns:
            Tuple of (values_list, labels_list)

        Raises:
            TypeError: If series is not a pandas Series or contains non-numeric data
            ValueError: If series is empty or empty after filtering

        Requirements: 1.2, 3.1, 3.2, 3.3, 7.1
        """
        if not DataValidator.is_pandas_series(series):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a pandas Series, "
                f"got {type(series).__name__}."
            )

        pd = DataValidator._get_pandas()

        # Check for empty series
        if len(series) == 0:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} Series is empty. "
                f"Please provide data with at least one row."
            )

        # Check if series contains numeric data
        if not pd.api.types.is_numeric_dtype(series):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} Series contains non-numeric data. "
                f"Expected numeric values for plotting."
            )

        values = []
        labels = []
        nan_count = 0
        inf_count = 0

        for idx, value in series.items():
            # Convert value to float
            float_val = float(value)

            # Check for NaN
            if math.isnan(float_val):
                nan_count += 1
                continue

            # Check for infinity
            if math.isinf(float_val):
                inf_count += 1
                continue

            values.append(float_val)

            # Convert index to string (handles datetime index)
            labels.append(str(idx))

        # Log warnings for filtered values
        if nan_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {nan_count} NaN value(s) filtered from {param_name}."
            )

        if inf_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {inf_count} infinity value(s) filtered from {param_name}."
            )

        # Check if all values were filtered
        if not values:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} is empty after filtering NaN/infinity values. "
                f"Please provide valid numeric data."
            )

        return (values, labels)


    @staticmethod
    def convert_dataframe_to_list(
        df: Any,
        value_column: Optional[str] = None,
        label_column: Optional[str] = None,
        param_name: str = "data"
    ) -> Tuple[List[float], Optional[List[str]]]:
        """
        Convert a pandas DataFrame to lists suitable for chart plotting.

        Accepts optional value_column and label_column parameters. Uses sensible
        defaults (first numeric column for values, index for labels) when not specified.
        Validates column existence and data types. Filters NaN and infinity values.

        Args:
            df: pandas DataFrame to convert
            value_column: Optional column name for values (defaults to first numeric column)
            label_column: Optional column name for labels (defaults to index)
            param_name: Name of the parameter for error messages

        Returns:
            Tuple of (values_list, labels_list or None)

        Raises:
            TypeError: If df is not a DataFrame or column contains non-numeric data
            ValueError: If DataFrame is empty, column doesn't exist, or empty after filtering

        Requirements: 1.1, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 7.1
        """
        if not DataValidator.is_pandas_dataframe(df):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a pandas DataFrame, "
                f"got {type(df).__name__}."
            )

        pd = DataValidator._get_pandas()

        # Check for empty DataFrame
        if len(df) == 0:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} DataFrame is empty. "
                f"Please provide data with at least one row."
            )

        available_columns = list(df.columns)

        # Determine value column
        if value_column is not None:
            if value_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{value_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            val_col = value_column
        else:
            # Find first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if not numeric_cols:
                raise TypeError(
                    f"[ChartForgeTK] Error: {param_name} DataFrame contains no numeric columns. "
                    f"Expected at least one numeric column for plotting. "
                    f"Available columns: {available_columns}"
                )
            val_col = numeric_cols[0]

        # Validate that value column is numeric
        if not pd.api.types.is_numeric_dtype(df[val_col]):
            raise TypeError(
                f"[ChartForgeTK] Error: Column '{val_col}' contains non-numeric data. "
                f"Expected numeric values for plotting."
            )

        # Determine labels
        labels = None
        if label_column is not None:
            if label_column not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{label_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            label_source = df[label_column]
            use_label_column = True
        else:
            label_source = df.index
            use_label_column = False

        values = []
        label_list = []
        nan_count = 0
        inf_count = 0

        for i, (idx, row) in enumerate(df.iterrows()):
            float_val = float(row[val_col])

            # Check for NaN
            if math.isnan(float_val):
                nan_count += 1
                continue

            # Check for infinity
            if math.isinf(float_val):
                inf_count += 1
                continue

            values.append(float_val)

            # Get label (convert to string, handles datetime)
            if use_label_column:
                label_list.append(str(row[label_column]))
            else:
                label_list.append(str(idx))

        # Log warnings for filtered values
        if nan_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {nan_count} NaN value(s) filtered from {param_name}."
            )

        if inf_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {inf_count} infinity value(s) filtered from {param_name}."
            )

        # Check if all values were filtered
        if not values:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} is empty after filtering NaN/infinity values. "
                f"Please provide valid numeric data."
            )

        labels = label_list if label_list else None
        return (values, labels)


    @staticmethod
    def extract_dataframe_columns(
        df: Any,
        columns: List[str],
        param_name: str = "data"
    ) -> Tuple[List[List[float]], List[str]]:
        """
        Extract multiple columns from a DataFrame for multi-series charts.

        Validates all specified columns exist and are numeric. Returns one list
        per column, each containing the exact values from that column in order.

        Args:
            df: pandas DataFrame to extract from
            columns: List of column names to extract
            param_name: Name of the parameter for error messages

        Returns:
            Tuple of (list of value lists (one per column), labels list from index)

        Raises:
            TypeError: If df is not a DataFrame or columns contain non-numeric data
            ValueError: If DataFrame is empty or columns don't exist

        Requirements: 4.2
        """
        if not DataValidator.is_pandas_dataframe(df):
            raise TypeError(
                f"[ChartForgeTK] Error: {param_name} must be a pandas DataFrame, "
                f"got {type(df).__name__}."
            )

        pd = DataValidator._get_pandas()

        # Check for empty DataFrame
        if len(df) == 0:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} DataFrame is empty. "
                f"Please provide data with at least one row."
            )

        if not columns:
            raise ValueError(
                f"[ChartForgeTK] Error: columns list cannot be empty. "
                f"Please specify at least one column to extract."
            )

        available_columns = list(df.columns)

        # Validate all columns exist and are numeric
        for col in columns:
            if col not in df.columns:
                raise ValueError(
                    f"[ChartForgeTK] Error: Column '{col}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(
                    f"[ChartForgeTK] Error: Column '{col}' contains non-numeric data. "
                    f"Expected numeric values for plotting."
                )

        # Extract values from each column
        result_columns = []
        labels = []
        nan_count = 0
        inf_count = 0

        # Build a mask for valid rows (no NaN or inf in any specified column)
        valid_mask = [True] * len(df)
        for i, (idx, row) in enumerate(df.iterrows()):
            for col in columns:
                float_val = float(row[col])
                if math.isnan(float_val) or math.isinf(float_val):
                    if math.isnan(float_val):
                        nan_count += 1
                    else:
                        inf_count += 1
                    valid_mask[i] = False
                    break

        # Extract valid rows
        for col in columns:
            col_values = []
            for i, (idx, row) in enumerate(df.iterrows()):
                if valid_mask[i]:
                    col_values.append(float(row[col]))
            result_columns.append(col_values)

        # Extract labels from valid rows
        for i, (idx, row) in enumerate(df.iterrows()):
            if valid_mask[i]:
                labels.append(str(idx))

        # Log warnings for filtered values
        if nan_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {nan_count} NaN value(s) filtered from {param_name}."
            )

        if inf_count > 0:
            logger.warning(
                f"[ChartForgeTK] Warning: {inf_count} infinity value(s) filtered from {param_name}."
            )

        # Check if all values were filtered
        if not result_columns[0]:
            raise ValueError(
                f"[ChartForgeTK] Error: {param_name} is empty after filtering NaN/infinity values. "
                f"Please provide valid numeric data."
            )

        return (result_columns, labels)
