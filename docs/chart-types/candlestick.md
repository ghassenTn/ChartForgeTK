# Candlestick Chart

OHLC (Open, High, Low, Close) financial data visualization for stock analysis.

```python
from ChartForgeTK import CandlestickChart

# Format: (index, open, high, low, close)
data = [
    (1, 100, 105, 98, 103),
    (2, 103, 108, 101, 106),
    (3, 106, 110, 104, 108)
]
chart = CandlestickChart(parent, width=600, height=400)
chart.plot(data)
```

## Data Format

Each candlestick is a tuple of `(index, open, high, low, close)`:

| Position | Field | Description |
|----------|-------|-------------|
| 0 | `index` | X-axis position |
| 1 | `open` | Opening price |
| 2 | `high` | Highest price |
| 3 | `low` | Lowest price |
| 4 | `close` | Closing price |

## Visual Convention

- **Green/white** candlestick = close ≥ open (bullish)
- **Red/black** candlestick = close < open (bearish)
- The thin line (wick) shows the high-low range
- The thick body shows the open-close range
