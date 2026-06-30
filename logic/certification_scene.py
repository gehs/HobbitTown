"""
certification_scene.py
Hardware certification scene: systematically test all smials and their components.
Non-blocking implementation using time.monotonic() for 2-minute runtime.
"""
import time
import math
import hardware.lighting_manager as lighting_manager
import hardware.motion as motion
import hardware.atmosphere as atmosphere
import hardware.audio as audio


class SmialTestScene:
    """Test scene that validates all hardware across three smials."""
    
    def __init__(self):
        self.is_running = False
        self.scene_start_time = None
        self.current_smial = 0  # 0=Smial1, 1=Smial2, 2=Smial3
        self.smials = [
            {
                'name': 'Smial 1',
                'door_id': 1,
                'light_segment': 'smial_1',
                'speaker_output': 1,
                'speaker_track': 1,
                'start_time': 0,
                'end_time': 40,
            },
            {
                'name': 'Smial 2',
                'door_id': 2,
                'light_segment': 'smial_2',
                'speaker_output': 2,
                'speaker_track': 2,
                'start_time': 40,
                'end_time': 80,
            },
            {
                'name': 'Smial 3',
                'door_id': 3,
                'light_segment': 'smial_3',
                'speaker_output': 3,
                'speaker_track': 3,
                'start_time': 80,
                'end_time': 120,
            },
        ]
    
    def start(self):
        """Begin test scene."""
        self.is_running = True
        self.scene_start_time = time.monotonic()
        self.current_smial = 0
        print("SmialTestScene: ✓ Hardware certification starting")
    
    def stop(self):
        """End test scene and reset hardware."""
        self.is_running = False
        motion.set_door(1, 90)
        motion.set_door(2, 90)
        motion.set_door(3, 90)
        lighting_manager.set_segment_color('smial_1', (0, 0, 0))
        lighting_manager.set_segment_color('smial_2', (0, 0, 0))
        lighting_manager.set_segment_color('smial_3', (0, 0, 0))
        atmosphere.setup_atmosphere()
        print("SmialTestScene: ✓ Hardware test complete")
    
    def update(self):
        """Non-blocking update cycle."""
        if not self.is_running or self.scene_start_time is None:
            return
        
        elapsed = time.monotonic() - self.scene_start_time
        
        # Determine which smial to test
        smial = None
        for s in self.smials:
            if s['start_time'] <= elapsed < s['end_time']:
                smial = s
                break
        
        if smial is None:
            if elapsed >= 120:
                print("SmialTestScene: All tests complete")
                self.stop()
            return
        
        smial_elapsed = elapsed - smial['start_time']
        self._run_smial_test(smial, smial_elapsed)
    
    def _run_smial_test(self, smial, elapsed):
        """Run test sequence for a single smial."""
        door_id = smial['door_id']
        light_segment = smial['light_segment']
        
        # 0-2s: Play bell tone + narration
        if elapsed < 2:
            if elapsed < 0.1:
                print(f"SmialTestScene: Testing {smial['name']}...")
                audio.play_audio(smial['speaker_output'], smial['speaker_track'], loop=False)
        
        # 2-5s: Door opens
        elif 2 <= elapsed < 5:
            progress = (elapsed - 2) / 3.0
            angle = 90 * progress
            motion.set_door(door_id, int(angle))
        
        # 5-8s: Door closes
        elif 5 <= elapsed < 8:
            progress = (elapsed - 5) / 3.0
            angle = 90 - (90 * progress)
            motion.set_door(door_id, int(angle))
        
        # 8-12s: Lights fade in (warm white)
        elif 8 <= elapsed < 12:
            progress = (elapsed - 8) / 4.0
            brightness = int(255 * progress)
            rgb = (brightness, brightness - 50, 0)  # Warm white
            lighting_manager.set_segment_color(light_segment, rgb)
        
        # 12-15s: Lights fade out
        elif 12 <= elapsed < 15:
            progress = (elapsed - 12) / 3.0
            brightness = int(255 * (1 - progress))
            rgb = (brightness, max(0, brightness - 50), 0)
            lighting_manager.set_segment_color(light_segment, rgb)
        
        # 15-18s: Fogger activates
        elif 15 <= elapsed < 18:
            if elapsed < 15.5:
                # Activate fogger via atmosphere module
                if hasattr(atmosphere, 'fogger_relay') and atmosphere.fogger_relay:
                    atmosphere.fogger_relay.value = False  # Relay ON
        
        # 18-20s: Fogger holds (chimney rising visual optional)
        elif 18 <= elapsed < 20:
            pass  # Fogger stays on
        
        # 20-25s: Fogger stops
        elif 20 <= elapsed < 25:
            if elapsed < 20.5:
                # Deactivate fogger
                if hasattr(atmosphere, 'fogger_relay') and atmosphere.fogger_relay:
                    atmosphere.fogger_relay.value = True  # Relay OFF
        
        # 25-40s: Silence/pause
        else:
            motion.set_door(door_id, 90)  # Reset to default
            lighting_manager.set_segment_color(light_segment, (0, 0, 0))


# Global instance
smial_test = SmialTestScene()
