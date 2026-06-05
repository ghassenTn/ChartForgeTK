# API Reference

## Core Classes

### Chart

Base class for all chart types. Inherits from `tk.Frame`.

```python
Chart(parent=None, width=400, height=400, display_mode='frame', theme='light', palette='modern')
```

**Methods:**

| Method | Description |
|--------|-------------|
| `plot(data, ...)` | Plot data (overridden by subclasses) |
| `redraw()` | Redraw the chart with current data |
| `clear()` | Clear the canvas and cancel animations |
| `destroy()` | Clean up all resources and destroy the chart |
| `show()` | Display chart in window mode |
| `to_window()` | Convert frame chart to separate window |
| `to_frame(parent)` | Convert window chart to embedded frame |
| `schedule_animation(callback, delay_ms)` | Schedule animation with lifecycle safety |
| `cancel_all_animations()` | Cancel all pending animations |
| `show_tooltip(x_root, y_root, text)` | Show tooltip at screen position |
| `hide_tooltip()` | Hide the current tooltip |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `style` | ChartStyle | Theme and palette configuration |
| `resource_manager` | ResourceManager | Lifecycle management |
| `tooltip_manager` | TooltipManager | Tooltip handling |
| `is_animating` | bool | Whether animation is in progress |

---

### ChartStyle

Theme and palette system for charts.

```python
ChartStyle(theme='light', palette='modern')
```

**Methods:**

| Method | Description |
|--------|-------------|
| `set_theme(theme)` | Apply a color theme |
| `set_palette(palette)` | Apply a color palette |
| `get_color(index)` | Get palette color by index |
| `adjust_brightness(color, factor)` | Lighten/darken a hex color |

**Themes:** `light`, `dark`, `corporate`, `pastel`, `monochrome`, `ocean`, `sunset`, `forest`
**Palettes:** `modern`, `corporate`, `pastel`, `vibrant`, `monochrome`, `ocean`, `sunset`, `forest`

---

### ChartRenderer

Static rendering utilities for canvas drawing.

```python
ChartRenderer.create_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs)
ChartRenderer.create_drop_shadow(canvas, x1, y1, x2, y2, ...)
ChartRenderer.create_bar_gradient(canvas, x1, y1, x2, y2, color, steps)
ChartRenderer.create_glow_effect(canvas, x1, y1, x2, y2, color, width, steps)
```

---

## Utility Classes

### DataValidator

Centralized input validation for chart data.

```python
DataValidator.validate_numeric_list(data, allow_empty=False, allow_negative=True)
DataValidator.validate_color(color)
DataValidator.validate_dimensions(width, height)
DataValidator.validate_padding(padding, width, height)
DataValidator.validate_spacing(spacing, available_space, num_items)
DataValidator.validate_labels(labels, expected_length)
DataValidator.validate_theme(theme)
DataValidator.validate_display_mode(mode)
```

---

### ResourceManager

Lifecycle management for chart resources (tooltips, animations, bindings).

```python
ResourceManager(chart)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `register_animation(after_id)` | Track an animation callback |
| `cancel_animations()` | Cancel all tracked animations |
| `register_tooltip(tooltip)` | Track a tooltip window |
| `unregister_tooltip(tooltip)` | Stop tracking a tooltip |
| `cleanup_tooltips()` | Destroy all tracked tooltips |
| `cleanup()` | Release all resources |
| `register_binding(binding_id)` | Track an event binding |
| `unregister_binding(binding_id)` | Stop tracking a binding |

---

### CoordinateTransformer

Data-to-pixel coordinate math with edge case handling.

```python
CoordinateTransformer(width, height, padding)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `calculate_ranges(x_min, x_max, y_min, y_max)` | Set data ranges |
| `calculate_safe_range(min_val, max_val, padding_factor)` | Expand zero/identical ranges |
| `data_to_pixel_x(x)` | Convert data x to pixel x |
| `data_to_pixel_y(y)` | Convert data y to pixel y |
| `calculate_tick_interval(range_val)` | Compute nice tick intervals |

---

### TooltipManager

Centralized tooltip creation, display, and cleanup.

```python
TooltipManager(chart)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `show(x_root, y_root, text)` | Show tooltip at position |
| `hide()` | Hide the tooltip |
| `update_text(text)` | Update tooltip text |
| `destroy()` | Destroy tooltip and clean up |
| `reset()` | Reset for retry after failure |
