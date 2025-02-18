"""
Configuration module for the paper search tool.
Defines directory paths and other configuration settings.
"""

import os

# Get absolute path of the tools directory
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root directory (paperlists/)
PROJECT_ROOT = os.path.abspath(os.path.join(TOOLS_DIR, ".."))

# Data directory (paperlists/)
DATA_DIR = PROJECT_ROOT 