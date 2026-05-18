from tests.modular_dry_run import common


class SkyModuleTest:
    """Dry-run module for sky: exciters plus sky lights."""

    def __init__(
        self,
        exciter_track_left=1,
        exciter_track_right=2,
        exciter_output_left=7,
        exciter_output_right=8,
    ):
        self.name = "Sky"
        self.left_track = int(exciter_track_left)
        self.right_track = int(exciter_track_right)
        self.left_output = int(exciter_output_left)
        self.right_output = int(exciter_output_right)
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
        print(
            "[TEST:sky] start (exciter outputs L=%d R=%d, tracks L=%d R=%d)"
            % (self.left_output, self.right_output, self.left_track, self.right_track)
        )

    def update(self):
        if self._done or self._start is None:
            return

        elapsed = common.monotonic_now() - self._start

        if not self._played_left and elapsed >= 0.2:
            self._played_left = True
            common.play_track_checked(self.left_output, self.left_track, loop=False)

        if not self._played_right and elapsed >= 1.0:
            self._played_right = True
            common.play_track_checked(self.right_output, self.right_track, loop=False)

        if elapsed < 0.2:
            common.lighting_sky.apply_lighting_preset_sky(3)
        elif elapsed < 5.0:
            common.lighting_sky.apply_lighting_preset_sky(5)
            common.lighting_sky.run_lighting_cycle_sky()
        else:
            common.lighting_sky.apply_lighting_preset_sky(4)

        if elapsed >= self.duration_s:
            self.stop()

    def stop(self):
        # Keep exciter verification audio-routed via Tsunami only.
        try:
            if common.audio.uart is not None:
                common.audio.uart.write(common.tsunami_stop_all())
        except Exception as exc:
            print("[TEST:sky] STOP_ALL failed: %s" % exc)
        common.lighting_sky.set_all_lights_off_sky()
        self._done = True
        print("[TEST:sky] done")

    def is_complete(self):
        return self._done
