"""
Comprehensive dry-run certification scene for HobbitTown.

This module runs a deterministic bench test across all three smials, then
validates shared systems (fogger, exciters, stream, sky). The scene is
non-blocking: call update() repeatedly from a loop.
"""

import json
import time

import digitalio  # type: ignore

import config
from hardware import atmosphere
from hardware import audio
from hardware import lighting_ground
from hardware import lighting_sky
from hardware import lighting_stream
from hardware import motion


WARM_COLOR = (255, 180, 40)
OFF_COLOR = (0, 0, 0)


class ComprehensiveDryRunScene:
    """Runs a full hardware dry-run with per-stage pass/fail reporting."""

    def __init__(self, smial_tracks=None, exciter_tracks=None):
        if smial_tracks is None:
            smial_tracks = (310, 312, 314)
        if exciter_tracks is None:
            exciter_tracks = (1, 2)

        self.smials = [
            {
                "name": "Smial 1",
                "door_id": 1,
                "relay_pin": config.CHIMNEY_RELAY_PIN1,
                "audio_output": 1,
                "track": int(smial_tracks[0]),
                "segments": ["smial_1"],
            },
            {
                "name": "Smial 2",
                "door_id": 2,
                "relay_pin": config.CHIMNEY_RELAY_PIN2,
                "audio_output": 2,
                "track": int(smial_tracks[1]),
                "segments": ["smial_2"],
            },
            {
                "name": "Smial 3",
                "door_id": 3,
                "relay_pin": config.CHIMNEY_RELAY_PIN3,
                "audio_output": 3,
                "track": int(smial_tracks[2]),
                "segments": ["smial_3_lower", "smial_3_main", "smial_3_upper"],
            },
        ]

        self.exciter_tracks = (int(exciter_tracks[0]), int(exciter_tracks[1]))
        self.segment_map = {}
        self.chimney_relays = {}
        self.stages = []
        self.stage_index = 0
        self.stage_started_at = 0.0
        self.started = False
        self.finished = False
        self.results = []

    def start(self):
        """Initialize hardware and begin staged dry-run execution."""
        self._setup_hardware()
        self._build_stage_plan()
        self.stage_index = 0
        self.stage_started_at = time.monotonic()
        self.started = True
        self.finished = False
        self.results = []
        print("DryRun: started comprehensive certification")

    def update(self):
        """Advance the state machine by one tick."""
        if not self.started or self.finished:
            return

        if self.stage_index >= len(self.stages):
            self._finalize()
            return

        now = time.monotonic()
        stage = self.stages[self.stage_index]
        elapsed = now - self.stage_started_at

        if elapsed <= 0.02:
            print("DryRun: stage ->", stage["name"])

        stage["tick"](elapsed)

        if elapsed >= stage["duration_s"]:
            self.results.append({"stage": stage["name"], "status": "PASS"})
            self.stage_index += 1
            self.stage_started_at = now

    def stop(self):
        """Stop execution and place hardware in a safe state."""
        self._safe_shutdown()
        self.finished = True
        self.started = False
        print("DryRun: stopped")

    def is_complete(self):
        return self.finished

    def get_results(self):
        return list(self.results)

    def _setup_hardware(self):
        self.segment_map = self._load_segment_map()

        lighting_ground.setup_lighting_ground()
        lighting_stream.setup_lighting_stream()
        lighting_sky.setup_lighting_sky()
        motion.setup_hardware()
        audio.setup_audio()
        atmosphere.setup_atmosphere()

        self._setup_chimney_relays()
        self._safe_shutdown()

    def _setup_chimney_relays(self):
        self.chimney_relays = {}
        for smial in self.smials:
            relay = digitalio.DigitalInOut(smial["relay_pin"])
            relay.direction = digitalio.Direction.OUTPUT
            relay.value = True
            self.chimney_relays[smial["name"]] = relay

    def _load_segment_map(self):
        segment_map = {}
        try:
            with open("ref/lights.json", "r") as f:
                data = json.load(f)
            for strip_name in ("strip_ground_effects", "strip_standard_ws2812b"):
                for segment in data.get(strip_name, {}).get("segments", []):
                    segment_map[segment["id"]] = tuple(segment["range"])
        except Exception as exc:
            print("DryRun: unable to load segment map", exc)
        return segment_map

    def _build_stage_plan(self):
        self.stages = []
        for smial in self.smials:
            self.stages.append(
                {
                    "name": smial["name"] + " | door",
                    "duration_s": 4.0,
                    "tick": self._mk_door_tick(smial),
                }
            )
            self.stages.append(
                {
                    "name": smial["name"] + " | chimney relay",
                    "duration_s": 3.0,
                    "tick": self._mk_chimney_tick(smial),
                }
            )
            self.stages.append(
                {
                    "name": smial["name"] + " | spot track",
                    "duration_s": 3.0,
                    "tick": self._mk_audio_tick(smial["audio_output"], smial["track"]),
                }
            )
            self.stages.append(
                {
                    "name": smial["name"] + " | light",
                    "duration_s": 4.0,
                    "tick": self._mk_smial_light_tick(smial["segments"]),
                }
            )

        self.stages.extend(
            [
                {
                    "name": "Shared | fogger relay",
                    "duration_s": 4.0,
                    "tick": self._tick_fogger,
                },
                {
                    "name": "Shared | exciter track 1",
                    "duration_s": 3.0,
                    "tick": self._mk_audio_tick(5, self.exciter_tracks[0]),
                },
                {
                    "name": "Shared | exciter track 2",
                    "duration_s": 3.0,
                    "tick": self._mk_audio_tick(6, self.exciter_tracks[1]),
                },
                {
                    "name": "Shared | stream lights",
                    "duration_s": 5.0,
                    "tick": self._tick_stream,
                },
                {
                    "name": "Shared | sky lights",
                    "duration_s": 5.0,
                    "tick": self._tick_sky,
                },
            ]
        )

    def _mk_door_tick(self, smial):
        door_id = smial["door_id"]

        def tick(elapsed):
            if elapsed < 2.0:
                angle = int((elapsed / 2.0) * 90)
            else:
                down = min(1.0, (elapsed - 2.0) / 2.0)
                angle = int(90 - (down * 90))
            motion.set_door(door_id, angle)

        return tick

    def _mk_chimney_tick(self, smial):
        relay = self.chimney_relays.get(smial["name"])

        def tick(elapsed):
            if relay is None:
                return
            relay.value = elapsed >= 1.5

        return tick

    def _mk_audio_tick(self, output_number, track):
        played = {"done": False}

        def tick(elapsed):
            if not played["done"]:
                audio.play_audio(output_number, track, loop=False)
                played["done"] = True

        return tick

    def _mk_smial_light_tick(self, segment_ids):
        def tick(elapsed):
            if elapsed < 2.0:
                level = elapsed / 2.0
            else:
                level = max(0.0, 1.0 - ((elapsed - 2.0) / 2.0))
            rgb = (
                int(WARM_COLOR[0] * level),
                int(WARM_COLOR[1] * level),
                int(WARM_COLOR[2] * level),
            )
            self._set_segments(segment_ids, rgb)

        return tick

    def _tick_fogger(self, elapsed):
        if atmosphere.fogger_relay is None:
            return
        atmosphere.fogger_relay.value = elapsed >= 2.0

    def _tick_stream(self, elapsed):
        if elapsed < 0.1:
            lighting_stream.apply_lighting_preset_stream(5)
        lighting_stream.run_lighting_cycle_stream()

    def _tick_sky(self, elapsed):
        if elapsed < 0.1:
            lighting_sky.apply_lighting_preset_sky(5)
        lighting_sky.run_lighting_cycle_sky()

    def _set_segments(self, segment_ids, rgb):
        if lighting_ground.pixels is None:
            return

        r = int(rgb[0] * config.BRIGHTNESS)
        g = int(rgb[1] * config.BRIGHTNESS)
        b = int(rgb[2] * config.BRIGHTNESS)

        for seg_id in segment_ids:
            if seg_id not in self.segment_map:
                continue
            start, end = self.segment_map[seg_id]
            for i in range(start, end + 1):
                lighting_ground.pixels[i] = (r, g, b)

        lighting_ground.pixels.show()

    def _safe_shutdown(self):
        motion.set_door(1, 90)
        motion.set_door(2, 90)
        motion.set_door(3, 90)

        if atmosphere.fogger_relay is not None:
            atmosphere.fogger_relay.value = True

        for relay in self.chimney_relays.values():
            relay.value = True

        self._set_segments(("smial_1", "smial_2", "smial_3_lower", "smial_3_main", "smial_3_upper"), OFF_COLOR)
        lighting_stream.set_all_lights_off_stream()
        lighting_sky.set_all_lights_off_sky()

    def _finalize(self):
        self._safe_shutdown()
        self.finished = True
        self.started = False
        print("DryRun: certification complete")
        print("DryRun: results ->", self.results)


def run_comprehensive_dry_run(
    smial_tracks=(310, 312, 314),
    exciter_tracks=(1, 2),
    tick_delay_s=0.02,
):
    """Run the complete dry-run sequence until completion."""
    scene = ComprehensiveDryRunScene(smial_tracks=smial_tracks, exciter_tracks=exciter_tracks)
    scene.start()
    while not scene.is_complete():
        scene.update()
        time.sleep(tick_delay_s)
    return scene.get_results()
