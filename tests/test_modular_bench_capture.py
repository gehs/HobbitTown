"""Interactive bench capture for modular dry-run verification.

Runs each modular test one at a time and prompts the operator to record:
- Audio output mapping pass/fail
- Segment light coverage pass/fail

Results are written to modular_dry_run_bench_results.json on the board.
"""

import json
import time

from tests.modular_dry_run import common
from tests.modular_dry_run.sky_test import SkyModuleTest
from tests.modular_dry_run.smial1_test import Smial1ModuleTest
from tests.modular_dry_run.smial2_test import Smial2ModuleTest
from tests.modular_dry_run.smial3_test import Smial3ModuleTest
from tests.modular_dry_run.stream_test import StreamModuleTest


RESULTS_PATH = "modular_dry_run_bench_results.json"


def _wait_for_enter(prompt):
    try:
        input(prompt)
    except Exception:
        # If input is unavailable, continue after a short pause.
        time.sleep(1.0)


def _ask_pass_fail(prompt):
    while True:
        try:
            answer = input(prompt).strip().lower()
        except Exception:
            return "unknown"

        if answer in ("p", "pass"):
            return "pass"
        if answer in ("f", "fail"):
            return "fail"
        if answer in ("u", "unknown", "skip"):
            return "unknown"

        print("Enter P=pass, F=fail, or U=unknown.")


def _run_module(module, tick_delay_s=0.02):
    module.start()
    try:
        while not module.is_complete():
            module.update()
            time.sleep(tick_delay_s)
    finally:
        module.stop()
        common.safe_shutdown()


def _summary_bucket(records, key):
    total = len(records)
    passed = 0
    failed = 0
    unknown = 0
    for rec in records:
        state = rec.get(key, "unknown")
        if state == "pass":
            passed += 1
        elif state == "fail":
            failed += 1
        else:
            unknown += 1
    return {
        "total": total,
        "pass": passed,
        "fail": failed,
        "unknown": unknown,
    }


def main():
    print("[TEST:bench] Modular dry-run bench capture start")
    print("[TEST:bench] Expected audio map:")
    print("  Smial1 output 4 tracks 310/311")
    print("  Smial2 output 2 tracks 312/314")
    print("  Smial3 output 3 tracks 314/316")
    print("  Stream output 4 track 316")
    print("  Sky 4L->out7(idx6) track1, 4R->out8(idx7) track2")
    print("[TEST:bench] Expected ground segments:")
    print("  Smial1: smial_1 + chimney_smial_1")
    print("  Smial2: smial_2 + chimney_smial_2")
    print("  Smial3: smial_3_lower + smial_3_main + smial_3_upper + chimney_smial_3")

    modules = [
        Smial1ModuleTest(track=310, output_number=4, end_track=311),
        Smial2ModuleTest(track=312, output_number=2, end_track=314),
        Smial3ModuleTest(track=314, output_number=3, end_track=316),
        StreamModuleTest(spot_speaker4_track=316),
        SkyModuleTest(exciter_track_left=1, exciter_track_right=2, exciter_output_left=7, exciter_output_right=8),
    ]

    records = []

    common.setup_shared_hardware()
    common.safe_shutdown()

    for module in modules:
        print("\n[TEST:bench] Prepare to run module: %s" % module.name)
        _wait_for_enter("Press Enter when ready...")

        try:
            _run_module(module)
        except Exception as exc:
            print("[TEST:bench] module '%s' crashed: %s" % (module.name, exc))
            records.append(
                {
                    "module": module.name,
                    "audio_mapping": "fail",
                    "segment_coverage": "fail",
                    "notes": "Module crashed: %s" % exc,
                }
            )
            continue

        audio_state = _ask_pass_fail("Audio mapping for %s (P/F/U): " % module.name)
        segment_state = _ask_pass_fail("Segment/light coverage for %s (P/F/U): " % module.name)

        try:
            notes = input("Optional notes for %s (Enter to skip): " % module.name).strip()
        except Exception:
            notes = ""

        records.append(
            {
                "module": module.name,
                "audio_mapping": audio_state,
                "segment_coverage": segment_state,
                "notes": notes,
            }
        )

    common.safe_shutdown()

    report = {
        "test": "modular_dry_run_bench_capture",
        "created_monotonic_s": time.monotonic(),
        "records": records,
        "audio_summary": _summary_bucket(records, "audio_mapping"),
        "segment_summary": _summary_bucket(records, "segment_coverage"),
    }

    try:
        with open(RESULTS_PATH, "w") as fh:
            json.dump(report, fh)
        print("[TEST:bench] wrote report: %s" % RESULTS_PATH)
    except Exception as exc:
        print("[TEST:bench] failed to write report: %s" % exc)

    print("[TEST:bench] report summary:")
    print("  audio   :", report["audio_summary"])
    print("  segments:", report["segment_summary"])
    print("[TEST:bench] done")


if __name__ == "__main__":
    main()
