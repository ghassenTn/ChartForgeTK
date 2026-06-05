# ChartForgeTK — Agent Guide

## Project
Pure-Tkinter charting library, zero external dependencies. Python 3.8+.
Single package `ChartForgeTK/` at repo root. `__init__.py` is the public API entrypoint.

## Key commands
- **Run all tests**: `python -m unittest discover tests` (uses `unittest`, no test runner config)
- **Run single test file**: `python -m unittest tests.test_validation`
- **Run showcase demo**: `python showcase.py`
- **Run enterprise dashboard demo**: `python test_charts/main.py`
- **Build for PyPI**: `python -m build`
- **Local install (editable)**: `pip install -e .`

## Architecture
- All charts inherit from `Chart` (tk.Frame) in `core.py:597`
- `DataValidator` in `validation.py` — centralized input validation
- `ResourceManager` in `resources.py` — lifecycle/cleanup for tooltips, animations
- `CoordinateTransformer` in `coordinates.py` — data↔pixel math
- `ChartStyle` in `core.py:270` — theme/palette system with 8 themes, 8 palettes
- Each chart type is its own file: `bar.py`, `line.py`, `pie.py`, `scatter.py`, `boxplot.py`, `bubble.py`, `heatmap.py`, `histograme.py`, `candlestik.py`, `network.py`, `tableau.py`, `gant.py`

## Chart types (all in `ChartForgeTK.*`)
BarChart, LineChart, PieChart, ScatterPlot, BubbleChart, BoxPlot, Histogram, CandlestickChart, TableauChart, GanttChart, NetworkGraph, HeatMap

## Testing quirks
- Only two test files exist: `tests/test_validation.py` and `tests/test_coordinates.py`
- **No CI pipeline runs tests** — only CI workflow (`publish.yml`) publishes to PyPI on GitHub release
- Tests use `unittest` — no pytest-specific config but pytest cache dir (`.pytest_cache`) exists

## Conventions & gotchas
- All `.plot()` methods accept both plain lists and pandas DataFrame/Series (optional dependency)
- Pandas is optional; charts gracefully handle its absence
- Some filenames have typos: `histograme.py`, `candlestik.py` — keep them as-is
- README license badge says MIT, but headers in source files and the `LICENSE` file are Apache 2.0
- There is no linter, formatter, or type checker configured
- The only dependency is `typing` (only needed for Python < 3.5; effectively none for 3.8+)
