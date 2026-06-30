"""
Comprehensive dry-run launcher.

Per-user mapping:
- Smial 1 spot speaker track: 310
- Smial 2 spot speaker track: 312
- Smial 3 spot speaker track: 314
- Exciter test tracks: 001 and 002
"""

from logic.certification_dry_run_scene import run_comprehensive_dry_run


if __name__ == "__main__":
    results = run_comprehensive_dry_run(
        smial_tracks=(310, 312, 314),
        exciter_tracks=(1, 2),
        tick_delay_s=0.02,
    )
    print("DryRunLauncher: finished")
    print(results)
