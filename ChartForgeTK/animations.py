import numpy as np

class Easing:
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

class Animation:
    def __init__(self, duration: float = 1.0, easing=Easing.ease_in_out_quad):
        """
        Initialize animation parameters.
        
        Args:
            duration: Duration of the animation in seconds
            easing: Easing function to use for the animation
        """
        self.duration = duration
        self.easing = easing
        
    def interpolate(self, start_values: np.ndarray, end_values: np.ndarray, 
                   progress: float) -> np.ndarray:
        """
        Interpolate between start and end values based on animation progress.
        
        Args:
            start_values: Initial values
            end_values: Target values
            progress: Animation progress (0 to 1)
            
        Returns:
            Interpolated values
        """
        t = self.easing(progress)
        return start_values + (end_values - start_values) * t
