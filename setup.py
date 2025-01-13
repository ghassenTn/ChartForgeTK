from setuptools import setup, find_packages

setup(
    name="ChartForgeTK",
    version="1.0.2",
    packages=["ChartForgeTK"],  # Updated package name
    package_dir={"ChartForgeTK": "ChartForgeTK"},  # Updated directory mapping
    install_requires=[
        "typing; python_version<'3.5'",  # For older Python versions
    ],
    author="Ghassen",
    author_email="ghassen.xr@gmail.com",
    description="A modern, smooth, and dynamic charting library for Python using pure Tkinter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ghassenTn/ChartForgeTK",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Matplotlib",
        "Operating System :: OS Independent",
    ],
    keywords="chart, graph, visualization, tkinter, gui, plot, matplotlib alternative",
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/ghassenTn/ChartForgeTK/issues",
        "Source": "https://github.com/ghassenTn/ChartForgeTK",
        "Documentation": "https://github.com/ghassenTn/ChartForgeTK#readme",
    },
)
