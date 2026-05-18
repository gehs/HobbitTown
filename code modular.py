"""
Modular dry-run launcher.

This entrypoint executes the modular test suite sequentially with a delay
between each module to allow hardware state transitions and operator checks.
"""

from tests.modular_dry_run.suite import run_modular_dry_run_suite


if __name__ == "__main__":
    results = run_modular_dry_run_suite(
        tick_delay_s=0.02,
        inter_module_delay_s=5.0,
    )
    print("ModularDryRunLauncher: finished")
    print(results)
