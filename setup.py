#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="tokenzero",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tokenzero=tokenzero.cli:main",
        ],
    },
)
