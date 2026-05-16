from tests.modular_dry_run import common


class StreamModuleTest:
    """Dry-run module for stream: spot speaker 4 plus stream lights."""

    def __init__(self, spot_speaker4_track=314):
        self.name = "Stream"
        self.track = int(spot_speaker4_track)
        self.duration_s = 7.0
        self._start = None
        self._done = False
        self._played = False

    def start(self):
        self._done = False
        self._played = False
        self._start = common.monotonic_now()
        print("[TEST:stream] start")

    def update(self):
        if self._done or self._start is None:
            return

        elapsed = common.monotonic_now() - self._start

        if not self._played and elapsed >= 0.2:
            self._played = True
            # Stream module reserves output 4 range (300-399).
            common.play_track_checked(4, self.track, loop=False)

        if elapsed < 0.2:
            common.lighting_stream.apply_lighting_preset_stream(3)
        elif elapsed < 4.0:
            common.lighting_stream.apply_lighting_preset_stream(5)
            common.lighting_stream.run_lighting_cycle_stream()
        else:
            common.lighting_stream.apply_lighting_preset_stream(4)

        if elapsed >= self.duration_s:
            self.stop()

    def stop(self):
        common.lighting_stream.set_all_lights_off_stream()
        self._done = True
        print("[TEST:stream] done")

    def is_complete(self):
        return self._done
