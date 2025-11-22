"""
ReminderEngine.py
Reminder and notification engine for StarCraft II Copilot

This module handles the logic for generating reminders and notifications
based on the analyzed game state.
"""

import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
from loguru import logger
from plyer import notification


class ReminderEngine:
    """
    Manages reminders and notifications based on game state analysis.
    
    This class provides intelligent reminder logic for various game events
    such as worker production, supply management, upgrades, and attack timings.
    """
    
    def __init__(self, enable_notifications: bool = True):
        """
        Initialize the reminder engine.
        
        Args:
            enable_notifications: Whether to enable desktop notifications
        """
        self.enable_notifications = enable_notifications
        self.reminder_history = []
        self.cooldowns = {}  # Prevent spam of same reminders
        self.default_cooldown = 30  # seconds
        
        # Configurable thresholds
        self.config = {
            'supply_warning_threshold': 0.85,  # Warn at 85% supply
            'supply_critical_threshold': 0.95,  # Critical at 95% supply
            'resource_overflow_threshold': 1000,
            'worker_ideal_count': {
                'early': 16,   # Per base early game
                'mid': 22,     # Per base mid game
                'late': 24,    # Per base late game (saturated)
            },
            'upgrade_reminder_interval': 120,  # Remind about upgrades every 2 min
            'amon_attack_wave_intervals': [240, 480, 720, 960],  # 4, 8, 12, 16 min
        }
        
        logger.info("Reminder Engine initialized")
    
    def _can_send_reminder(self, reminder_type: str) -> bool:
        """
        Check if a reminder can be sent (cooldown management).
        
        Args:
            reminder_type: Type of reminder to check
            
        Returns:
            bool: True if reminder can be sent
        """
        current_time = time.time()
        
        if reminder_type in self.cooldowns:
            last_time = self.cooldowns[reminder_type]
            if current_time - last_time < self.default_cooldown:
                return False
        
        self.cooldowns[reminder_type] = current_time
        return True
    
    def _send_notification(self, title: str, message: str, urgency: str = 'normal'):
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level ('low', 'normal', 'critical')
        """
        if not self.enable_notifications:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='SC2 Copilot',
                timeout=5
            )
            logger.info(f"Notification sent: {title} - {message}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
        
        # Log to history
        self.reminder_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': title,
            'message': message,
            'urgency': urgency
        })
    
    def check_supply(self, supply_data: Dict[str, int]) -> Optional[str]:
        """
        Check supply status and generate reminders if needed.
        
        Args:
            supply_data: Dict with 'supply_used' and 'supply_cap'
            
        Returns:
            Optional[str]: Reminder message if needed
        """
        supply_used = supply_data.get('supply_used', 0)
        supply_cap = supply_data.get('supply_cap', 200)
        
        if supply_cap == 0:
            return None
        
        ratio = supply_used / supply_cap
        
        if ratio >= self.config['supply_critical_threshold']:
            if self._can_send_reminder('supply_critical'):
                message = f"⚠️ SUPPLY BLOCKED! {supply_used}/{supply_cap}"
                self._send_notification("Supply Critical", message, 'critical')
                return message
        elif ratio >= self.config['supply_warning_threshold']:
            if self._can_send_reminder('supply_warning'):
                message = f"⚠️ Supply Warning: {supply_used}/{supply_cap}"
                self._send_notification("Build Supply", message, 'normal')
                return message
        
        return None
    
    def check_resources(self, resource_data: Dict[str, int], 
                       game_time_seconds: int) -> List[str]:
        """
        Check resource levels and generate overflow warnings.
        
        Args:
            resource_data: Dict with 'minerals' and 'gas'
            game_time_seconds: Current game time in seconds
            
        Returns:
            List[str]: List of reminder messages
        """
        reminders = []
        minerals = resource_data.get('minerals', 0)
        gas = resource_data.get('gas', 0)
        
        # Only check overflow after first few minutes
        if game_time_seconds < 180:  # 3 minutes
            return reminders
        
        threshold = self.config['resource_overflow_threshold']
        
        if minerals > threshold:
            if self._can_send_reminder('mineral_overflow'):
                message = f"💎 High minerals: {minerals} - Expand or build army!"
                self._send_notification("Resource Alert", message)
                reminders.append(message)
        
        if gas > threshold:
            if self._can_send_reminder('gas_overflow'):
                message = f"⛽ High gas: {gas} - Tech up or build advanced units!"
                self._send_notification("Resource Alert", message)
                reminders.append(message)
        
        return reminders
    
    def check_worker_production(self, worker_count: int, 
                               base_count: int,
                               game_phase: str = 'mid') -> Optional[str]:
        """
        Remind about worker production.
        
        Args:
            worker_count: Current worker count
            base_count: Number of bases
            game_phase: Current game phase ('early', 'mid', 'late')
            
        Returns:
            Optional[str]: Reminder message if needed
        """
        ideal_workers = self.config['worker_ideal_count'].get(game_phase, 22)
        target_workers = ideal_workers * base_count
        
        if worker_count < target_workers * 0.8:  # Below 80% of ideal
            if self._can_send_reminder('worker_production'):
                message = f"👷 Build workers! Current: {worker_count}, Target: ~{target_workers}"
                self._send_notification("Worker Production", message)
                return message
        
        return None
    
    def check_upgrade_timing(self, game_time_seconds: int,
                           current_upgrades: Dict[str, int]) -> List[str]:
        """
        Remind about upgrade timings.
        
        Args:
            game_time_seconds: Current game time in seconds
            current_upgrades: Dict of upgrade types and levels
            
        Returns:
            List[str]: Reminder messages
        """
        reminders = []
        
        # Typical upgrade timings
        upgrade_timings = {
            300: "Consider starting +1 attack/armor upgrades",  # 5 min
            480: "Time for +2 upgrades if +1 is done",  # 8 min
            720: "Consider +3 upgrades if +2 is complete",  # 12 min
        }
        
        for timing, message in upgrade_timings.items():
            reminder_key = f"upgrade_{timing}"
            if game_time_seconds >= timing and self._can_send_reminder(reminder_key):
                self._send_notification("Upgrade Reminder", f"⬆️ {message}")
                reminders.append(message)
                break  # Only send one upgrade reminder at a time
        
        return reminders
    
    def check_amon_attack_wave(self, game_time_seconds: int,
                              mission_type: str = 'standard') -> Optional[Dict]:
        """
        Predict and remind about Amon attack waves (Co-op mode).
        
        Args:
            game_time_seconds: Current game time in seconds
            mission_type: Type of mission affecting wave timings
            
        Returns:
            Optional[Dict]: Attack wave information if imminent
        """
        wave_intervals = self.config['amon_attack_wave_intervals']
        
        for i, wave_time in enumerate(wave_intervals):
            time_until_wave = wave_time - game_time_seconds
            
            # Warn 30 seconds before attack wave
            if 0 < time_until_wave <= 30:
                reminder_key = f"amon_wave_{i}"
                if self._can_send_reminder(reminder_key):
                    message = f"🚨 Attack wave incoming in {int(time_until_wave)}s!"
                    self._send_notification("Amon Attack Warning", message, 'critical')
                    return {
                        'wave_number': i + 1,
                        'time_until': time_until_wave,
                        'message': message
                    }
        
        return None
    
    def get_commander_tip(self, commander_name: str, 
                         prestige: int,
                         game_phase: str) -> Optional[str]:
        """
        Provide commander-specific tips based on game state.
        
        Args:
            commander_name: Name of the co-op commander
            prestige: Prestige level (0-3)
            game_phase: Current phase ('early', 'mid', 'late')
            
        Returns:
            Optional[str]: Commander tip if available
        """
        # This would typically load from CoopCommanderData.json
        # Placeholder implementation
        tips = {
            'Raynor': {
                'early': "Focus on orbital command calldowns for early aggression",
                'mid': "Build bio ball with medics for sustained push",
                'late': "Use battlecruiser calldowns on key targets"
            },
            'Kerrigan': {
                'early': "Level up Kerrigan quickly with early assaults",
                'mid': "Unlock Ultralisk and Omega Worm abilities",
                'late': "Use Kerrigan's abilities to eliminate high-value targets"
            }
        }
        
        if commander_name in tips and game_phase in tips[commander_name]:
            tip = tips[commander_name][game_phase]
            if self._can_send_reminder(f"commander_tip_{game_phase}"):
                self._send_notification(f"{commander_name} Tip", f"💡 {tip}")
                return tip
        
        return None
    
    def process_game_state(self, game_state: Dict) -> Dict[str, List[str]]:
        """
        Process complete game state and generate all relevant reminders.
        
        Args:
            game_state: Complete game state from OCR analysis
            
        Returns:
            Dict: Categorized reminders
        """
        reminders = {
            'supply': [],
            'resources': [],
            'workers': [],
            'upgrades': [],
            'attacks': [],
            'tips': []
        }
        
        # Convert game time to seconds
        game_time_str = game_state.get('game_time', '00:00')
        try:
            minutes, seconds = map(int, game_time_str.split(':'))
            game_time_seconds = minutes * 60 + seconds
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse game time '{game_time_str}': {e}")
            game_time_seconds = 0
        
        # Check supply
        supply_reminder = self.check_supply(game_state.get('supply', {}))
        if supply_reminder:
            reminders['supply'].append(supply_reminder)
        
        # Check resources
        resource_reminders = self.check_resources(
            game_state.get('resources', {}),
            game_time_seconds
        )
        reminders['resources'].extend(resource_reminders)
        
        # Check upgrades
        upgrade_reminders = self.check_upgrade_timing(
            game_time_seconds,
            game_state.get('upgrades', {})
        )
        reminders['upgrades'].extend(upgrade_reminders)
        
        # Check Amon waves (if in co-op mode)
        if game_state.get('mode') == 'coop':
            wave_info = self.check_amon_attack_wave(game_time_seconds)
            if wave_info:
                reminders['attacks'].append(wave_info['message'])
        
        return reminders
    
    def get_reminder_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent reminder history.
        
        Args:
            limit: Maximum number of reminders to return
            
        Returns:
            List[Dict]: Recent reminders
        """
        return self.reminder_history[-limit:]
    
    def clear_cooldowns(self):
        """Reset all reminder cooldowns."""
        self.cooldowns.clear()
        logger.info("All reminder cooldowns cleared")


if __name__ == "__main__":
    # Example usage
    logger.add("reminder_engine.log", rotation="10 MB")
    
    engine = ReminderEngine(enable_notifications=False)  # Disable for testing
    
    # Test with sample game state
    test_state = {
        'resources': {'minerals': 1500, 'gas': 800},
        'supply': {'supply_used': 190, 'supply_cap': 200},
        'game_time': '08:30',
        'mode': 'coop'
    }
    
    reminders = engine.process_game_state(test_state)
    print("Generated reminders:")
    for category, messages in reminders.items():
        if messages:
            print(f"  {category}: {messages}")
