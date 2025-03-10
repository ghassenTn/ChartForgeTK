import numpy as np
import math

class Easing:
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation: steady progress."""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in: starts slow, accelerates."""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out: starts fast, decelerates."""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out: smooth start and end."""
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in: stronger acceleration."""
        return t ** 3
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out: stronger deceleration."""
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out: smooth with strong curves."""
        return 4 * t ** 3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_sine(t: float) -> float:
        """Sine ease-in: smooth start using sine curve."""
        return 1 - math.cos((t * math.pi) / 2)
    
    @staticmethod
    def ease_out_sine(t: float) -> float:
        """Sine ease-out: smooth end using sine curve."""
        return math.sin((t * math.pi) / 2)
    
    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        """Sine ease-in-out: smooth start and end."""
        return -(math.cos(math.pi * t) - 1) / 2

class Animation:
    def __init__(
        self, 
        duration: float = 1.0, 
        easing=Easing.ease_in_out_quad, 
        loop: bool = False, 
        reverse: bool = False,
        on_start=None,
        on_end=None
    ):
        """
        Initialize animation parameters.

        Args:
            duration: Duration of the animation in seconds.
            easing: Easing function to use for interpolation.
            loop: If True, animation repeats indefinitely.
            reverse: If True, animation reverses after reaching the end.
            on_start: Optional callback when animation starts.
            on_end: Optional callback when animation ends.
        """
        self.duration = duration
        self.easing = easing
        self.loop = loop
        self.reverse = reverse
        self.on_start = on_start
        self.on_end = on_end
        self.keyframes = []  # List of (time, value) tuples
        self.has_started = False

    def add_keyframe(self, time: float, value):
        """
        Add a keyframe to the animation.

        Args:
            time: Time (0 to 1) at which the keyframe occurs.
            value: Value at the keyframe (e.g., float, list, tuple, or np.ndarray).
        """
        if not 0 <= time <= 1:
            raise ValueError("Keyframe time must be between 0 and 1")
        # Convert value to NumPy array if it isn’t already
        value = np.array(value) if not isinstance(value, np.ndarray) else value
        self.keyframes.append((time, value))
        self.keyframes.sort(key=lambda x: x[0])  # Sort by time

    def interpolate(self, progress: float) -> np.ndarray:
        """
        Interpolate between keyframes based on animation progress.

        Args:
            progress: Animation progress (typically 0 to 1).

        Returns:
            Interpolated value as a NumPy array.

        Raises:
            ValueError: If no keyframes are defined or values are incompatible.
        """
        if not self.keyframes:
            raise ValueError("No keyframes defined. Add keyframes using add_keyframe().")

        # Trigger callbacks
        if not self.has_started and progress > 0:
            if self.on_start:
                self.on_start()
            self.has_started = True
        if progress >= 1 and self.on_end:
            self.on_end()

        # Adjust progress for looping or reversing
        if self.loop and progress >= 1:
            progress = progress % 1.0
        elif self.reverse and progress > 1:
            progress = 2.0 - progress
        progress = max(0.0, min(1.0, progress))

        # Single keyframe case
        if len(self.keyframes) == 1:
            return self.keyframes[0][1]

        # Find the relevant keyframe segment
        for i in range(len(self.keyframes) - 1):
            start_time, start_value = self.keyframes[i]
            end_time, end_value = self.keyframes[i + 1]
            if start_time <= progress <= end_time:
                # Calculate segment progress and apply easing
                segment_progress = (progress - start_time) / (end_time - start_time)
                t = self.easing(segment_progress)
                if start_value.shape != end_value.shape:
                    raise ValueError("Keyframe values must have the same shape")
                return start_value + (end_value - start_value) * t

        # Before first or after last keyframe
        if progress <= self.keyframes[0][0]:
            return self.keyframes[0][1]
        return self.keyframes[-1][1]