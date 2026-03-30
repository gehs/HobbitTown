import json
import time
import config
import hardware.lighting as lighting

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
    _load_segments()
    if lighting.pixels is None:
        print('LightingManager: dry-load mode (lighting module not initialized)')
        return False
    lighting.pixels.fill((0, 0, 0))
    lighting.pixels.show()
    print('LightingManager: initialized, segments', list(_segment_map.keys()))
    return True


def set_segment_color(segment_id, rgb):
    if lighting.pixels is None:
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
        lighting.pixels[i] = (r, g, b)
    lighting.pixels.show()


def apply_preset(preset_name):
    if preset_name == 'sunrise':
        lighting.apply_lighting_preset(3)
    elif preset_name == 'storm':
        lighting.apply_lighting_preset(9)
    elif preset_name == 'party':
        lighting.apply_lighting_preset(5)
    elif preset_name == 'night':
        lighting.apply_lighting_preset(4)
    else:
        print('LightingManager: unknown preset', preset_name)


def update_lighting(current_time=None):
    # Runs the existing lighting cycle for active animated presets
    if current_time is None:
        current_time = time.monotonic()
    lighting.run_lighting_cycle()


def stop_lighting():
    if lighting.pixels is None:
        return
    lighting.pixels.fill((0, 0, 0))
    lighting.pixels.show()
    print('LightingManager: stopped')