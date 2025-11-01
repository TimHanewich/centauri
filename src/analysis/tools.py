def unpack_packet(data:bytes) -> dict:

    # extract timestamp (in ms)
    ticks_ms:int = data[0] << 16 | data[1] << 8 | data[2]

    # extract battery reading
    vbat:float = 6.0 + ((16.8 - 6.0) * (data[3] / 255))

    # rates
    pitch_rate:int = data[4] - 128
    roll_rate:int = data[5] - 128
    yaw_rate:int = data[6] - 128

    # inputs
    input_throttle:int = data[7]     # flat percentage (0-100)
    input_pitch:int = data[8] - 100  # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
    input_roll:int = data[9] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
    input_yaw:int = data[10] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives

    # motor throttles
    m1_throttle:int = data[11]
    m2_throttle:int = data[12]
    m3_throttle:int = data[13]
    m4_throttle:int = data[14]

    return {"ticks_ms": ticks_ms, "vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "input_throttle": input_throttle, "input_pitch": input_pitch, "input_roll": input_roll, "input_yaw": input_yaw, "m1_throttle": m1_throttle, "m2_throttle": m2_throttle, "m3_throttle": m3_throttle, "m4_throttle": m4_throttle}