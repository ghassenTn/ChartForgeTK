# Installation

## Requirements

- Python 3.8+
- Tkinter (included with Python)
- Optional: pandas (for DataFrame/Series support)

## Install from PyPI

```bash
pip install ChartForgeTK
```

## Install from source

```bash
git clone https://github.com/ghassenTn/ChartForgeTK.git
cd ChartForgeTK
pip install -e .
```

## Verify installation

```python
from ChartForgeTK import BarChart
print("ChartForgeTK installed successfully!")
```

## Optional dependencies

pandas is fully optional. All charts work with plain Python lists.
When pandas is available, `.plot()` methods also accept DataFrames and Series.

```bash
pip install pandas
```
