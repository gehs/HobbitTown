import json
import time
import config
from hardware import lighting_ground

_segment_map = {}
_next_effect = None


def _load_segments():
    global _segment_map
    _segment_map = {}
    try:
        with open('lights.json', 'r') as f:
            data = json.load(f)
            # Load segment definitions from current and legacy strip keys.
            for strip in [
                'strip_ground_effects',
                'strip_water_effects',
                'strip_sky_arc',
                'strip_standard_ws2812b',
                'strip_high_density_sk6812',
            ]:
                for segment in data.get(strip, {}).get('segments', []):
                    _segment_map[segment['id']] = segment['range']
    except Exception as e:
        print('LightingManager: failed to load lights.json', e)
        _segment_map = {}


def init_lighting():
    _load_segments()
    lighting_ground.setup_lighting_ground()
    if lighting_ground.pixels is None:
        print('LightingManager: dry-load mode (lighting module not initialized)')
        return False
    lighting_ground.pixels.fill((0, 0, 0))
    lighting_ground.pixels.show()
    print('LightingManager: initialized, segments', list(_segment_map.keys()))
    return True


def set_segment_color(segment_id, rgb):
    if lighting_ground.pixels is None:
        return
    if segment_id not in _segment_map:
        print(f'LightingManager: unknown segment "{segment_id}"')
        return
    r, g, b = rgb
    r = int(r * config.BRIGHTNESS)
    g = int(g * config.BRIGHTNESS)
    b = int(b * config.BRIGHTNESS)
    start, end = _segment_map[segment_id]
    for i in range(start, end + 1):
        lighting_ground.pixels[i] = (r, g, b)
    lighting_ground.pixels.show()


def apply_preset(preset_name):
    if preset_name == 'sunrise':
        lighting_ground.apply_lighting_preset_ground(3)
    elif preset_name == 'storm':
        lighting_ground.apply_lighting_preset_ground(9)
    elif preset_name == 'party':
        lighting_ground.apply_lighting_preset_ground(5)
    elif preset_name == 'night':
        lighting_ground.apply_lighting_preset_ground(4)
    else:
        print('LightingManager: unknown preset', preset_name)


def update_lighting(current_time=None):
    # Runs the existing lighting cycle for active animated presets
    if current_time is None:
        current_time = time.monotonic()
    lighting_ground.run_lighting_cycle_ground()


def stop_lighting():
    if lighting_ground.pixels is None:
        return
    lighting_ground.pixels.fill((0, 0, 0))
    lighting_ground.pixels.show()
    print('LightingManager: stopped')