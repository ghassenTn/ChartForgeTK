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
Resource management module for ChartForgeTK.

Provides lifecycle management for chart resources including tooltips,
animation callbacks, and event bindings to prevent memory leaks and
ensure proper cleanup.
"""

import logging
import tkinter as tk
from typing import List, Tuple, Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .core import Chart

logger = logging.getLogger('ChartForgeTK')


class ResourceManager:
    """
    Manages chart resources and cleanup for proper lifecycle management.
    
    This class tracks and manages:
    - Tooltip windows (Toplevel widgets)
    - Animation callback IDs (after() calls)
    - Event bindings on the canvas
    
    It ensures all resources are properly cleaned up when a chart is
    destroyed or redrawn, preventing memory leaks and orphaned resources.
    
    Requirements: 3.1, 3.2, 3.3, 3.5, 3.6
    """

    def __init__(self, chart: 'Chart'):
        """
        Initialize the ResourceManager.
        
        Args:
            chart: The Chart instance this manager is associated with
        """
        self._chart = chart
        self._tooltips: List[tk.Toplevel] = []
        self._animation_ids: List[str] = []
        self._event_bindings: List[Tuple[tk.Widget, str, str]] = []
        self._is_cleaned_up = False
    
    @property
    def chart(self) -> 'Chart':
        """Get the associated chart instance."""
        return self._chart
    
    @property
    def tooltip_count(self) -> int:
        """Get the number of registered tooltips."""
        return len(self._tooltips)
    
    @property
    def animation_count(self) -> int:
        """Get the number of registered animation callbacks."""
        return len(self._animation_ids)
    
    @property
    def binding_count(self) -> int:
        """Get the number of registered event bindings."""
        return len(self._event_bindings)
    
    @property
    def is_cleaned_up(self) -> bool:
        """Check if cleanup has been performed."""
        return self._is_cleaned_up
    
    def register_tooltip(self, tooltip: tk.Toplevel) -> None:
        """
        Register a tooltip window for cleanup.
        
        Args:
            tooltip: The Toplevel widget representing the tooltip
            
        Requirements: 3.1
        """
        if tooltip is None:
            logger.warning("Attempted to register None tooltip")
            return
        
        if not isinstance(tooltip, tk.Toplevel):
            logger.warning(f"Attempted to register non-Toplevel as tooltip: {type(tooltip)}")
            return
        
        if tooltip not in self._tooltips:
            self._tooltips.append(tooltip)
            logger.debug(f"Registered tooltip, total: {len(self._tooltips)}")
    
    def unregister_tooltip(self, tooltip: tk.Toplevel) -> bool:
        """
        Unregister a tooltip without destroying it.
        
        Args:
            tooltip: The tooltip to unregister
            
        Returns:
            bool: True if the tooltip was found and unregistered
        """
        if tooltip in self._tooltips:
            self._tooltips.remove(tooltip)
            return True
        return False
    
    def register_animation(self, after_id: str) -> None:
        """
        Register an animation callback ID for cancellation.
        
        Args:
            after_id: The ID returned by canvas.after() or widget.after()
            
        Requirements: 3.2, 3.6
        """
        if after_id is None:
            logger.warning("Attempted to register None animation ID")
            return
        
        if after_id not in self._animation_ids:
            self._animation_ids.append(after_id)
            logger.debug(f"Registered animation {after_id}, total: {len(self._animation_ids)}")
    
    def unregister_animation(self, after_id: str) -> bool:
        """
        Unregister an animation callback without cancelling it.
        
        Args:
            after_id: The animation ID to unregister
            
        Returns:
            bool: True if the animation was found and unregistered
        """
        if after_id in self._animation_ids:
            self._animation_ids.remove(after_id)
            return True
        return False
    
    def register_binding(
        self, 
        widget: tk.Widget, 
        sequence: str, 
        func_id: str
    ) -> None:
        """
        Register an event binding for cleanup.
        
        Args:
            widget: The widget the binding is on
            sequence: The event sequence (e.g., '<Button-1>')
            func_id: The function ID returned by bind()
            
        Requirements: 3.5
        """
        if widget is None or sequence is None or func_id is None:
            logger.warning("Attempted to register binding with None values")
            return
        
        binding = (widget, sequence, func_id)
        if binding not in self._event_bindings:
            self._event_bindings.append(binding)
            logger.debug(f"Registered binding {sequence}, total: {len(self._event_bindings)}")
    
    def unregister_binding(
        self, 
        widget: tk.Widget, 
        sequence: str, 
        func_id: str
    ) -> bool:
        """
        Unregister an event binding without unbinding it.
        
        Args:
            widget: The widget the binding is on
            sequence: The event sequence
            func_id: The function ID
            
        Returns:
            bool: True if the binding was found and unregistered
        """
        binding = (widget, sequence, func_id)
        if binding in self._event_bindings:
            self._event_bindings.remove(binding)
            return True
        return False

    
    def cancel_animations(self) -> int:
        """
        Cancel all pending animation callbacks.
        
        This method safely cancels all registered animation callbacks
        using the chart's canvas.after_cancel() method.
        
        Returns:
            int: Number of animations cancelled
            
        Requirements: 3.2, 3.6
        """
        cancelled_count = 0
        
        for after_id in self._animation_ids[:]:  # Copy list to allow modification
            try:
                # Try to cancel using canvas if available
                if hasattr(self._chart, 'canvas') and self._chart.canvas:
                    try:
                        self._chart.canvas.after_cancel(after_id)
                        cancelled_count += 1
                        logger.debug(f"Cancelled animation {after_id}")
                    except tk.TclError:
                        # Animation may have already completed
                        logger.debug(f"Animation {after_id} already completed or invalid")
                # Fallback to chart widget itself
                elif hasattr(self._chart, 'after_cancel'):
                    try:
                        self._chart.after_cancel(after_id)
                        cancelled_count += 1
                    except tk.TclError:
                        logger.debug(f"Animation {after_id} already completed or invalid")
            except Exception as e:
                logger.warning(f"Error cancelling animation {after_id}: {e}")
        
        self._animation_ids.clear()
        logger.debug(f"Cancelled {cancelled_count} animations")
        return cancelled_count
    
    def cleanup_tooltips(self) -> int:
        """
        Destroy all registered tooltip windows.
        
        Returns:
            int: Number of tooltips destroyed
            
        Requirements: 3.1
        """
        destroyed_count = 0
        
        for tooltip in self._tooltips[:]:  # Copy list to allow modification
            try:
                if tooltip.winfo_exists():
                    tooltip.destroy()
                    destroyed_count += 1
                    logger.debug("Destroyed tooltip")
            except tk.TclError:
                # Widget may already be destroyed
                logger.debug("Tooltip already destroyed")
            except Exception as e:
                logger.warning(f"Error destroying tooltip: {e}")
        
        self._tooltips.clear()
        logger.debug(f"Destroyed {destroyed_count} tooltips")
        return destroyed_count
    
    def cleanup_bindings(self) -> int:
        """
        Unbind all registered event bindings.
        
        Returns:
            int: Number of bindings removed
            
        Requirements: 3.5
        """
        unbound_count = 0
        
        for widget, sequence, func_id in self._event_bindings[:]:  # Copy list
            try:
                if widget.winfo_exists():
                    widget.unbind(sequence, func_id)
                    unbound_count += 1
                    logger.debug(f"Unbound {sequence}")
            except tk.TclError:
                # Widget may already be destroyed
                logger.debug(f"Widget for binding {sequence} already destroyed")
            except Exception as e:
                logger.warning(f"Error unbinding {sequence}: {e}")
        
        self._event_bindings.clear()
        logger.debug(f"Unbound {unbound_count} bindings")
        return unbound_count
    
    def cleanup(self) -> Tuple[int, int, int]:
        """
        Clean up all registered resources.
        
        This method performs a complete cleanup of all resources:
        1. Cancels all pending animations
        2. Destroys all tooltip windows
        3. Unbinds all event bindings
        
        Returns:
            Tuple[int, int, int]: (animations_cancelled, tooltips_destroyed, bindings_removed)
            
        Requirements: 3.1, 3.2, 3.3, 3.5, 3.6
        """
        if self._is_cleaned_up:
            logger.debug("Cleanup already performed, skipping")
            return (0, 0, 0)
        
        logger.debug("Starting resource cleanup")
        
        # Cancel animations first to prevent callbacks during cleanup
        animations_cancelled = self.cancel_animations()
        
        # Destroy tooltips
        tooltips_destroyed = self.cleanup_tooltips()
        
        # Unbind events
        bindings_removed = self.cleanup_bindings()
        
        self._is_cleaned_up = True
        
        logger.info(
            f"Resource cleanup complete: {animations_cancelled} animations, "
            f"{tooltips_destroyed} tooltips, {bindings_removed} bindings"
        )
        
        return (animations_cancelled, tooltips_destroyed, bindings_removed)
    
    def reset(self) -> None:
        """
        Reset the manager state without cleaning up resources.
        
        This is useful when resources have been cleaned up externally
        and the manager needs to be reused.
        """
        self._tooltips.clear()
        self._animation_ids.clear()
        self._event_bindings.clear()
        self._is_cleaned_up = False
        logger.debug("ResourceManager reset")
    
    def prepare_for_redraw(self) -> int:
        """
        Prepare for a chart redraw by cancelling animations.
        
        This method should be called before redrawing a chart to ensure
        no pending animations interfere with the new rendering.
        
        Returns:
            int: Number of animations cancelled
            
        Requirements: 3.2, 3.3
        """
        return self.cancel_animations()
    
    def __repr__(self) -> str:
        """Return a string representation of the ResourceManager."""
        return (
            f"ResourceManager("
            f"tooltips={len(self._tooltips)}, "
            f"animations={len(self._animation_ids)}, "
            f"bindings={len(self._event_bindings)}, "
            f"cleaned_up={self._is_cleaned_up})"
        )


def create_safe_animation_callback(
    chart: 'Chart',
    callback: Callable[[], None],
    on_error: Optional[Callable[[Exception], None]] = None
) -> Callable[[], None]:
    """
    Create a safe animation callback wrapper with error recovery.
    
    This function wraps an animation callback to:
    1. Check if the widget still exists before executing
    2. Catch and log any errors that occur during execution
    3. Optionally call an error handler for custom recovery
    
    Args:
        chart: The Chart instance the animation is for
        callback: The original callback function
        on_error: Optional error handler function that receives the exception
        
    Returns:
        Callable: A wrapped callback function with error recovery
        
    Requirements: 4.1, 6.3
    
    Example:
        def my_animation_frame():
            # Animation logic here
            pass
        
        safe_callback = create_safe_animation_callback(chart, my_animation_frame)
        after_id = chart.canvas.after(16, safe_callback)
    """
    def safe_callback():
        # Check if widget still exists (Requirements: 6.3)
        try:
            if not hasattr(chart, 'canvas') or chart.canvas is None:
                logger.debug("Canvas is None, skipping animation callback")
                return
            if not chart.canvas.winfo_exists():
                logger.debug("Canvas no longer exists, skipping animation callback")
                return
        except tk.TclError:
            logger.debug("TclError checking widget existence, skipping callback")
            return
        except Exception as e:
            logger.debug(f"Error checking widget existence: {e}")
            return
        
        # Execute the callback with error recovery (Requirements: 4.1)
        try:
            callback()
        except tk.TclError as e:
            # Widget may have been destroyed during callback execution
            logger.debug(f"TclError during animation callback: {e}")
            if on_error:
                try:
                    on_error(e)
                except Exception:
                    pass  # Don't let error handler crash
        except Exception as e:
            # Log the error and stop the animation without crashing (Requirements: 4.1)
            logger.error(f"Error in animation callback: {e}", exc_info=True)
            if on_error:
                try:
                    on_error(e)
                except Exception:
                    pass  # Don't let error handler crash
    
    return safe_callback


def schedule_safe_animation(
    chart: 'Chart',
    callback: Callable[[], None],
    delay_ms: int = 16,
    on_error: Optional[Callable[[Exception], None]] = None
) -> Optional[str]:
    """
    Schedule an animation callback with automatic error recovery.
    
    This is a convenience function that combines create_safe_animation_callback
    with scheduling and resource registration.
    
    Args:
        chart: The Chart instance to schedule the animation for
        callback: The callback function to execute
        delay_ms: Delay in milliseconds (default 16ms for ~60 FPS)
        on_error: Optional error handler function
        
    Returns:
        str: The after ID if scheduled successfully, None otherwise
        
    Requirements: 3.2, 3.6, 4.1, 6.3
    """
    # Check if widget exists before scheduling
    try:
        if not hasattr(chart, 'canvas') or chart.canvas is None:
            return None
        if not chart.canvas.winfo_exists():
            return None
    except tk.TclError:
        return None
    except Exception:
        return None
    
    # Create safe callback wrapper
    safe_callback = create_safe_animation_callback(chart, callback, on_error)
    
    # Schedule the callback
    try:
        after_id = chart.canvas.after(delay_ms, safe_callback)
        
        # Register with resource manager if available
        if hasattr(chart, 'resource_manager') and chart.resource_manager:
            chart.resource_manager.register_animation(after_id)
        
        return after_id
    except tk.TclError as e:
        logger.debug(f"Failed to schedule animation: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error scheduling animation: {e}")
        return None
