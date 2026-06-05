# Contributing

Contributions are welcome! Here's how to get started:

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ghassenTn/ChartForgeTK.git
cd ChartForgeTK

# Install in editable mode
pip install -e .
```

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests.test_validation
python -m unittest tests.test_coordinates
```

## Running Demos

```bash
# Chart showcase
python showcase.py

# Enterprise dashboard
python test_charts/main.py
```

## Building for Distribution

```bash
pip install build
python -m build
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code Conventions

- All charts inherit from `Chart` (tk.Frame) in `core.py`
- Input validation uses `DataValidator` from `validation.py`
- Resource management uses `ResourceManager` from `resources.py`
- Coordinate math uses `CoordinateTransformer` from `coordinates.py`
- `.plot()` methods accept both lists and pandas DataFrames/Series
- No external dependencies — use only Python stdlib + tkinter
