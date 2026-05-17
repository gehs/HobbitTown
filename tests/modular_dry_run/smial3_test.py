import digitalio  # type: ignore

import config
from tests.modular_dry_run import common


class Smial3ModuleTest:
    """Dry-run module for Smial 3: door, chimney relay, speaker, and grouped lights."""

    def __init__(self, track=314, output_number=3, end_track=316):
        self.name = "Smial3"
        self.track = int(track)
        self.output_number = int(output_number)
        self.end_track = int(end_track)
        self.duration_s = 9.0
        self._start = None
        self._done = False
        self._played = False
        self._end_played = False
        self._relay = None
        self._segment_map = {}
        self._segments = ("smial_3_lower", "smial_3_main", "smial_3_upper", "chimney_smial_3")

    def start(self):
        self._done = False
        self._played = False
        self._end_played = False
        self._start = common.monotonic_now()
        self._segment_map = common.load_segment_map()
        self._relay = digitalio.DigitalInOut(config.CHIMNEY_RELAY_PIN3)
        self._relay.direction = digitalio.Direction.OUTPUT
        self._relay.value = True
        print("[TEST:smial3] start")

    def update(self):
        if self._done or self._start is None:
            return

        elapsed = common.monotonic_now() - self._start

        if elapsed < 2.0:
            angle = int((elapsed / 2.0) * 90)
            common.motion.set_door(3, angle)
        elif elapsed < 4.0:
            down = min(1.0, (elapsed - 2.0) / 2.0)
            common.motion.set_door(3, int(90 - down * 90))

        if self._relay is not None:
            self._relay.value = elapsed >= 5.0

        if not self._played and elapsed >= 5.0:
            self._played = True
            common.play_track_checked(self.output_number, self.track, loop=False)

        if elapsed < 7.5:
            level = min(1.0, max(0.0, (elapsed - 4.0) / 3.5))
            common.set_ground_segments(self._segment_map, self._segments, (int(255 * level), int(170 * level), int(40 * level)))
        else:
            common.set_ground_segments(self._segment_map, self._segments, (0, 0, 0))

        if elapsed >= self.duration_s:
            self.stop()

    def stop(self):
        if not self._end_played:
            self._end_played = True
            common.play_track_checked(self.output_number, self.end_track, loop=False)
        if self._relay is not None:
            self._relay.value = True
        common.motion.set_door(3, 90)
        common.set_ground_segments(self._segment_map, self._segments, (0, 0, 0))
        self._done = True
        print("[TEST:smial3] done")

    def is_complete(self):
        return self._done
