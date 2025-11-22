"""
OCR_Analysis.py
OCR and game state analysis module for StarCraft II Copilot

This module handles Optical Character Recognition (OCR) on captured screen regions
and analyzes the extracted text to determine the current game state.
"""

import cv2
import numpy as np
import pytesseract
import re
from typing import Dict, Optional, List, Tuple
from loguru import logger


class OCRAnalysis:
    """
    Handles OCR and analysis of StarCraft II game state from screen captures.
    
    This class provides methods to extract text from images and interpret
    game-relevant information such as resources, supply, time, and unit counts.
    """
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize the OCR analysis engine.
        
        Args:
            tesseract_path: Optional path to tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        logger.info("OCR Analysis initialized")
        
        # Cache for last known good values (helps with OCR errors)
        self.last_known_state = {
            'minerals': 0,
            'gas': 0,
            'supply_used': 0,
            'supply_cap': 0,
            'game_time': '00:00'
        }
    
    def preprocess_image(self, image: np.ndarray, 
                        enhance: bool = True) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image as numpy array
            enhance: Whether to apply enhancement filters
            
        Returns:
            np.ndarray: Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        if enhance:
            # Apply thresholding for better text recognition
            _, thresh = cv2.threshold(gray, 0, 255, 
                                     cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            return enhanced
        
        return gray
    
    def extract_text(self, image: np.ndarray, 
                    config: str = '--psm 7') -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image: Input image
            config: Tesseract configuration string
            
        Returns:
            str: Extracted text
        """
        try:
            processed = self.preprocess_image(image)
            text = pytesseract.image_to_string(processed, config=config)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def extract_numbers(self, text: str) -> List[int]:
        """
        Extract numeric values from text.
        
        Args:
            text: Input text
            
        Returns:
            List[int]: List of extracted numbers
        """
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]
    
    def analyze_resources(self, image: np.ndarray) -> Dict[str, int]:
        """
        Analyze resource bar to extract minerals and gas.
        
        Args:
            image: Image of the resource region
            
        Returns:
            Dict containing 'minerals' and 'gas' values
        """
        text = self.extract_text(image)
        numbers = self.extract_numbers(text)
        
        result = {
            'minerals': self.last_known_state['minerals'],
            'gas': self.last_known_state['gas']
        }
        
        if len(numbers) >= 2:
            result['minerals'] = numbers[0]
            result['gas'] = numbers[1]
            # Update cache
            self.last_known_state['minerals'] = numbers[0]
            self.last_known_state['gas'] = numbers[1]
            logger.debug(f"Resources: {result['minerals']} minerals, {result['gas']} gas")
        
        return result
    
    def analyze_supply(self, image: np.ndarray) -> Dict[str, int]:
        """
        Analyze supply information (used/cap).
        
        Args:
            image: Image of the supply region
            
        Returns:
            Dict containing 'supply_used' and 'supply_cap'
        """
        text = self.extract_text(image)
        
        result = {
            'supply_used': self.last_known_state['supply_used'],
            'supply_cap': self.last_known_state['supply_cap']
        }
        
        # Supply is typically shown as "XX/YY"
        if '/' in text:
            parts = text.split('/')
            if len(parts) == 2:
                try:
                    supply_used = int(''.join(filter(str.isdigit, parts[0])))
                    supply_cap = int(''.join(filter(str.isdigit, parts[1])))
                    result['supply_used'] = supply_used
                    result['supply_cap'] = supply_cap
                    # Update cache
                    self.last_known_state['supply_used'] = supply_used
                    self.last_known_state['supply_cap'] = supply_cap
                    logger.debug(f"Supply: {supply_used}/{supply_cap}")
                except ValueError:
                    pass
        
        return result
    
    def analyze_game_time(self, image: np.ndarray) -> str:
        """
        Extract game timer.
        
        Args:
            image: Image of the timer region
            
        Returns:
            str: Game time in MM:SS format
        """
        text = self.extract_text(image)
        
        # Game time is typically in MM:SS format
        time_match = re.search(r'(\d{1,2}):(\d{2})', text)
        
        if time_match:
            game_time = time_match.group(0)
            self.last_known_state['game_time'] = game_time
            logger.debug(f"Game time: {game_time}")
            return game_time
        
        return self.last_known_state['game_time']
    
    def detect_supply_block(self, supply_data: Dict[str, int], 
                          threshold: float = 0.9) -> bool:
        """
        Detect if player is supply blocked or approaching supply cap.
        
        Args:
            supply_data: Dict with 'supply_used' and 'supply_cap'
            threshold: Percentage threshold for warning (default 90%)
            
        Returns:
            bool: True if supply blocked or near cap
        """
        supply_used = supply_data.get('supply_used', 0)
        supply_cap = supply_data.get('supply_cap', 200)
        
        if supply_cap == 0:
            return False
        
        ratio = supply_used / supply_cap
        return ratio >= threshold
    
    def detect_resource_overflow(self, resource_data: Dict[str, int],
                                 threshold: int = 1000) -> List[str]:
        """
        Detect resource overflow (too many unspent resources).
        
        Args:
            resource_data: Dict with 'minerals' and 'gas'
            threshold: Resource threshold for overflow warning
            
        Returns:
            List[str]: List of overflowing resource types
        """
        overflow = []
        
        minerals = resource_data.get('minerals', 0)
        gas = resource_data.get('gas', 0)
        
        if minerals > threshold:
            overflow.append('minerals')
            logger.warning(f"Mineral overflow detected: {minerals}")
        
        if gas > threshold:
            overflow.append('gas')
            logger.warning(f"Gas overflow detected: {gas}")
        
        return overflow
    
    def get_game_state(self, resource_img: Optional[np.ndarray] = None,
                      supply_img: Optional[np.ndarray] = None,
                      timer_img: Optional[np.ndarray] = None) -> Dict:
        """
        Get comprehensive game state from multiple image regions.
        
        Args:
            resource_img: Image of resource bar
            supply_img: Image of supply counter
            timer_img: Image of game timer
            
        Returns:
            Dict: Complete game state information
        """
        state = {
            'resources': {'minerals': 0, 'gas': 0},
            'supply': {'supply_used': 0, 'supply_cap': 200},
            'game_time': '00:00',
            'warnings': []
        }
        
        if resource_img is not None:
            state['resources'] = self.analyze_resources(resource_img)
        
        if supply_img is not None:
            state['supply'] = self.analyze_supply(supply_img)
        
        if timer_img is not None:
            state['game_time'] = self.analyze_game_time(timer_img)
        
        # Check for warnings
        if self.detect_supply_block(state['supply']):
            state['warnings'].append('supply_block')
        
        overflow = self.detect_resource_overflow(state['resources'])
        if overflow:
            state['warnings'].extend([f'{res}_overflow' for res in overflow])
        
        return state


if __name__ == "__main__":
    # Example usage
    logger.add("ocr_analysis.log", rotation="10 MB")
    
    ocr = OCRAnalysis()
    
    # Test with sample data (in real use, would come from ScreenCapture)
    print("OCR Analysis module initialized successfully")
    print("Ready to process game state from screen captures")
