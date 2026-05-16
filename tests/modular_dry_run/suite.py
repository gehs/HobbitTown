import time

from tests.modular_dry_run import common
from tests.modular_dry_run.sky_test import SkyModuleTest
from tests.modular_dry_run.smial1_test import Smial1ModuleTest
from tests.modular_dry_run.smial2_test import Smial2ModuleTest
from tests.modular_dry_run.smial3_test import Smial3ModuleTest
from tests.modular_dry_run.stream_test import StreamModuleTest


class ModularDryRunSuite:
    """Run each modular dry-run test sequentially with shared safety handling."""

    def __init__(self):
        self.modules = [
            Smial1ModuleTest(track=11),
            Smial2ModuleTest(track=112),
            Smial3ModuleTest(track=213),
            StreamModuleTest(spot_speaker4_track=314),
            SkyModuleTest(exciter_track_left=401, exciter_track_right=502),
        ]
        self.current_index = -1
        self.started = False
        self.done = False
        self.results = []

    def start(self):
        common.setup_shared_hardware()
        common.safe_shutdown()
        self.started = True
        self.done = False
        self.current_index = -1
        self.results = []
        print("[TEST:suite] start modular dry run")
        self._start_next()

    def update(self):
        if not self.started or self.done:
            return

        if self.current_index < 0 or self.current_index >= len(self.modules):
            self._finish()
            return

        module = self.modules[self.current_index]
        module.update()

        if module.is_complete():
            self.results.append({"module": module.name, "status": "PASS"})
            self._start_next()

    def is_complete(self):
        return self.done

    def stop(self):
        if 0 <= self.current_index < len(self.modules):
            self.modules[self.current_index].stop()
        common.safe_shutdown()
        self.done = True
        self.started = False
        print("[TEST:suite] stopped")

    def _start_next(self):
        self.current_index += 1
        if self.current_index >= len(self.modules):
            self._finish()
            return
        common.safe_shutdown()
        self.modules[self.current_index].start()

    def _finish(self):
        common.safe_shutdown()
        self.done = True
        self.started = False
        print("[TEST:suite] complete")
        print("[TEST:suite] results:", self.results)


def run_modular_dry_run_suite(tick_delay_s=0.02):
    suite = ModularDryRunSuite()
    suite.start()
    try:
        while not suite.is_complete():
            suite.update()
            time.sleep(tick_delay_s)
    finally:
        common.safe_shutdown()
    return suite.results
