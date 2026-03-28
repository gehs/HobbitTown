import wifi  # type: ignore
import socketpool  # type: ignore
import mdns  # type: ignore
import config

# Assuming NetworkSecrets.py or hardcoded
WIFI_SSID = "YOUR_WIFI_SSID"  # Replace or import from secrets
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
DEVICE_HOSTNAME = "hobbitt2"

pool = None
server = None
party_mode_active = False

def setup_web():
    global pool
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print("WiFi connected. IP:", wifi.radio.ipv4_address)
    
    pool = socketpool.SocketPool(wifi.radio)
    
    # mDNS
    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = DEVICE_HOSTNAME
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
    print("mDNS ready at http://" + DEVICE_HOSTNAME + ".local")
    
    # Web server placeholder
    print("Web server setup placeholder")

def run_web_sync():
    # Handle web requests
    pass

def apply_lighting_preset(preset_id):
    # Import here to avoid circular
    import hardware.lighting as lighting
    lighting.apply_lighting_preset(preset_id)