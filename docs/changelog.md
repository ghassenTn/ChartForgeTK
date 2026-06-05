# Changelog

## v2.0.0 (Latest)

### Stability Improvements
- Comprehensive input validation with type checking
- Clear, descriptive error messages
- Automatic handling of edge cases (empty data, NaN, infinity)
- Single data point rendering
- Identical value handling with meaningful axis ranges
- Zero-range data protection against division errors
- All-zero pie chart detection

### Resource Management
- Proper cleanup of tooltips and animation callbacks
- Memory leak prevention for long-running applications
- Safe animation cancellation on chart updates

### Pandas Integration
- DataFrame support for `BarChart`, `LineChart`, `PieChart`, `ScatterPlot`, `Histogram`
- Series support for `PieChart` and `Histogram`
- Column-based API using `value_column`, `label_column`, `y_columns`, `x_column`, `y_column`

### New Features
- `ResourceManager` for lifecycle management
- `DataValidator` for input validation
- `CoordinateTransformer` with edge case handling
- `TooltipManager` for centralized tooltip handling

## v1.0.0

Initial release with 12 chart types:

- BarChart, LineChart, PieChart, ScatterPlot, BubbleChart
- BoxPlot, Histogram, CandlestickChart, TableauChart
- GanttChart, NetworkGraph, HeatMap

### Features
- 8 color themes
- 8 color palettes
- Chart animations
- Tooltip support
- Click interaction (pie charts)
- `display_mode` ('frame' / 'window')
