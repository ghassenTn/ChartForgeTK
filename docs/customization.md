# Customization

## Themes

ChartForgeTK includes 8 built-in color themes:

```python
chart = BarChart(parent, theme='light')    # Default
chart = BarChart(parent, theme='dark')
chart = BarChart(parent, theme='corporate')
chart = BarChart(parent, theme='pastel')
chart = BarChart(parent, theme='monochrome')
chart = BarChart(parent, theme='ocean')
chart = BarChart(parent, theme='sunset')
chart = BarChart(parent, theme='forest')
```

## Palettes

8 color palettes for chart series:

```python
chart = BarChart(parent, palette='modern')      # Default
chart = BarChart(parent, palette='corporate')
chart = BarChart(parent, palette='pastel')
chart = BarChart(parent, palette='vibrant')
chart = BarChart(parent, palette='monochrome')
chart = BarChart(parent, palette='ocean')
chart = BarChart(parent, palette='sunset')
chart = BarChart(parent, palette='forest')
```

## Changing Theme and Palette at Runtime

```python
chart.style.set_theme('dark')
chart.style.set_palette('vibrant')
chart.redraw()
```

## Chart Titles and Labels

```python
chart.title = "Sales by Quarter"
chart.x_label = "Quarter"
chart.y_label = "Revenue ($)"
chart.redraw()
```

## Line Chart Options

```python
chart = LineChart(
    parent,
    show_point_labels=True,           # Show value labels on data points
    use_container_width_height=True   # Auto-resize with parent container
)
```

## Multi-Series Styling

```python
chart.plot([
    {
        'data': [10, 15, 13, 18],
        'color': '#FF5733',           # Custom hex color
        'shape': 'circle',            # circle, square, triangle, diamond
        'label': 'Series A'           # Legend label
    }
])
```

## Reference Lines

```python
# Horizontal reference line
chart.add_bar('horizontal', value=15, color='#FF0000', label='Target')

# Vertical reference line
chart.add_bar('vertical', value=3, color='#0000FF', dash=(4, 2))
```
