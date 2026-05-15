---
name: music-scape
description: Design soundscapes, audio asset plans, speaker routing concepts, trigger mappings, and non-blocking scene-audio behavior for the HobbitTown diorama. Use when asked for ambient audio, music loops, sound effects, asset organization, sample search terms, sound timing, speaker or exciter assignment, event-triggered sound, or audio integration with scenes such as storms, markets, parties, doors, creatures, streams, or weather effects. For Tsunami Super WAV Trigger serial commands, gain encoding, track-number encoding, SD card rules, mono output indexes, or hex debugging, use tsunami-audio-control.
---

# Music Scape

## Goal

Help design and plan audio for HobbitTown in a way that is scene-aware, storage-aware, hardware-aware, and safe for non-blocking CircuitPython integration.

This skill focuses on creative and architectural soundscape planning:

- mood and intent
- ambient beds
- one-shot effects
- loops
- triggered sounds
- asset reuse
- speaker and exciter placement concepts
- scene synchronization points
- implementation handoff notes

This skill should not own byte-level Tsunami serial protocol details. When implementation requires Tsunami Super WAV Trigger control, use the `tsunami-audio-control` skill.

## Implementation Boundary

Use this skill for soundscape planning and audio behavior design.

Use `tsunami-audio-control` when the user asks to:

- implement Tsunami Super WAV Trigger serial commands
- encode track numbers
- encode gain or volume values
- encode fade durations
- generate or debug hex bytes
- map user-facing mono outputs to Tsunami serial output indexes
- define SD card WAV rules for Tsunami
- create CircuitPython helpers for Tsunami command framing
- review Tsunami-specific playback code

Do not duplicate Tsunami serial protocol details in this skill. Instead, produce a clear handoff plan that `tsunami-audio-control` can implement.

## Typical Outputs

Depending on the request, produce one or more of the following:

- A `docs/soundscape_<name>.md` plan.
- An audio asset list with filenames, approximate duration, format intent, and reuse notes.
- A trigger map connecting scene events to sounds.
- A speaker or exciter routing concept.
- A non-blocking timing plan for scene integration.
- Sample search terms with licensing reminders.
- A handoff table for `tsunami-audio-control` when Tsunami implementation is needed.
- Notes about required audio hardware, libraries, and `requirements.txt` changes when relevant.

Avoid generating low-level Tsunami serial code here. Delegate that to `tsunami-audio-control`.

## Workflow

1. Identify the scene mood, location, narrative purpose, and key events.
2. Separate the soundscape into:
   - ambient beds
   - loops
   - one-shot effects
   - random occasional effects
   - event-triggered sounds
   - transition sounds
3. Identify available hardware before assigning outputs:
   - ESP32-S3 board
   - Tsunami Super WAV Trigger or other playback device
   - speakers
   - exciters
   - amplifiers
   - SD card or flash storage
   - available pins and serial connections
4. Use Spot Speakers for localized, short, directional, or hidden sounds, typically under 10 seconds.
5. Use Exciters for resonance, hidden vibration, structure-coupled sound, bass-like depth, or effects that should feel embedded in scenery.
6. Reuse audio assets across soundscapes when practical to reduce storage needs.
7. Give practical sample search terms, but do not imply licensing is solved. Remind the user to use properly licensed audio.
8. Map each component to a proposed filename or synthesis method, for example:
   - `001_thunder_close.wav`
   - `002_market_murmur_loop.wav`
   - `003_door_creak.wav`
   - generated wind/noise layer
9. Connect sounds to scene events with non-blocking timing, for example:
   - lightning flash first
   - thunder after elapsed delay
   - rain bed fades in before storm peak
   - creature sound triggered after motion begins
10. Make missing audio files non-fatal. The program should print a warning and continue safely.
11. When implementation will use Tsunami, prepare a handoff plan for `tsunami-audio-control` instead of encoding serial bytes directly.

## Known Synchronization Points

The following non-sound effects may exist in HobbitTown scenes and can be referenced as triggers or synchronization points:

- Door opening or closing
- Lighting within structures
- Lighting across the sky
- Lighting within the stream
- Smoke from chimneys
- Fog from the stream
- Servo or motion events
- Sensor input events
- Scene start, peak, transition, and stop events

Do not treat these as audio layers. Reference them only when they help synchronize sound.

## CircuitPython Planning Rules

When describing runtime behavior:

- Do not use `time.sleep()` in runtime scene or hardware modules.
- Use `time.monotonic()` for timing and delayed triggers.
- Design sound events so they can be called from a fast main loop.
- Avoid blocking playback logic.
- Missing files, missing hardware, or unavailable audio devices should fail safely.
- Include imports at the top of generated files when code is requested.
- If adding a new library, check `/lib` when possible and update `requirements.txt`.

When code requires Tsunami-specific serial commands, hand off to `tsunami-audio-control`.

## Audio Format Guidance

For creative planning, describe the audio role first:

- short one-shot
- loop
- long ambience
- random accent
- transition
- synchronized event sound

Do not assume MP3 playback unless the user is using a device that supports MP3.

For Tsunami playback, defer file format rules to `tsunami-audio-control`.

In soundscape plans, use a neutral “format intent” such as:

- short WAV one-shot
- loopable WAV ambience
- generated noise layer
- external source TBD

## Handoff to Tsunami Audio Control

When a soundscape will be implemented using the Tsunami Super WAV Trigger, include a handoff table like this:

| Sound role | Proposed filename | Behavior | Trigger | Timing | Routing intent | Mix/gain intent | Notes |
|---|---|---|---|---|---|---|---|
| Rain bed | `001_rain_loop.wav` | loop | scene start | immediate | ambient output | quiet under other sounds | fade in/out |
| Close thunder | `002_thunder_close.wav` | one-shot | lightning flash | delay 0.6-1.5 sec | localized speaker | loud but not clipping | choose random delay |
| Door creak | `003_door_creak.wav` | one-shot | door servo starts | immediate | house spot speaker | medium | sync to motion |

Leave exact Tsunami track-number encoding, output index conversion, gain byte encoding, fade command construction, and serial hex generation to `tsunami-audio-control`.

## Documentation Template

When asked to create a soundscape document, use this structure:

```markdown
# Soundscape: <name>

## Intent

What the user should feel, notice, or understand from the soundscape.

## Scene Context

Where the soundscape occurs, what is happening physically, and what non-audio effects may synchronize with it.

## Audio Layers

| Layer | File or method | Format intent | Loop? | Trigger | Approx. duration | Notes |
|---|---|---|---|---|---:|---|

## Hardware Routing Concept

Speaker and exciter assignment assumptions.

Examples:

- Spot 1: localized house or door sound
- Spot 2: creature or market sound
- Exciter 1: structure resonance, low rumble, or embedded ambience
- Ambient output: rain, wind, stream, or crowd bed

## Trigger Map

| Scene event | Audio response | Timing relationship | Fallback behavior |
|---|---|---|---|

## Asset Search Terms

Search terms and licensing reminders.

## Reuse Opportunities

Existing or reusable sounds across other scenes.

## Implementation Handoff

If using Tsunami, include the handoff table for `tsunami-audio-control`.

If using another playback device, identify what implementation details still need confirmation.

## CircuitPython Integration Notes

Non-blocking timing, fallback behavior, and integration points.
```

## Sound Design Heuristics

Use layered sound sparingly. A small diorama can feel more realistic with fewer, well-timed sounds than with constant noise.

Prefer:

- quiet ambient beds
- occasional accents
- physical synchronization
- short localized effects
- asset reuse
- clear scene transitions

Avoid:

- too many simultaneous full-volume layers
- sounds that compete with each other
- long files when a short loop will work
- requiring exact timing when a natural random range feels better
- making sound failure stop the whole scene

## Common Mistakes to Avoid

- Do not make this skill responsible for Tsunami byte-level serial protocol.
- Do not assume MP3 playback for Tsunami.
- Do not overfill a scene with too many simultaneous sounds.
- Do not create blocking timing logic.
- Do not ignore storage constraints.
- Do not assign outputs before identifying the actual hardware.
- Do not imply sample licensing is solved by finding a search term.
- Do not make missing audio files fatal.
- Do not include lighting, smoke, fog, or motion as audio layers; use them only as synchronization points.