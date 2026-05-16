from tests.modular_dry_run import common


class SkyModuleTest:
    """Dry-run module for sky: exciters plus sky lights."""

    def __init__(self, exciter_track_left=401, exciter_track_right=502):
        self.name = "Sky"
        self.left_track = int(exciter_track_left)
        self.right_track = int(exciter_track_right)
        self.duration_s = 8.0
        self._start = None
        self._done = False
        self._played_left = False
        self._played_right = False

    def start(self):
        self._done = False
        self._played_left = False
        self._played_right = False
        self._start = common.monotonic_now()
        print("[TEST:sky] start")

    def update(self):
        if self._done or self._start is None:
            return

        elapsed = common.monotonic_now() - self._start

        if not self._played_left and elapsed >= 0.2:
            self._played_left = True
            common.play_track_checked(5, self.left_track, loop=False)

        if not self._played_right and elapsed >= 1.0:
            self._played_right = True
            common.play_track_checked(6, self.right_track, loop=False)

        if elapsed < 0.2:
            common.lighting_sky.apply_lighting_preset_sky(3)
        elif elapsed < 5.0:
            common.lighting_sky.apply_lighting_preset_sky(5)
            common.lighting_sky.run_lighting_cycle_sky()
        else:
            common.lighting_sky.apply_lighting_preset_sky(4)

        # Physical exciter pulse confirmation path for PCA9685 channels 12/13.
        common.pulse_exciter_channels(elapsed)

        if elapsed >= self.duration_s:
            self.stop()

    def stop(self):
        common.motion.set_speaker(12, 0)
        common.motion.set_speaker(13, 0)
        common.lighting_sky.set_all_lights_off_sky()
        self._done = True
        print("[TEST:sky] done")

    def is_complete(self):
        return self._done
