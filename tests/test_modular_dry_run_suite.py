"""Launcher for modular dry-run suite.

Modules executed:
1. Smial1
2. Smial2
3. Smial3
4. Stream (Spot Speaker4 + Stream lights)
5. Sky (Exciters + Sky lights)
"""

from tests.modular_dry_run.suite import run_modular_dry_run_suite


if __name__ == "__main__":
    results = run_modular_dry_run_suite(tick_delay_s=0.02)
    print("[TEST:launcher] done")
    print(results)
