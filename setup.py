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


from setuptools import setup, find_packages

setup(
    name="ChartForgeTK",
    version="2.0.0",
    packages=["ChartForgeTK"],  
    package_dir={"ChartForgeTK": "ChartForgeTK"}, 
    install_requires=[
        "typing; python_version<'3.5'", 
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
