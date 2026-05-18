import time

from tests.modular_dry_run import Convert_for_Tsunami as cft
from tests.modular_dry_run import common
from tests.modular_dry_run.sky_test import SkyModuleTest
from tests.modular_dry_run.smial1_test import Smial1ModuleTest
from tests.modular_dry_run.smial2_test import Smial2ModuleTest
from tests.modular_dry_run.smial3_test import Smial3ModuleTest
from tests.modular_dry_run.stream_test import StreamModuleTest


# Exciters are wired to Tsunami physical labels 4L and 4R.
# These labels are NOT command bytes; convert them to mono output numbers:
# 4L -> output 7, 4R -> output 8.
EXCITER1_OUTPUT = cft.physical_label_to_output_number("4L")
EXCITER2_OUTPUT = cft.physical_label_to_output_number("4R")


class ModularDryRunSuite:
    """Run each modular dry-run test sequentially with shared safety handling."""

    def __init__(self, inter_module_delay_s=5.0):
        self.modules = [
            Smial1ModuleTest(track=310),
            Smial2ModuleTest(track=312),
            Smial3ModuleTest(track=314),
            StreamModuleTest(spot_speaker4_track=316),
            # Exciter routing uses physical labels 4L/4R -> outputs 7/8.
            SkyModuleTest(
                exciter_track_left=1,
                exciter_track_right=2,
                exciter_output_left=EXCITER1_OUTPUT,
                exciter_output_right=EXCITER2_OUTPUT,
            ),
        ]
        self.current_index = -1
        self.started = False
        self.done = False
        self.results = []
        self.inter_module_delay_s = float(inter_module_delay_s)
        self.waiting_for_next_start_time = None

    def start(self):
        common.setup_shared_hardware()
        common.safe_shutdown()
        self.started = True
        self.done = False
        self.current_index = -1
        self.results = []
        self.waiting_for_next_start_time = None
        print("[TEST:suite] start modular dry run")
        self._start_next()

    def update(self):
        if not self.started or self.done:
            return

        if self.current_index < 0 or self.current_index >= len(self.modules):
            self._finish()
            return

        module = self.modules[self.current_index]
        if module.is_complete():
            if self.waiting_for_next_start_time is None:
                self.results.append({"module": module.name, "status": "PASS"})
                self.waiting_for_next_start_time = time.monotonic()
                print(
                    "[TEST:suite] module '%s' complete; waiting %.1fs before next"
                    % (module.name, self.inter_module_delay_s)
                )
                module.stop()
                return

            if time.monotonic() - self.waiting_for_next_start_time >= self.inter_module_delay_s:
                self._start_next()
            return

        module.update()

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
        self.waiting_for_next_start_time = None
        if self.current_index >= len(self.modules):
            self._finish()
            return
        common.safe_shutdown()
        self.modules[self.current_index].start()

    def _finish(self):
        self.waiting_for_next_start_time = None
        common.safe_shutdown()
        self.done = True
        self.started = False
        print("[TEST:suite] complete")
        print("[TEST:suite] results:", self.results)


def run_modular_dry_run_suite(tick_delay_s=0.02, inter_module_delay_s=5.0):
    suite = ModularDryRunSuite(inter_module_delay_s=inter_module_delay_s)
    suite.start()
    try:
        while not suite.is_complete():
            suite.update()
            time.sleep(tick_delay_s)
    finally:
        common.safe_shutdown()
    return suite.results
