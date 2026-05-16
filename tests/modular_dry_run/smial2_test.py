import digitalio  # type: ignore

import config
from tests.modular_dry_run import common


class Smial2ModuleTest:
    """Dry-run module for Smial 2: door, chimney relay, speaker, and lights."""

    def __init__(self, track=312):
        self.name = "Smial2"
        self.track = int(track)
        self.duration_s = 9.0
        self._start = None
        self._done = False
        self._played = False
        self._relay = None
        self._segment_map = {}

    def start(self):
        self._done = False
        self._played = False
        self._start = common.monotonic_now()
        self._segment_map = common.load_segment_map()
        self._relay = digitalio.DigitalInOut(config.CHIMNEY_RELAY_PIN2)
        self._relay.direction = digitalio.Direction.OUTPUT
        self._relay.value = True
        print("[TEST:smial2] start")

    def update(self):
        if self._done or self._start is None:
            return

        elapsed = common.monotonic_now() - self._start

        if elapsed < 2.0:
            angle = int((elapsed / 2.0) * 90)
            common.motion.set_door(2, angle)
        elif elapsed < 4.0:
            down = min(1.0, (elapsed - 2.0) / 2.0)
            common.motion.set_door(2, int(90 - down * 90))

        if self._relay is not None:
            self._relay.value = elapsed >= 5.0

        if not self._played and elapsed >= 5.0:
            self._played = True
            common.play_track_checked(2, self.track, loop=False)

        if elapsed < 7.5:
            level = min(1.0, max(0.0, (elapsed - 4.0) / 3.5))
            common.set_ground_segments(self._segment_map, ("smial_2",), (int(255 * level), int(170 * level), int(40 * level)))
        else:
            common.set_ground_segments(self._segment_map, ("smial_2",), (0, 0, 0))

        if elapsed >= self.duration_s:
            self.stop()

    def stop(self):
        if self._relay is not None:
            self._relay.value = True
        common.motion.set_door(2, 90)
        common.set_ground_segments(self._segment_map, ("smial_2",), (0, 0, 0))
        self._done = True
        print("[TEST:smial2] done")

    def is_complete(self):
        return self._done
