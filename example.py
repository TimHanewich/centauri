import micropython

BUF_SIZE = 128  # big enough for your largest packet + some margin
rxBuffer = bytearray(BUF_SIZE)
write_idx = 0
terminator = b"\r\n"

while True:
    # 1. Read what fits in the remaining buffer space
    if uart.any():
        space = BUF_SIZE - write_idx
        if space > 0:
            n = uart.readinto(memoryview(rxBuffer)[write_idx:write_idx+space])
            if n:
                write_idx += n
        else:
            # Buffer overflow handling - drop or resync
            write_idx = 0  # simple reset for this example

    # 2. Scan for terminators within the filled portion
    search_from = 0
    while True:
        loc = rxBuffer.find(terminator, search_from, write_idx)
        if loc == -1:
            break  # no full packet yet
        # Extract the packet (no allocation if you use memoryview)
        line_mv = memoryview(rxBuffer)[0:loc]
        # --- Process line_mv here ---
        first_byte = line_mv[0]
        if first_byte & 0b00000001:
            if tools.unpack_desired_rates(line_mv, desired_rates_data):
                throttle_uint16, pitch_int16, roll_int16, yaw_int16 = desired_rates_data
        elif line_mv.tobytes() == TIMHPING:
            sendtimhmsg("PONG")
        elif (first_byte & 0b00000001) == 0:
            settings = tools.unpack_settings_update(line_mv)
            if settings is not None:
                pitch_kp = settings["pitch_kp"]
                # ... assign others ...
                sendtimhmsg("SETUP")
            else:
                sendtimhmsg("SETUP FAIL")
        else:
            sendtimhmsg("?")

        # Move search start past this packet+terminator
        search_from = loc + 2

    # 3. Compact leftover bytes down to start of buffer
    if search_from:
        leftover = write_idx - search_from
        if leftover:
            rxBuffer[0:leftover] = rxBuffer[search_from:write_idx]
        write_idx = leftover
