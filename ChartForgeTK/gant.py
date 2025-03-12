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


from typing import List, Tuple, Optional
import tkinter as tk
from tkinter import ttk
from .core import Chart, ChartStyle

class GanttChart(Chart):
    def __init__(self, parent=None, width: int = 400, height: int = 400, 
                 display_mode='frame', theme='light', max_bar_height=30, min_bar_height=15):
        super().__init__(parent, width=width, height=height, display_mode=display_mode, theme=theme)
        self.data = []
        self.dependencies = []
        self.milestones = []
        self.elements = []
        self.colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', 
                      '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
        self.parent = parent
        # Dynamic sizing parameters
        self.max_bar_height = max_bar_height
        self.min_bar_height = min_bar_height
        self.bar_spacing = 5
        self.current_scale = 1.0
        self.v_offset = 0
        
        # Scrollable canvas setup
        self.container = ttk.Frame(self.parent)
        self.canvas = tk.Canvas(self.container, bg=self.style.BACKGROUND)
        self.scroll_y = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        self.container.pack(fill='both', expand=True)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Event bindings
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._on_pan)
        self.canvas.bind("<Motion>", self._on_hover)

    def plot(self, data: List[Tuple[str, float, float]], 
            dependencies: Optional[List[Tuple[int, int]]] = None,
            milestones: Optional[List[Tuple[str, float]]] = None):
        """Plot the Gantt chart with tasks, dependencies, and milestones."""
        self.data = data
        self.dependencies = dependencies or []
        self.milestones = milestones or []
        self.max_days = max((start + duration for _, start, duration in data), default=0)
        
        # Calculate dynamic bar height
        self._calculate_dynamic_layout()
        self._redraw()

    def _calculate_dynamic_layout(self):
        """Calculate bar height and spacing based on available canvas space."""
        visible_area = self.canvas.winfo_height() - 2 * self.padding
        required_height = len(self.data) * (self.max_bar_height + self.bar_spacing)
        
        if required_height > visible_area:
            self.bar_height = max(
                self.min_bar_height,
                (visible_area - len(self.data) * self.bar_spacing) // len(self.data)
            )
        else:
            self.bar_height = self.max_bar_height
            
        self.total_height = len(self.data) * (self.bar_height + self.bar_spacing) + 2 * self.padding

    def _redraw(self):
        """Redraw the entire Gantt chart."""
        self.canvas.delete('all')
        self._draw_grid()
        self._draw_gantt()
        self._draw_dependencies()
        self._draw_milestones()
        self._update_scrollregion()

    def _update_scrollregion(self):
        """Update the scrollable region of the canvas."""
        total_width = self.padding * 2 + self.max_days * self._get_time_scale()
        self.canvas.configure(scrollregion=(0, 0, total_width, self.total_height))

    def _get_time_scale(self):
        """Calculate the scaling factor for the timeline."""
        return (self.canvas.winfo_width() - 2 * self.padding) / max(1, self.max_days)

    def _draw_grid(self):
        """Draw the background grid."""
        time_scale = self._get_time_scale()
        y_base = self.padding
        
        # Vertical grid lines
        for day in range(0, int(self.max_days) + 1):
            x = self.padding + day * time_scale
            dash = (2, 2) if day % 5 != 0 else None
            self.canvas.create_line(x, y_base, x, self.total_height, 
                                   fill=self.style.SECONDARY, dash=dash)
            
        # Horizontal lines
        for i in range(len(self.data) + 1):
            y = y_base + i * (self.bar_height + self.bar_spacing)
            self.canvas.create_line(self.padding, y, 
                                  self.padding + self.max_days * time_scale, y,
                                  fill=self.style.SECONDARY, dash=(2, 2))
    def _draw_dependencies(self):
        """Draw dependency arrows between tasks."""
        for src, dest in self.dependencies:
            if 0 <= src < len(self.data) and 0 <= dest < len(self.data):
                self._draw_dependency_arrow(src, dest)
    def _draw_milestones(self):
        """Draw milestone markers."""
        for name, day in self.milestones:
            x = self.padding + (day - self.x_offset) * ((self.width - 2*self.padding) / self.max_days)
            y = self.padding + 30
            self.canvas.create_polygon(
                x, y-10, x+10, y, x, y+10, x-10, y,
                fill='#e74c3c', outline=self.style.BACKGROUND
            )
            self.canvas.create_text(
                x, y+15, text=name,
                font=('Arial', 8, 'bold'), fill='#e74c3c',
                anchor='n'
            )
    def _draw_gantt(self):
        """Draw the Gantt bars and labels."""
        time_scale = self._get_time_scale()
        y_base = self.padding
        
        for idx, (task, start, duration) in enumerate(self.data):
            y = y_base + idx * (self.bar_height + self.bar_spacing)
            x_start = self.padding + start * time_scale
            x_end = x_start + duration * time_scale
            
            # Draw bar
            color = self.colors[idx % len(self.colors)]
            bar = self.canvas.create_rectangle(
                x_start, y, x_end, y + self.bar_height,
                fill=color, outline=self.style.BACKGROUND,
                tags=('task', f'task_{idx}')
            )
            
            # Draw label if space permits
            if x_end - x_start > 50:
                self.canvas.create_text(
                    x_start + 5, y + self.bar_height / 2,
                    text=task, anchor='w',
                    font=('Arial', max(8, int(self.bar_height / 2))),
                    fill=self.style.BACKGROUND
                )

        # Left-side task labels
        self._draw_side_labels()

    def _draw_side_labels(self):
        """Draw task labels on the left side."""
        y_base = self.padding
        for idx, (task, _, _) in enumerate(self.data):
            y = y_base + idx * (self.bar_height + self.bar_spacing)
            self.canvas.create_text(
                self.padding - 10, y + self.bar_height / 2,
                text=task, anchor='e',
                font=('Arial', max(8, int(self.bar_height / 2))),
                fill=self.style.TEXT
            )

    def _on_canvas_configure(self, event):
        """Handle canvas resize events."""
        self._calculate_dynamic_layout()
        self._redraw()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        # Vertical scrolling
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        
        # Horizontal scrolling with Shift+Mousewheel
        if event.state & 0x0001:
            self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def _start_pan(self, event):
        """Start panning the canvas."""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan(self, event):
        """Handle canvas panning."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_hover(self, event):
        """Handle hover events for task highlighting and tooltips."""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        task_id = self.canvas.find_overlapping(x, y, x, y)
        
        if task_id and 'task' in self.canvas.gettags(task_id[0]):
            idx = int(self.canvas.gettags(task_id[0])[1].split('_')[1])
            self._highlight_task(idx)
            self._show_tooltip(x, y, idx)
        else:
            self._clear_highlights()
            self._hide_tooltip()

    def _highlight_task(self, idx):
        """Highlight a task bar."""
        self.canvas.itemconfig(f'task_{idx}', outline=self.style.ACCENT, width=2)

    def _clear_highlights(self):
        """Clear all task highlights."""
        for item in self.canvas.find_withtag('task'):
            self.canvas.itemconfig(item, outline=self.style.BACKGROUND, width=1)

    def _show_tooltip(self, x, y, idx):
        """Show a tooltip for a task."""
        task, start, duration = self.data[idx]
        end = start + duration
        tooltip_text = f"{task}\nStart: {start}\nEnd: {end}\nDuration: {duration}"
        
        self.canvas.delete('tooltip')
        self.canvas.create_rectangle(
            x + 15, y - 15, x + 200, y + 40,
            fill=self.style.BACKGROUND, outline=self.style.ACCENT,
            tags='tooltip'
        )
        self.canvas.create_text(
            x + 20, y - 10, text=tooltip_text,
            anchor='nw', fill=self.style.TEXT,
            font=self.style.TOOLTIP_FONT, tags='tooltip'
        )

    def _hide_tooltip(self):
        """Hide the tooltip."""
        self.canvas.delete('tooltip')