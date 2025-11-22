"""
StarCraft II Copilot - Core Module

This package contains the core functionality for the StarCraft II Copilot,
a real-time assistant for Co-op and Versus modes.
"""

__version__ = "0.1.0"
__author__ = "ProbiusOfficial"

from .ScreenCapture import ScreenCapture
from .OCR_Analysis import OCRAnalysis
from .ReminderEngine import ReminderEngine

__all__ = ['ScreenCapture', 'OCRAnalysis', 'ReminderEngine']
