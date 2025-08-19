### GENERAL HELPER FUNCTIONS

def shift_int16_to_uint16(val:int) -> int:
    """Does a simple 'shift' of an int16 (-32768 to 32767) to a uint16 (0 to 65535) by just adding 32768, shifting it upwards. Can later be shifted back down. Simple."""
    if val > 32767: # if exceeds bounds of upper limit of int16, return max of uint16
        return 65535
    elif val < -32768: # if lower than the lower limit of int16, return min value of uint16
        return 0
    else:
        return val + 32768

##### TO BE SENT TO REMOTE CONTROLLER

def pack_control_status(m1_throttle:float, m2_throttle:float, m3_throttle:float, m4_throttle:float, pitch_rate:float, roll_rate:float, yaw_rate:float, pitch_angle:float, roll_angle:float) -> bytes:

    ToReturn:bytearray = bytearray()

    # Add header (metadata) byte
    header:int = 0b00000000 # bit 0 (right-most) is "0" to declare as status packet
    ToReturn.append(header)

    # all motor throttles are alraedy expressed as 0.0 to 1.0, a percentage
    # we will just get equivalent integer in 0-65535 scale by scaling
    # and then convert that int16 to 2 bytes

    # add M1 throttle
    asint16:int = min(max(int(m1_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M2 throttle
    asint16:int = min(max(int(m2_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M3 throttle
    asint16:int = min(max(int(m3_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add M4 throttle
    asint16:int = min(max(int(m4_throttle * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # pitch rate, roll rate, and yaw rate will all be 
    # expressed as a percentage of the range from -180 d/s to 180 d/s
    # and then converted to an int16

    # add pitch rate
    aspop:float = (pitch_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add roll rate
    aspop:float = (roll_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add yaw rate
    aspop:float = (yaw_rate + 180) / 360
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # pitch and roll angle will be expressed as a % of the range of -90 and 90
    # and then that % will then be scaled between 0-65535
    # and then that int16 number being converted to 2 bytes

    # add pitch angle
    aspop:float = (pitch_angle + 90) / 180
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add roll angle
    aspop:float = (roll_angle + 90) / 180
    asint16 = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    return bytes(ToReturn)

def pack_system_status(battery:float, tfluna_distance:int, tfluna_strength:int, altitude:float, heading:float) -> bytes:
    """Packs the second portion of the status packet, the portion that originates from the HL MCU, into bytes"""

    ToReturn:bytearray = bytearray()

    # header byte (metadata)
    ToReturn.append(0b00000001) # 01 for bits 0 and 1 is the packet identifier for system status

    # battery voltage
    # Fully charged 4S = 16.8v
    # Full discharged 2S = 6.0v
    # So a range of 10.8 volts, over 65,636 unique values (uint16) = ~6,068 per volt. High resolution!
    aspor:float = (battery - 6.0) / (16.8 - 6.0) # percent of range
    asint16:int = min(max(int(aspor * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # TF Luna Reading: Distance
    asint16:int = min(max(tfluna_distance, 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # TF Luna Reading: Strength
    asint16:int = min(max(tfluna_strength, 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # BMP180: Altitude, in meters
    # BMP180's min pressure reading: 300 hPa = 9,165.16 meters
    # BMP180's max pressure reading: 1,100 hPa = -698.42 meters
    # thus, the range in meters is 9,863.58
    # We are able to express that over 65,536 unique values (uint16)
    # Which would be 6.64 per meter
    aspor:float = (altitude + 698.42) / 9863.58 # percent of range
    asint16:int = min(max(int(aspor * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # Heading
    # heading can be 0 to 360
    # however, since it isn't very sensitive, we will use a single byte here
    valb:int = int(heading / (256 / 360))
    valb = min(max(valb, 0), 255)
    ToReturn.append(valb)

    return bytes(ToReturn)

def pack_special_packet(msg:str) -> bytes:
    """Packs special packet with a message to be sent to the remote controller (via HC-12). Does NOT append \r\n at the end"""

    ToReturn:bytearray = bytearray()

    # header byte
    ToReturn.append(0b00000001) # bit 0 1 to declare as special packet

    # message
    ToUse:str = msg[0:50] # truncate to 50 characters
    ToReturn.extend(ToUse.encode("ascii"))

    return bytes(ToReturn)


### TO BE SENT TO LL-MCU

def pack_settings_update(pitch_kp:int, pitch_ki:int, pitch_kd:int, roll_kp:int, roll_ki:int, roll_kd:int, yaw_kp:int, yaw_ki:int, yaw_kd:int, i_limit:int) -> bytes:
    """Packs settings for LL-MCU into bytes, ready to be delivered to LL-MCU via UART."""

    ToReturn:bytearray = bytearray()

    # header byte (metadata)
    ToReturn.append(0b00000000) # 0 in the Bit 0 position (farthest to right) as packet identifier

    # Pitch values
    ToReturn.extend(pitch_kp.to_bytes(2, "little"))
    ToReturn.extend(pitch_ki.to_bytes(2, "little"))
    ToReturn.extend(pitch_kd.to_bytes(2, "little"))

    # Roll values
    ToReturn.extend(roll_kp.to_bytes(2, "little"))
    ToReturn.extend(roll_ki.to_bytes(2, "little"))
    ToReturn.extend(roll_kd.to_bytes(2, "little"))

    # Yaw values
    ToReturn.extend(yaw_kp.to_bytes(2, "little"))
    ToReturn.extend(yaw_ki.to_bytes(2, "little"))
    ToReturn.extend(yaw_kd.to_bytes(2, "little"))

    # i limit
    ToReturn.extend(i_limit.to_bytes(2, "little"))

    # XOR-chain based checksum:
    checksum:int = 0x00 # start with 0
    for byte in ToReturn:
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    return bytes(ToReturn)

def pack_desired_rates(throttle_uint16:int, pitch_int16:int, roll_int16:int, yaw_int16:int) -> bytes:

    ToReturn:bytearray = bytearray()

    # header byte
    ToReturn.append(0b00000001) # 1 is the packet identifier

    # pack throttle, pitch, roll, yaw
    ToReturn.extend(throttle_uint16.to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(pitch_int16).to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(roll_int16).to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(yaw_int16).to_bytes(2, "little"))
    
    # XOR-chain based checksum:
    checksum:int = 0x00 # start with 0
    for byte in ToReturn:
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    return bytes(ToReturn)