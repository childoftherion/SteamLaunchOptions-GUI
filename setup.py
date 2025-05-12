#!/usr/bin/env python3
"""
Setup script for SteamLauncherGUI.
"""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open("steamlaunchergui/__init__.py", "r") as f:
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    version = version_match.group(1) if version_match else "0.1.0"

# Get long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="steamlaunchergui",
    version=version,
    description="A GUI tool for configuring Steam game launch options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TimeFlex1 and contributors",
    author_email="",
    url="https://github.com/TimeFlex1/SteamLaunchOptions-GUI",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "steamlaunchergui=steamlaunchergui.main:main",
        ],
    },
    install_requires=[
        "PyGObject",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.6",
) 