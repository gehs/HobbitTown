"""
web_logic.py – Lightweight HTTP server for HobbitTown diorama UI.

Serves two HTML pages (Events + Test Console) and handles API endpoints
to control lighting, audio, motion, atmosphere, and test scenes.
Uses raw sockets via CircuitPython's socketpool – no external web framework needed.
"""
import wifi  # type: ignore
import socketpool  # type: ignore
import mdns  # type: ignore
import config

# ── WiFi / Network credentials ──────────────────────────────────
# Loaded from secrets.py – edit that file with your actual WiFi credentials
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD  # type: ignore
except ImportError:
    print("ERROR: secrets.py not found. Create it with WIFI_SSID and WIFI_PASSWORD.")
    WIFI_SSID = ""
    WIFI_PASSWORD = ""

DEVICE_HOSTNAME = "hobbittown"

# ── Module-level state ───────────────────────────────────────────
pool = None
server_socket = None

# ── HTML page cache (loaded once at startup to save memory) ──────
_page_index = ""
_page_test = ""


# ================================================================
#  Setup
# ================================================================

def setup_web():
    """Connect WiFi, start mDNS, open listening socket on port 80."""
    global pool, server_socket, _page_index, _page_test

    if not getattr(config, "ENABLE_WEB", True):
        print("Web: disabled in config.py")
        return

    if not WIFI_SSID or WIFI_SSID == "YOUR_WIFI_SSID":
        print("WiFi SKIPPED: Update secrets.py with your real WiFi credentials.")
        return

    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print("WiFi connected. IP:", wifi.radio.ipv4_address)

    pool = socketpool.SocketPool(wifi.radio)

    # Advertise via mDNS so the user can reach http://hobbittown.local
    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = DEVICE_HOSTNAME
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
    print("mDNS ready at http://" + DEVICE_HOSTNAME + ".local")

    # Pre-load HTML pages into RAM so we don't hit the filesystem on every request
    _page_index = _load_file("static/index.html")
    _page_test = _load_file("static/test.html")

    # Open a TCP listening socket (non-blocking so it won't stall the main loop)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind(("0.0.0.0", 80))
    server_socket.listen(2)
    print("Web server listening on port 80")


def _load_file(path):
    """Read a file from the filesystem and return its contents as a string."""
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        print("web_logic: could not load", path)
        return "<html><body><h1>File not found</h1></body></html>"


# ================================================================
#  Main request handler – called every main-loop iteration
# ================================================================

def run_web_sync():
    """Non-blocking: accept one pending HTTP request and respond."""
    if server_socket is None:
        return

    try:
        client, _addr = server_socket.accept()
    except OSError:
        # No pending connection – that's normal in non-blocking mode
        return

    try:
        client.settimeout(2)
        buf = bytearray(1024)
        numbytes = client.recv_into(buf)
        if numbytes == 0:
            client.close()
            return
        request = buf[:numbytes].decode("utf-8")
    except Exception:
        try:
            client.close()
        except Exception:
            pass
        return

    # Parse the first line: "GET /path?query HTTP/1.1"
    first_line = request.split("\r\n")[0]
    parts = first_line.split(" ")
    if len(parts) < 2:
        _send_response(client, 400, "Bad Request")
        return

    method = parts[0]
    raw_path = parts[1]

    # Split path and query string
    if "?" in raw_path:
        path, query_string = raw_path.split("?", 1)
    else:
        path, query_string = raw_path, ""

    params = _parse_query(query_string)

    # Route the request
    _route_request(client, method, path, params)


# ================================================================
#  Routing
# ================================================================

def _route_request(client, method, path, params):
    """Dispatch the request to the correct handler based on URL path."""

    # ── HTML pages ──
    if path == "/" or path == "/index.html":
        _send_html(client, _page_index)
    elif path == "/test" or path == "/test.html":
        _send_html(client, _page_test)

    # ── Lighting preset ──
    elif path == "/api/preset":
        _handle_preset(client, params)

    # ── High-level events (party, dragon, fog, ambience) ──
    elif path == "/api/event":
        _handle_event(client, params)

    # ── Scene triggers ──
    elif path == "/api/scene":
        _handle_scene(client, params)

    # ── Test: individual door/servo ──
    elif path == "/api/test/door":
        _handle_test_door(client, params)

    # ── Test: mister control ──
    elif path == "/api/test/mister":
        _handle_test_mister(client, params)

    # ── Test: blower control ──
    elif path == "/api/test/blower":
        _handle_test_blower(client, params)

    # ── Test: speaker channel ──
    elif path == "/api/test/speaker":
        _handle_test_speaker(client, params)

    # ── Test: audio playback ──
    elif path == "/api/test/audio":
        _handle_test_audio(client, params)

    # ── Test: LED segment color ──
    elif path == "/api/test/segment":
        _handle_test_segment(client, params)

    # ── Test: fogger on/off ──
    elif path == "/api/test/fog":
        _handle_test_fog(client, params)

    # ── Test: scene start/stop ──
    elif path == "/api/test/scene/start":
        _handle_test_scene_start(client)
    elif path == "/api/test/scene/stop":
        _handle_test_scene_stop(client)

    # ── Test: reset all hardware ──
    elif path == "/api/test/reset":
        _handle_test_reset(client)

    else:
        _send_response(client, 404, "Not Found")


# ================================================================
#  API Handlers
# ================================================================

def _handle_preset(client, params):
    """Apply a lighting preset by numeric ID."""
    import hardware.lighting as lighting
    preset_id = _int_param(params, "id", -1)
    if preset_id < 0:
        _send_response(client, 400, "Missing preset id")
        return
    lighting.apply_lighting_preset(preset_id)
    _send_response(client, 200, "Preset " + str(preset_id))


def _handle_event(client, params):
    """Trigger a named event: party, dragon, fog, daytime, nighttime."""
    import hardware.audio as audio
    import hardware.atmosphere as atmosphere
    name = params.get("name", "")
    if name == "party":
        import hardware.lighting as lighting
        lighting.apply_lighting_preset(5)
        audio.play_party_music()
        _send_response(client, 200, "Party mode!")
    elif name == "dragon":
        audio.play_dragon_event()
        _send_response(client, 200, "Dragon roar!")
    elif name == "fog":
        # Short fog pulse: relay ON for config.FOG_DURATION via atmosphere cycle
        if hasattr(atmosphere, "fogger_relay") and atmosphere.fogger_relay:
            atmosphere.fogger_relay.value = False  # Relay ON
            atmosphere.is_fogging = True
            import time
            atmosphere.last_fog_time = time.monotonic()
        _send_response(client, 200, "Fog pulse")
    elif name == "daytime":
        audio.play_daytime()
        _send_response(client, 200, "Daytime ambience")
    elif name == "nighttime":
        audio.play_nighttime()
        _send_response(client, 200, "Nighttime ambience")
    else:
        _send_response(client, 400, "Unknown event: " + name)


def _handle_scene(client, params):
    """Start or stop a named scene."""
    from logic.test_scene import smial_test
    name = params.get("name", "")
    if name == "smial_test":
        smial_test.start()
        _send_response(client, 200, "Smial test started")
    elif name == "stop":
        smial_test.stop()
        _send_response(client, 200, "Scene stopped")
    else:
        _send_response(client, 400, "Unknown scene: " + name)


# ── Test handlers: individual component isolation ────────────────

def _handle_test_door(client, params):
    """Set a single door servo to a given angle."""
    import hardware.motion as motion
    door_id = _int_param(params, "id", -1)
    angle = _int_param(params, "angle", -1)
    if door_id < 1 or door_id > 3:
        _send_response(client, 400, "Door id must be 1-3")
        return
    if angle < 0 or angle > 180:
        _send_response(client, 400, "Angle must be 0-180")
        return
    motion.set_door(door_id, angle)
    _send_response(client, 200, "Door " + str(door_id) + " -> " + str(angle))


def _handle_test_mister(client, params):
    """Set a single mister to a PWM value (0-255)."""
    import hardware.motion as motion
    mister_id = _int_param(params, "id", -1)
    value = _int_param(params, "value", -1)
    if mister_id < 1 or mister_id > 4:
        _send_response(client, 400, "Mister id must be 1-4")
        return
    if value < 0 or value > 255:
        _send_response(client, 400, "Value must be 0-255")
        return
    motion.set_mister(mister_id, value)
    _send_response(client, 200, "Mister " + str(mister_id) + " -> " + str(value))


def _handle_test_blower(client, params):
    """Set a single blower to a PWM value (0-255)."""
    import hardware.motion as motion
    blower_id = _int_param(params, "id", -1)
    value = _int_param(params, "value", -1)
    if blower_id < 1 or blower_id > 3:
        _send_response(client, 400, "Blower id must be 1-3")
        return
    if value < 0 or value > 255:
        _send_response(client, 400, "Value must be 0-255")
        return
    motion.set_blower(blower_id, value)
    _send_response(client, 200, "Blower " + str(blower_id) + " -> " + str(value))


def _handle_test_speaker(client, params):
    """Set a speaker channel level (channels 8-13)."""
    import hardware.motion as motion
    channel = _int_param(params, "channel", -1)
    value = _int_param(params, "value", -1)
    if channel < 8 or channel > 13:
        _send_response(client, 400, "Channel must be 8-13")
        return
    if value < 0 or value > 255:
        _send_response(client, 400, "Value must be 0-255")
        return
    motion.set_speaker(channel, value)
    _send_response(client, 200, "Speaker ch" + str(channel) + " -> " + str(value))


def _handle_test_audio(client, params):
    """Play a specific audio track for speaker testing."""
    import hardware.audio as audio
    player = _int_param(params, "player", 1)
    track = _int_param(params, "track", -1)
    loop = _int_param(params, "loop", 0)
    if track < 1 or track > 99:
        _send_response(client, 400, "Track must be 1-99")
        return
    audio.play_audio(player, track, loop=(loop == 1))
    mode = "looping" if loop == 1 else "one-shot"
    _send_response(client, 200, "Playing track " + str(track) + " (" + mode + ")")


def _handle_test_segment(client, params):
    """Set a single LED segment to an RGB color."""
    import hardware.lighting_manager as lighting_manager
    seg_id = params.get("id", "")
    r = _int_param(params, "r", -1)
    g = _int_param(params, "g", -1)
    b = _int_param(params, "b", -1)
    if not seg_id:
        _send_response(client, 400, "Missing segment id")
        return
    if r < 0 or g < 0 or b < 0 or r > 255 or g > 255 or b > 255:
        _send_response(client, 400, "RGB values must be 0-255")
        return
    lighting_manager.set_segment_color(seg_id, (r, g, b))
    _send_response(client, 200, seg_id + " -> (" + str(r) + "," + str(g) + "," + str(b) + ")")


def _handle_test_fog(client, params):
    """Turn the fogger relay on or off directly."""
    import hardware.atmosphere as atmosphere
    state = params.get("state", "")
    if state == "on":
        if hasattr(atmosphere, "fogger_relay") and atmosphere.fogger_relay:
            atmosphere.fogger_relay.value = False  # Relay ON (active-low)
        _send_response(client, 200, "Fogger ON")
    elif state == "off":
        if hasattr(atmosphere, "fogger_relay") and atmosphere.fogger_relay:
            atmosphere.fogger_relay.value = True  # Relay OFF
        _send_response(client, 200, "Fogger OFF")
    else:
        _send_response(client, 400, "state must be on or off")


def _handle_test_scene_start(client):
    """Start the Smial inspection test scene."""
    from logic.test_scene import smial_test
    smial_test.start()
    _send_response(client, 200, "Test scene started")


def _handle_test_scene_stop(client):
    """Stop the currently running test scene."""
    from logic.test_scene import smial_test
    smial_test.stop()
    _send_response(client, 200, "Test scene stopped")


def _handle_test_reset(client):
    """Reset all hardware to safe default state."""
    import hardware.motion as motion
    import hardware.lighting as lighting
    import hardware.atmosphere as atmosphere
    motion.reset_all()
    lighting.set_all_lights_off()
    if hasattr(atmosphere, "fogger_relay") and atmosphere.fogger_relay:
        atmosphere.fogger_relay.value = True  # Relay OFF
    _send_response(client, 200, "All hardware reset")


# ================================================================
#  HTTP helpers
# ================================================================

def _parse_query(query_string):
    """Parse 'key=value&key2=value2' into a dict. No URL-decoding needed for our simple keys."""
    params = {}
    if not query_string:
        return params
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key] = value
    return params


def _int_param(params, key, default):
    """Safely extract an integer from the params dict."""
    try:
        return int(params.get(key, default))
    except (ValueError, TypeError):
        return default


def _send_html(client, html):
    """Send a full HTML page response with correct headers."""
    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "Content-Length: " + str(len(html)) + "\r\n"
        "\r\n"
    )
    try:
        client.sendall(header.encode("utf-8"))
        # Send HTML in chunks to avoid memory pressure on ESP32
        chunk_size = 1024
        for i in range(0, len(html), chunk_size):
            client.sendall(html[i:i + chunk_size].encode("utf-8"))
    except Exception as e:
        print("web_logic: send error", e)
    finally:
        client.close()


def _send_response(client, status_code, message):
    """Send a short plain-text API response."""
    status_text = "OK" if status_code == 200 else "Error"
    header = (
        "HTTP/1.1 " + str(status_code) + " " + status_text + "\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Content-Length: " + str(len(message)) + "\r\n"
        "\r\n"
    )
    try:
        client.sendall((header + message).encode("utf-8"))
    except Exception as e:
        print("web_logic: send error", e)
    finally:
        client.close()


# ================================================================
#  Legacy helper (kept for backward compatibility with code.py)
# ================================================================

def apply_lighting_preset(preset_id):
    """Convenience wrapper used by code.py."""
    import hardware.lighting as lighting
    lighting.apply_lighting_preset(preset_id)