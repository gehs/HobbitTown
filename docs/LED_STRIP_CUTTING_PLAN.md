# LED Strip Cutting Plan

## Overview

Two independent LED strips drive the diorama. This guide lists every physical cut point, segment length, and current budget for both.

- **Strip 1 — Sky Arc** (GPIO 2): 3 chained strip sections, 129 pixels, 48 inches
- **Strip 2 — Ground Effects** (GPIO 4): 17 segments, 153 pixels, WS2812B only

Source of truth: `lights.json`

---

## Addressable Reconnect Rules (Read Before Cutting)

When you cut addressable LEDs, reconnect in the same data order.

For this project, use an SN74AHCT125N level shifter on each ESP32 LED data output before the first strip DIN.
- GPIO 2 or GPIO 4 from the ESP32 is 3.3V logic.
- WS2812B and SK6812 strips are powered from 5V and behave more reliably with a 5V logic-level data signal.
- Recommended chain: ESP32 GPIO -> SN74AHCT125N -> 470 ohm resistor -> first DIN.

Always preserve this pathway:
- Controller GPIO -> DIN of segment 1
- DOUT of segment N -> DIN of segment N+1
- Last segment DOUT -> end (no return loop)

Pad-by-pad solder rule for each reconnect:
1. 5V pad -> 5V pad (red wire)
2. GND pad -> GND pad (black wire)
3. DOUT (upstream segment) -> DIN (next segment) (data wire)

Never do these:
- DIN -> DIN
- DOUT -> DOUT
- Reverse arrow direction

Beginner bench method:
1. Cut one segment only.
2. Label both ends immediately: DIN side and DOUT side.
3. Solder 3 jumper wires (5V/GND/DATA).
4. Power and run a quick test before cutting the next segment.
5. Repeat one segment at a time.

---

## Strip 1: Sky Arc (GPIO 2)

The sky arc is **three physically distinct strips** chained in data order. Dawn and Dusk are WS2812B (60px/m). Noon is SK6812 RGBW (144px/m) — a different strip type purchased separately. There are **2 solder joints** between the three pieces.

### Cut / Chain Points

| # | Segment | Strip type | Pixels | Physical length | Pixel range | Solder joint after pixel |
|---|---|---|---:|---|---|---|
| 1 | Dawn Sky Gradient | WS2812B 60px/m | 19 | 12" | 0–18 | 18 |
| 2 | Noon Sky Peak | SK6812 RGBW 144px/m | 91 | 24" | 19–109 | 109 |
| 3 | Dusk Sky Gradient | WS2812B 60px/m | 19 | 12" | 110–128 | END |
| | **Total** | | **129** | **48"** | | |

> Dawn and Dusk WS2812B sections can be cut from the same 60px/m roll. Noon SK6812 RGBW must be purchased separately at 144px/m density.

### Sky Arc Current Budget

| Segment | Strip type | Pixels | Max @ 60/80 mA/px | @ BRIGHTNESS 0.5 | Typical |
|---|---|---:|---:|---:|---|
| Dawn Sky | WS2812B | 19 | 1.14 A | 0.57 A | 0.15–0.35 A |
| Noon Sky (sun/moon peak) | SK6812 RGBW | 91 | 7.28 A | 3.64 A | 1.50–2.80 A |
| Dusk Sky | WS2812B | 19 | 1.14 A | 0.57 A | 0.15–0.35 A |
| **Total Sky Arc** | | **129** | **9.56 A** | **4.78 A** | **1.80–3.50 A** |

> SK6812 RGBW worst-case is 80 mA/pixel (all 4 channels full). In normal use the white channel only fires; realistic draw is 20–40 mA/pixel.

### Sky Arc Wiring Steps

1. Purchase strips: one 12" WS2812B (60px/m), one 24" SK6812 RGBW (144px/m), one 12" WS2812B (60px/m).
2. Confirm DIN direction arrows on all three before soldering.
3. Solder DOUT of Dawn WS2812B → DIN of Noon SK6812 (joint at pixel 18/19).
4. Solder DOUT of Noon SK6812 → DIN of Dusk WS2812B (joint at pixel 109/110).
5. Route GPIO 2 data line → SN74AHCT125N input.
6. Route SN74AHCT125N output → 470 Ω resistor → DIN of Dawn strip.
7. Power the SN74AHCT125N from 5V and GND; tie the selected OE pin low.
8. Power all three from the 5V bus; add 1000 µF capacitor at the start of each strip section.

---

## Strip 2: Ground Effects (GPIO 4)

Single continuous WS2812B 60px/m strip, routed left-to-right by x-coordinate through the diorama. **17 segments, 16 cut points.** After cutting, each piece is placed at its physical location and the data line is re-joined with short jumper wires.

### Cut Sequence

Count pixels from the DIN end. Cut after the last pixel of each segment.

| # | Segment | Pixels | Pixel range | Cut after pixel | Physical location |
|---|---|---:|---|---|---|
| 1 | Bag End | 3 | 0–2 | 2 | x=9, y=10 — window interior |
| 2 | Smial 2 | 3 | 3–5 | 5 | x=15, y=16 — window interior |
| 3 | The Bridge | 14 | 6–19 | 19 | x=23–32, y=8 — path surface |
| 4 | The River | 36 | 20–55 | 55 | x=25–32, y=0–24 — water channel |
| 5 | Great Smial Lower Window | 2 | 56–57 | 57 | x=42, y=9 — window |
| 6 | Great Smial Main Entrance | 5 | 58–62 | 62 | x=36, y=12 — entrance |
| 7 | Great Smial Upper Window | 2 | 63–64 | 64 | x=34, y=19 — window |
| 8 | Party Tree | 15 | 65–79 | 79 | x=45, y=21 — branches |
| 9 | Server Room Edge | 16 | 80–95 | 95 | x=36–48, y=12–24 — perimeter |
| 9a | etc | 4 | 96-99 | 99 | tbd |
| 10 | Path Lanterns | 6 | 100–105 | 105 | x=20–23, y=8 — bridge approach |
| 11 | Fireflies | 12 | 106–117 | 117 | scattered x=12–25, y=4–14 — meadow |
| 12 | Star Field | 10 | 118–127 | 127 | fiber optics bundle input |
| 13 | Storm Clouds | 10 | 128–137 | 137 | x=42–48, y>24 — cloud cutout |
| 14 | Bag End Chimney | 2 | 138–139 | 139 | x=9, y=10 — upward into chimney |
| 15 | Smial 2 Chimney | 2 | 140–141 | 141 | x=15, y=16 — upward into chimney |
| 16 | Great Smial Chimney | 3 | 142–144 | 144 | x=36, y=12 — upward into chimney |
| 17 | Bridge Mist | 8 | 145–152 | END | x=23–32, y=8 — under deck, upward |
| | **Total** | **153** | | | |

### Routing Notes

- **Segments 14–16 (chimneys)** double back to x=9, 15, 36 — route the data jumper wire through the torsion box wiring channel rather than across the surface.
- **Segment 12 (Star Field)** has no surface x,y position — terminate the strip at the fiber optics bundle input, wherever that is mounted in the ceiling void.
- **Segment 11 (Fireflies)** uses individually scattered naked LEDs; after cutting, split the 12-pixel piece into single pixels or small clusters and place them across the meadow area.
- **Segment 17 (Bridge Mist)** mounts under the bridge deck facing upward — allow 2–3" of slack wire on the DIN side before securing.

### Ground Effects Current Budget

WS2812B worst-case: 60 mA/pixel. @ BRIGHTNESS 0.5: 30 mA/pixel.

| Segment | Pixels | Max @ 60 mA/px | @ BRIGHTNESS 0.5 | Typical duty |
|---|---:|---:|---:|---|
| Bag End | 3 | 0.18 A | 0.09 A | ~0.05 A warm glow |
| Smial 2 | 3 | 0.18 A | 0.09 A | ~0.05 A warm glow |
| The Bridge | 14 | 0.84 A | 0.42 A | ~0.15 A path dim |
| The River | 36 | 2.16 A | 1.08 A | ~0.45 A shimmer |
| Great Smial Lower Window | 2 | 0.12 A | 0.06 A | ~0.04 A |
| Great Smial Main Entrance | 5 | 0.30 A | 0.15 A | ~0.08 A |
| Great Smial Upper Window | 2 | 0.12 A | 0.06 A | ~0.04 A |
| Party Tree | 15 | 0.90 A | 0.45 A | ~0.25 A lanterns |
| Server Room Edge | 20 | 1.20 A | 0.60 A | ~0.20 A ambient |
| etc | 4 | 0.36 A | 0.12 A | ~0.08 A |
| Path Lanterns | 6 | 0.36 A | 0.18 A | ~0.10 A amber |
| Fireflies | 12 | 0.72 A | 0.36 A | ~0.08 A twinkle |
| Star Field | 10 | 0.60 A | 0.30 A | ~0.10 A sparkle |
| Storm Clouds | 10 | 0.60 A | 0.30 A | ~0.40 A peak strobe |
| Bag End Chimney | 2 | 0.12 A | 0.06 A | ~0.04 A flicker |
| Smial 2 Chimney | 2 | 0.12 A | 0.06 A | ~0.04 A flicker |
| Great Smial Chimney | 3 | 0.18 A | 0.09 A | ~0.06 A flicker |
| Bridge Mist | 8 | 0.48 A | 0.24 A | ~0.12 A cool wash |
| **Total Ground** | **153** | **9.18 A** | **4.59 A** | **~2.25 A typical** |

### Ground Effects Wiring Steps

1. Mark DIN end of a full WS2812B 60px/m roll with tape before making any cuts.
2. Working from the DIN end, count and cut each segment in the order listed in the table above.
3. Label each cut piece immediately with its segment name and pixel range.
4. Place all pieces at their physical x,y locations in the diorama.
5. Solder data jumper wires: DOUT of each piece → DIN of next in sequence.
6. Route GPIO 4 → 470 Ω resistor → DIN of segment 1 (Bag End).
7. Power injection: add a 1000 µF capacitor at the strip DIN start and a second injection point at pixel 80 (Server Room) halfway through.

### Reconnect Pathway Checklist (Ground Effects)

- Segment 1 DIN receives controller data from the GPIO4 resistor path.
- Each segment DOUT is wired to the next segment DIN.
- Every jumper includes 5V and GND continuity (not just DATA).
- DATA wires are kept short and routed away from high-current motor/relay wiring.
- After every 3 to 4 reconnect joints, run a quick color test before continuing.

---

## Power Summary

| Strip | Pixels | Max draw | @ BRIGHTNESS 0.5 | Design target |
|---|---:|---:|---:|---|
| Sky Arc — GPIO 2 | 129 | 9.56 A | 4.78 A | 6 A minimum available |
| Ground Effects — GPIO 4 | 153 | 9.18 A | 4.59 A | 6 A minimum available |
| **Combined diorama total** | **282** | **18.74 A** | **9.37 A** | **Mean Well LRS-100-5 (18 A @ 5 V)** |

> The LRS-100-5 comfortably covers both strips at BRIGHTNESS 0.5 with headroom for servos, fogger relay, and audio amplifiers. Do not set BRIGHTNESS above 0.6 without measuring actual draw first.
