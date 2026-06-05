# Gantt Chart

Timeline visualization for project planning and scheduling.

```python
from ChartForgeTK import GanttChart

tasks = [
    {"task": "Research", "start": 0, "duration": 5},
    {"task": "Design", "start": 5, "duration": 4},
    {"task": "Implementation", "start": 9, "duration": 8},
    {"task": "Testing", "start": 17, "duration": 3}
]

chart = GanttChart(parent, width=600, height=400)
chart.plot(tasks)
```

## Parameters

### `GanttChart.plot()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `list[dict]` | List of task dictionaries |

Each task dictionary requires:

| Key | Type | Description |
|-----|------|-------------|
| `task` | str | Task name/label |
| `start` | int/float | Start time on the timeline |
| `duration` | int/float | How long the task takes |

Bars are color-coded and positioned horizontally by start time,
with length proportional to duration.
