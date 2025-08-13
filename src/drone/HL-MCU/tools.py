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
    """Does NOT append \r\n at the end"""

    ToReturn:bytearray = bytearray()

    # header byte
    ToReturn.append(0b00000001) # bit 0 1 to declare as special packet

    # message
    ToUse:str = msg[0:50] # truncate to 50 characters
    ToReturn.extend(ToUse.encode("ascii"))

    return bytes(ToReturn)