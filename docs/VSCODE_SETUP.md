# Readme_VSCODE

## Purpose
This document explains how the current VS Code skills in this repository should be used.
It includes:
- What each skill does
- How each skill aligns with project-level Copilot instructions
- The best way to use skills one at a time and in coordinated workflows

For runtime folder boundaries and naming conventions, see `docs/FOLDER_STRUCTURE_AND_NAMING.md`.

## Skill Inventory Summary

### lighting-management
- Primary outcome: Build and manage non-blocking lighting behavior in hardware/lighting_manager.py.
- Main outputs: segment control, presets, runtime updates, safe shutdown.
- Key constraints: no blocking sleeps, use time.monotonic(), scale by config.BRIGHTNESS, handle missing segment IDs safely.

### music-scape
- Primary outcome: Design a themed soundscape plan and example CircuitPython integration snippets.
- Main outputs: docs markdown file in docs/, audio component map, search terms, file/trigger mapping.
- Key constraints: no blocking sleeps, use Adafruit CircuitPython libraries, recommend WAV for short clips and MP3 for longer tracks, tolerate missing files.

### new-hardware
- Primary outcome: Scaffold a new hardware module in hardware/.
- Main outputs: module with init() and non-blocking update().
- Key constraints: import config, avoid time.sleep(), Adafruit CircuitPython only, remind user to update config.py pins.

### new-scene
- Primary outcome: Scaffold a scene orchestrator in logic/ with a timeline/state machine.
- Main outputs: start(), update(), stop() with non-blocking timing.
- Key constraints: use time.monotonic(), update() must return quickly, no sleep, descriptive timing variables.

### tech-manual
- Primary outcome: Produce beginner-friendly wiring and safety documentation in docs/.
- Main outputs: component overview, pin guidance, power/current analysis, protective components, wiring steps.
- Key constraints: educational tone, conservative power guidance, explicit safety rationale.

### ui
- Primary outcome: Create or update local web UI features for diorama control.
- Main outputs: responsive UI changes, route/endpoint updates if needed, comments and docs updates.
- Key constraints: modular architecture, error handling, educational comments, mobile/desktop support.

## Comparison Against Project Copilot Instructions

## Strong Alignment
- CircuitPython focus: all hardware-facing skills align with the requirement to use Adafruit CircuitPython libraries.
- Non-blocking design: new-hardware, new-scene, lighting-management, and music-scape all forbid blocking sleeps and promote monotonic timing.
- Modular architecture: skills are split cleanly by hardware, logic, docs, and UI responsibilities, matching the project architecture.
- Beginner readability: tech-manual and ui explicitly emphasize educational clarity, consistent with project context.

## Partial or Missing Coverage
- Config discipline: project rules require avoiding hardcoded pins and limits via config.py. This is explicit in new-hardware, but not consistently called out in all skills that may touch hardware.
- Hardware safety defaults: project rules call for safe startup states. lighting-management includes this clearly; other skills could reinforce safe initialization requirements.
- Graceful failure behavior: project rules require sensor/read failures to fail safely. lighting-management and ui mention error handling, but other skills could be more explicit.
- Version documentation per commit: project instruction requests version update markdown per commit; skills do not consistently enforce this.

## Net Assessment
The skill set is coherent and mostly aligned with the repository instructions.
The largest improvement opportunity is adding consistent cross-skill checks for config.py usage, safe defaults, and failure handling when hardware logic is generated.

## Best Way to Use Skills In Isolation

## 1) Use one skill for one clear artifact
- lighting-management: when the request is only about runtime lighting behavior.
- new-hardware: when adding one new physical device module.
- new-scene: when creating a scene timeline that orchestrates existing modules.
- music-scape: when designing audio plan/content first.
- tech-manual: when producing wiring and safety docs only.
- ui: when implementing local web controls/views.

## 2) Keep inputs specific
For best results, each isolated request should include:
- Target file path
- Hardware assumptions (pins/power/source)
- Required public functions or endpoints
- Non-blocking requirement and failure behavior

## 3) Run an isolated validation pass
Before moving on, confirm:
- No time.sleep() in hardware/logic update paths
- config.py is used for pins/limits
- Startup state is safe
- Docs are updated where behavior changed

## Skill Trigger Matrix (Short)

| If the request says... | Primary skill | Secondary skill(s) | Typical output |
|---|---|---|---|
| "wire this new component" | tech-manual | new-hardware | docs wiring guide + hardware module scaffold |
| "add support for new sensor/servo/strip" | new-hardware | tech-manual, new-scene | hardware module + optional wiring/safety notes + scene hooks |
| "create a thunderstorm/party/story sequence" | new-scene | lighting-management, music-scape, ui | logic scene timeline + coordinated light/sound + controls |
| "improve light presets/segments/animation" | lighting-management | new-scene, ui | updated lighting manager behavior + trigger points + test controls |
| "design ambient audio/soundscape" | music-scape | new-scene, ui | docs sound plan + trigger mapping + optional UI selectors |
| "add web control/dashboard" | ui | new-scene, lighting-management, new-hardware | responsive UI + routes/endpoints + integration hooks |

Use the primary skill first, then add secondary skills only when the request crosses module boundaries.

## Best Way to Use Skills In Cooperation

## Recommended Collaboration Chains

### Chain A: New physical component end-to-end
1. tech-manual: define safe wiring and power limits.
2. new-hardware: scaffold module based on documented constraints.
3. new-scene: orchestrate behavior using the new module.
4. ui: expose controls/status in local web UI.
5. lighting-management or music-scape (optional): add coordinated effects.

### Chain B: New story scene with light and sound
1. new-scene: scaffold state timeline and transitions.
2. lighting-management: add or tune lighting preset/state hooks.
3. music-scape: map timed audio events and fallback behavior.
4. ui: add scene trigger and status display.
5. tech-manual (optional): add wiring notes if new hardware is introduced.

### Chain C: Lighting-first expansion
1. lighting-management: implement new segments/presets.
2. new-scene: call those presets in timed logic.
3. ui: add testing controls for presets.
4. tech-manual: document any electrical changes.

## Cooperation Rules That Prevent Drift
- Keep ownership boundaries strict:
  - hardware/ = direct device control
  - logic/ = orchestration/state machines
  - docs/ = human instructions and planning artifacts
  - logic/web_logic.py + static UI files = operator interface
- Enforce shared invariants across all generated outputs:
  - Adafruit CircuitPython APIs only
  - Non-blocking update loops
  - config-driven pins/limits
  - Safe startup and safe fallback behavior

## Prompting Templates

### Isolated template
Use skill X only. Create or update file Y. Keep logic non-blocking with monotonic timers, use config.py for all pins/limits, and include graceful error handling plus brief documentation updates.

### Cooperative template
Use skills in this order: A -> B -> C. Each stage should consume outputs of the previous stage. Maintain modular boundaries, avoid blocking calls, keep hardware safe on startup, and update docs for user operation.

## Practical Operating Pattern
- Start with docs-first when electrical risk exists.
- Move to hardware scaffolding next.
- Add scene orchestration after hardware contracts are stable.
- Add UI controls last.
- Finish with a short verification checklist and update docs.

This pattern produces safer changes, clearer ownership, and easier debugging in a mixed hardware/software project.