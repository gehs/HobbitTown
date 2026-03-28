import busio
import digitalio
import time
import config

uart = None
gate_voices = None
gate_deep = None

def setup_audio():
    global uart, gate_voices, gate_deep
    uart = busio.UART(config.AUDIO_TX_PIN, config.AUDIO_RX_PIN, baudrate=9600)
    
    gate_voices = digitalio.DigitalInOut(config.GATE_VOICES_PIN)
    gate_deep = digitalio.DigitalInOut(config.GATE_DEEP_PIN)
    gate_voices.direction = digitalio.Direction.OUTPUT
    gate_deep.direction = digitalio.Direction.OUTPUT
    gate_voices.value = True
    gate_deep.value = True
    
    # Initialize players
    # Switch to spots (player 2)
    gate_voices.value = False
    time.sleep(0.1)
    send_cmd(0x06, 0, config.SPOT_VOL)  # Set volume
    time.sleep(0.1)
    gate_voices.value = True
    
    # Switch to base (player 1)
    gate_deep.value = False
    time.sleep(0.1)
    send_cmd(0x06, 0, config.BASE_VOL)  # Set volume
    time.sleep(0.1)
    gate_deep.value = True
    
    print("Audio: initialized")

def send_cmd(cmd, param1=0, param2=0):
    # DFPlayer Mini protocol
    data = [0x7E, 0xFF, 0x06, cmd, 0x00, param1, param2, 0x00, 0x00, 0xEF]
    checksum = 0
    for i in range(1, 7):
        checksum += data[i]
    checksum = -checksum & 0xFFFF
    data[7] = (checksum >> 8) & 0xFF
    data[8] = checksum & 0xFF
    uart.write(bytes(data))

def play_audio(player, track, loop=False):
    gate = gate_deep if player == 1 else gate_voices
    gate.value = False
    time.sleep(0.02)
    cmd = 0x08 if loop else 0x03  # 0x08 loop, 0x03 play
    send_cmd(cmd, 0, track)
    time.sleep(0.05)
    gate.value = True

def run_audio_cycle():
    # Placeholder for any continuous audio logic
    pass

# Convenience functions
def play_daytime():
    play_audio(1, 1, loop=True)

def play_sunset_sfx():
    play_audio(1, 2, loop=False)

def play_nighttime():
    play_audio(1, 3, loop=True)

def play_dragon_event():
    play_audio(1, 4, loop=False)

def play_party_music():
    play_audio(1, 5, loop=True)