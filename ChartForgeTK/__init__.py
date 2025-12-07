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
ChartForgeTK - A powerful charting library built purely on Tkinter.

ChartForgeTK provides modern, interactive data visualization for desktop
applications with zero external dependencies. It supports a wide variety
of chart types including bar charts, line charts, pie charts, scatter plots,
and more.

Features:
    - Comprehensive input validation and type safety
    - Robust error handling and graceful degradation
    - Proper resource management and memory cleanup
    - Edge case handling for unusual data patterns
    - Interactive features with tooltips and animations

Example:
    >>> import tkinter as tk
    >>> from ChartForgeTK import BarChart
    >>> root = tk.Tk()
    >>> chart = BarChart(root, width=400, height=300)
    >>> chart.pack()
    >>> chart.plot([10, 20, 15, 25], ["Q1", "Q2", "Q3", "Q4"])
    >>> root.mainloop()
"""

# Core chart base class
from .core import Chart

# Chart types
from .network import NetworkGraph
from .bubble import BubbleChart
from .heatmap import HeatMap
from .pie import PieChart
from .line import LineChart
from .bar import BarChart
from .scatter import ScatterPlot
from .boxplot import BoxPlot
from .histograme import Histogram
from .candlestik import CandlestickChart
from .tableau import TableauChart
from .gant import GanttChart

# Stability and validation modules
from .validation import DataValidator
from .resources import ResourceManager, create_safe_animation_callback, schedule_safe_animation
from .coordinates import CoordinateTransformer

# from .area import AreaChart

__version__ = "2.0.0"
__author__ = "Ghassen Saidi"
__license__ = "Apache-2.0"

__all__ = [
    # Core
    'Chart',
    
    # Chart types
    'LineChart',
    'ScatterPlot',
    'BarChart',
    'PieChart',
    'NetworkGraph',
    'BubbleChart',
    'HeatMap',
    'BoxPlot',
    'Histogram',
    'CandlestickChart',
    'TableauChart',
    'GanttChart',
    
    # Validation and utilities
    'DataValidator',
    'ResourceManager',
    'CoordinateTransformer',
    'create_safe_animation_callback',
    'schedule_safe_animation',
]
