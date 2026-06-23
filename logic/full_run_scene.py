"""
full_run_scene.py
Sequential full hardware run-through: tests all three smials one at a time.

Each smial runs a 40-second window:
  t= 0s  — spot speaker plays (track N on output N)
  t= 2s  — door servo opens
  t= 5s  — door servo closes
  t= 8s  — smial + chimney LEDs fade in over 1 second
  t=12s  — chimney smoker relay ON
  t=20s  — chimney smoker relay OFF
  t=25s  — LEDs fade out over 1 second
  t=40s  — advance to next smial

Ambient bed (track 4, output 4) and both exciters (tracks 5+6, outputs 5+6)
loop from scene start through the full 120-second run.

Total scene time: 120 seconds, then auto-stop.
"""

import time
import hardware.lighting_manager as lighting_manager
import hardware.motion as motion
import hardware.atmosphere as atmosphere
import hardware.audio as audio

# Warm amber-white used for smial and chimney glow segments
_WARM_WHITE = (255, 200, 100)

# Seconds each smial occupies in the run
_SMIAL_WINDOW = 40

# Full scene duration
_SCENE_DURATION = _SMIAL_WINDOW * 3  # 120 seconds


class FullRunScene:
    """
    Non-blocking 2-minute hardware run-through covering all three smials.
    Call start() once, then update() every main-loop iteration.
    """

    def __init__(self):
        self.is_running = False
        self._start_time = None
        # Track which smial steps have already been triggered (one-shot guards)
        self._triggered = {}

        self._smials = [
            {
                'name': 'Smial 1',
                'door_id': 1,
                'light_segments': ['smial_1', 'chimney_smial_1'],
                'chimney_id': 1,
                'audio_output': 1,
                'audio_track': 1,
                'start_time': 0,
            },
            {
                'name': 'Smial 2',
                'door_id': 2,
                'light_segments': ['smial_2', 'chimney_smial_2'],
                'chimney_id': 2,
                'audio_output': 2,
                'audio_track': 2,
                'start_time': 40,
            },
            {
                'name': 'Smial 3',
                'door_id': 3,
                'light_segments': [
                    'smial_3_lower',
                    'smial_3_main',
                    'smial_3_upper',
                    'chimney_smial_3',
                ],
                'chimney_id': 3,
                'audio_output': 3,
                'audio_track': 3,
                'start_time': 80,
            },
        ]

    def start(self):
        """Begin the full run-through."""
        self._start_time = time.monotonic()
        self._triggered = {}
        self.is_running = True

        atmosphere.setup_chimneys()

        # Start ambient bed and exciters looping from the beginning
        audio.play_audio(4, 4, loop=True)
        audio.play_audio(5, 5, loop=True)
        audio.play_audio(6, 6, loop=True)

        print("FullRunScene: starting — 120-second hardware run-through")

    def stop(self):
        """Reset all hardware and mark scene complete."""
        self.is_running = False
        audio.stop_all()
        motion.reset_all()
        atmosphere.stop_chimneys()
        lighting_manager.stop_lighting()
        print("FullRunScene: complete — all hardware reset")

    def update(self):
        """Non-blocking update; call once per main-loop iteration."""
        if not self.is_running or self._start_time is None:
            return

        elapsed = time.monotonic() - self._start_time

        if elapsed >= _SCENE_DURATION:
            self.stop()
            return

        # Find the active smial based on elapsed time
        smial = None
        for s in self._smials:
            window_end = s['start_time'] + _SMIAL_WINDOW
            if s['start_time'] <= elapsed < window_end:
                smial = s
                break

        if smial is None:
            return

        smial_elapsed = elapsed - smial['start_time']
        self._run_smial_step(smial, smial_elapsed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _once(self, key):
        """Return True the first time this key is seen; False on repeats."""
        if key in self._triggered:
            return False
        self._triggered[key] = True
        return True

    def _set_segments(self, segments, rgb):
        """Apply the same RGB color to a list of segment IDs."""
        for seg in segments:
            lighting_manager.set_segment_color(seg, rgb)

    def _run_smial_step(self, smial, elapsed):
        name = smial['name']
        door_id = smial['door_id']
        segments = smial['light_segments']
        chimney_id = smial['chimney_id']
        audio_output = smial['audio_output']
        audio_track = smial['audio_track']

        # t = 0s: play spot speaker once
        if elapsed < 2:
            if self._once(f'{name}_audio'):
                print(f"FullRunScene: {name} — playing track {audio_track} on output {audio_output}")
                audio.play_audio(audio_output, audio_track, loop=False)

        # t = 2–5s: door sweeps open (0° → 90°)
        elif 2 <= elapsed < 5:
            if self._once(f'{name}_door_open_start'):
                print(f"FullRunScene: {name} — door opening")
            progress = (elapsed - 2) / 3.0
            motion.set_door(door_id, int(90 * progress))

        # t = 5–8s: door sweeps closed (90° → 0°)
        elif 5 <= elapsed < 8:
            if self._once(f'{name}_door_close_start'):
                print(f"FullRunScene: {name} — door closing")
            progress = (elapsed - 5) / 3.0
            motion.set_door(door_id, int(90 * (1.0 - progress)))

        # t = 8–9s: lights fade in over 1 second
        elif 8 <= elapsed < 9:
            progress = elapsed - 8  # 0.0 → 1.0
            r = int(_WARM_WHITE[0] * progress)
            g = int(_WARM_WHITE[1] * progress)
            b = int(_WARM_WHITE[2] * progress)
            self._set_segments(segments, (r, g, b))

        # t = 9–12s: lights hold at full brightness
        elif 9 <= elapsed < 12:
            if self._once(f'{name}_lights_full'):
                self._set_segments(segments, _WARM_WHITE)

        # t = 12s: chimney smoker ON
        elif 12 <= elapsed < 20:
            if self._once(f'{name}_chimney_on'):
                print(f"FullRunScene: {name} — chimney smoker ON")
                atmosphere.set_chimney(chimney_id, True)

        # t = 20s: chimney smoker OFF
        elif 20 <= elapsed < 25:
            if self._once(f'{name}_chimney_off'):
                print(f"FullRunScene: {name} — chimney smoker OFF")
                atmosphere.set_chimney(chimney_id, False)

        # t = 25–26s: lights fade out over 1 second
        elif 25 <= elapsed < 26:
            progress = elapsed - 25  # 0.0 → 1.0
            r = int(_WARM_WHITE[0] * (1.0 - progress))
            g = int(_WARM_WHITE[1] * (1.0 - progress))
            b = int(_WARM_WHITE[2] * (1.0 - progress))
            self._set_segments(segments, (r, g, b))

        # t = 26–40s: hold dark, door back to neutral
        elif elapsed >= 26:
            if self._once(f'{name}_done'):
                print(f"FullRunScene: {name} — complete")
                self._set_segments(segments, (0, 0, 0))
                motion.set_door(door_id, 90)  # Neutral rest position


# Module-level instance — import and call .start() / .update() from code.py
full_run = FullRunScene()
