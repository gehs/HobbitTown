import json
import time
import neopixel  # type: ignore
import config
from hardware.lighting import pixels, apply_lighting_preset, run_lighting_cycle

_segment_map = {}
_next_effect = None


def _load_segments():
    global _segment_map
    try:
        with open('lights.json', 'r') as f:
            data = json.load(f)
            # merge segments for all strips
            for strip in ['strip_standard_ws2812b', 'strip_high_density_sk6812']:
                for segment in data.get(strip, {}).get('segments', []):
                    _segment_map[segment['id']] = segment['range']
    except Exception as e:
        print('LightingManager: failed to load lights.json', e)
        _segment_map = {}


def init_lighting():
    global pixels
    _load_segments()
    if not pixels:
        # Should be configured by hardware/lighting setup
        raise RuntimeError('Lighting module not yet initialized')
    pixels.fill((0, 0, 0))
    pixels.show()
    print('LightingManager: initialized, segments', list(_segment_map.keys()))


def set_segment_color(segment_id, rgb):
    if segment_id not in _segment_map:
        print(f'LightingManager: unknown segment "{segment_id}"')
        return
    r, g, b = rgb
    r = int(r * config.BRIGHTNESS)
    g = int(g * config.BRIGHTNESS)
    b = int(b * config.BRIGHTNESS)
    start, end = _segment_map[segment_id]
    for i in range(start, end + 1):
        pixels[i] = (r, g, b)
    pixels.show()


def apply_preset(preset_name):
    if preset_name == 'sunrise':
        apply_lighting_preset(3)
    elif preset_name == 'storm':
        apply_lighting_preset(9)
    elif preset_name == 'party':
        apply_lighting_preset(5)
    elif preset_name == 'night':
        apply_lighting_preset(4)
    else:
        print('LightingManager: unknown preset', preset_name)


def update_lighting(current_time=None):
    # Runs the existing lighting cycle for active animated presets
    if current_time is None:
        current_time = time.monotonic()
    run_lighting_cycle()


def stop_lighting():
    pixels.fill((0, 0, 0))
    pixels.show()
    print('LightingManager: stopped')