"""
ScreenCapture.py
Screen capture module for StarCraft II Copilot

This module handles real-time screen capture of the StarCraft II game window.
It provides functionality to capture specific regions of the screen for analysis.
"""

import mss
import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict
from loguru import logger


class ScreenCapture:
    """
    Handles screen capture operations for StarCraft II game monitoring.
    
    This class provides methods to capture the entire screen or specific regions,
    optimized for real-time game state analysis.
    """
    
    def __init__(self):
        """Initialize the screen capture engine."""
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
        logger.info(f"Screen capture initialized. Monitor: {self.monitor}")
        
        # Define common SC2 UI regions (relative coordinates, will be adjusted based on resolution)
        self.regions = {
            'resources': None,      # Resource bar (minerals, gas, supply)
            'minimap': None,        # Minimap area
            'command_card': None,   # Command card (unit abilities)
            'unit_info': None,      # Selected unit information
            'timer': None,          # Game timer
        }
        
    def capture_screen(self) -> np.ndarray:
        """
        Capture the entire screen.
        
        Returns:
            np.ndarray: Screen capture as a numpy array (RGB format)
        """
        try:
            screenshot = self.sct.grab(self.monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            return np.array(img)
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None
    
    def capture_region(self, region: Dict[str, int]) -> Optional[np.ndarray]:
        """
        Capture a specific region of the screen.
        
        Args:
            region: Dictionary with keys 'left', 'top', 'width', 'height'
            
        Returns:
            np.ndarray: Captured region as a numpy array, or None if capture fails
        """
        try:
            screenshot = self.sct.grab(region)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            return np.array(img)
        except Exception as e:
            logger.error(f"Failed to capture region {region}: {e}")
            return None
    
    def set_region(self, name: str, left: int, top: int, width: int, height: int):
        """
        Define a named region for repeated capture.
        
        Args:
            name: Region identifier (e.g., 'resources', 'minimap')
            left: Left coordinate
            top: Top coordinate
            width: Region width
            height: Region height
        """
        self.regions[name] = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        logger.debug(f"Region '{name}' set to: {self.regions[name]}")
    
    def capture_named_region(self, name: str) -> Optional[np.ndarray]:
        """
        Capture a predefined named region.
        
        Args:
            name: Name of the region to capture
            
        Returns:
            np.ndarray: Captured region, or None if region not defined or capture fails
        """
        if name not in self.regions or self.regions[name] is None:
            logger.warning(f"Region '{name}' not defined")
            return None
        
        return self.capture_region(self.regions[name])
    
    def auto_detect_sc2_window(self) -> bool:
        """
        Automatically detect the StarCraft II game window.
        
        This method attempts to find the SC2 window and adjust capture regions accordingly.
        
        Returns:
            bool: True if SC2 window detected, False otherwise
        """
        # Placeholder for window detection logic
        # In a full implementation, this would use platform-specific APIs
        # to find the StarCraft II window and calculate UI regions
        logger.info("Auto-detecting StarCraft II window...")
        
        # For now, assume full screen at 1920x1080 (most common SC2 resolution)
        # These values should be adjusted based on actual window detection
        self.set_region('resources', 10, 10, 300, 50)
        self.set_region('minimap', 10, 650, 300, 300)
        self.set_region('command_card', 700, 800, 500, 200)
        self.set_region('unit_info', 1400, 800, 500, 200)
        self.set_region('timer', 860, 10, 200, 40)
        
        logger.info("SC2 UI regions configured for standard 1920x1080 resolution")
        return True
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """
        Get the current screen resolution.
        
        Returns:
            Tuple[int, int]: (width, height) of the screen
        """
        return (self.monitor['width'], self.monitor['height'])
    
    def save_capture(self, image: np.ndarray, filename: str):
        """
        Save a captured image to disk.
        
        Args:
            image: Image array to save
            filename: Output filename
        """
        try:
            img = Image.fromarray(image)
            img.save(filename)
            logger.info(f"Capture saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save capture: {e}")
    
    def cleanup(self):
        """Release screen capture resources."""
        if self.sct:
            self.sct.close()
            logger.info("Screen capture resources released")


if __name__ == "__main__":
    # Example usage
    logger.add("screen_capture.log", rotation="10 MB")
    
    capture = ScreenCapture()
    capture.auto_detect_sc2_window()
    
    # Capture full screen
    screen = capture.capture_screen()
    if screen is not None:
        print(f"Captured screen: {screen.shape}")
        capture.save_capture(screen, "test_capture.png")
    
    # Capture specific region
    minimap = capture.capture_named_region('minimap')
    if minimap is not None:
        print(f"Captured minimap: {minimap.shape}")
    
    capture.cleanup()
