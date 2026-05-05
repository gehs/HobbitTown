def _send_track_command_routed(self, action, track_num, output=0, lock_voice=0):
        """
        Builds and sends the 10-byte Track Control packet with output routing.
        output: 0-7 for Mono firmware, 0-3 for Stereo firmware.
        lock_voice: 1 prevents the track's voice from being stolen, 0 is normal.

	In the Tsunami protocol, track numbers can go all the way up to 4096. However, a single standard data byte sent over serial can only hold a maximum value of 255. To get around this, the Tsunami requires that 16-bit data values, such as track numbers, be sent "little-endian". This means the 16-bit number is chopped in half into two 8-bit bytes:

LSB (The "bottom" half): Contains the smaller portion of the value.

MSB (The "top" half): Contains the overflow multiplier.

	LSB = Least Significant Byte
	MSB = Most Significant Byte
        """
        # Split the track number into LSB and MSB
        track_lsb = track_num & 0xFF
        track_msb = (track_num >> 8) & 0xFF
        
        packet = bytearray([
            0xF0,              # Start of Message 1
            0xAA,              # Start of Message 2
            0x0A,              # Length of message (10 bytes)
            0x03,              # Command: Track Control
            action,            # Action Code (0=Solo, 1=Poly, 2=Pause, etc.)
            track_lsb,         # Track LSB
            track_msb,         # Track MSB
            output,            # Output Routing 
            lock_voice,        # Flags (bit 0 = Lock Voice)
            0x55               # End of Message
        ])
        self.uart.write(packet)

    # --- Updated Helper Functions ---

    def track_play_poly_routed(self, track_num, output):
        """Plays a track polyphonically on a specific output port."""
        self._send_track_command_routed(0x01, track_num, output=output, lock_voice=0)
        
    def track_play_solo_routed(self, track_num, output):
        """Stops other tracks and plays on a specific output port."""
        self._send_track_command_routed(0x00, track_num, output=output, lock_voice=0)