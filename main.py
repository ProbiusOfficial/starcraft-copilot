"""
main.py
Main entry point for StarCraft II Copilot

This script demonstrates the basic usage of the screen capture assistant tool
for StarCraft II Co-op and Versus modes.
"""

import time
import json
from pathlib import Path
from loguru import logger

from src.ScreenCapture import ScreenCapture
from src.OCR_Analysis import OCRAnalysis
from src.ReminderEngine import ReminderEngine


def load_commander_data():
    """Load co-op commander data from JSON file."""
    data_path = Path(__file__).parent / 'src' / 'DataStore' / 'CoopCommanderData.json'
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load commander data: {e}")
        return None


def main():
    """Main application loop."""
    # Configure logging
    logger.add("sc2_copilot.log", rotation="10 MB", level="INFO")
    logger.info("StarCraft II Copilot starting...")
    
    # Initialize modules
    screen_capture = ScreenCapture()
    ocr_analysis = OCRAnalysis()
    reminder_engine = ReminderEngine(enable_notifications=True)
    
    # Load commander data
    commander_data = load_commander_data()
    if commander_data:
        logger.info(f"Loaded data for {len(commander_data['commanders'])} commanders")
    
    # Auto-detect SC2 window
    if not screen_capture.auto_detect_sc2_window():
        logger.warning("Could not auto-detect StarCraft II window")
        logger.info("Using default screen regions")
    
    # Display configuration
    resolution = screen_capture.get_screen_resolution()
    logger.info(f"Screen resolution: {resolution[0]}x{resolution[1]}")
    
    print("\n" + "="*60)
    print("StarCraft II Copilot - Screen Capture Assistant")
    print("="*60)
    print("\nCore Features:")
    print("  1. Operational Reminders (Worker production, Supply, Resources)")
    print("  2. Co-op Commander Tactics & Prestige")
    print("  3. Attack/Defense Upgrade Tracking")
    print("  4. Amon Red Point Analysis & Timing")
    print("\nPress Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    try:
        # Main monitoring loop
        iteration = 0
        while True:
            iteration += 1
            
            # Capture relevant screen regions
            resource_img = screen_capture.capture_named_region('resources')
            timer_img = screen_capture.capture_named_region('timer')
            
            # Analyze game state (only if captures succeeded)
            if resource_img is not None:
                game_state = ocr_analysis.get_game_state(
                    resource_img=resource_img,
                    supply_img=resource_img,  # Resource bar usually contains supply too
                    timer_img=timer_img
                )
                
                # Process reminders
                reminders = reminder_engine.process_game_state(game_state)
                
                # Display status (every 10 iterations to reduce spam)
                if iteration % 10 == 0:
                    logger.info(
                        f"Status - Time: {game_state['game_time']}, "
                        f"Minerals: {game_state['resources']['minerals']}, "
                        f"Gas: {game_state['resources']['gas']}, "
                        f"Supply: {game_state['supply']['supply_used']}/{game_state['supply']['supply_cap']}"
                    )
                    
                    # Show any active warnings
                    if game_state['warnings']:
                        logger.warning(f"Warnings: {', '.join(game_state['warnings'])}")
            
            # Wait before next capture (adjust based on performance needs)
            time.sleep(2)  # 2 seconds between captures
            
    except KeyboardInterrupt:
        print("\n\nShutting down StarCraft II Copilot...")
        logger.info("Application stopped by user")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    finally:
        # Cleanup
        screen_capture.cleanup()
        logger.info("StarCraft II Copilot stopped")


if __name__ == "__main__":
    main()
