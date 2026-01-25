def unpack_packet(data:bytes) -> dict:

    # extract timestamp (in ms)
    ticks_ms:int = data[0] << 16 | data[1] << 8 | data[2]

    # extract battery reading
    # the battery voltage will come in 10x what it is - so 168 would be 16.8, 60 would be 6.0
    # so just divide by 10 to get the actual value (as a float)
    vbat:float = data[3] / 10

    # rates
    pitch_rate:int = data[4] - 128
    roll_rate:int = data[5] - 128
    yaw_rate:int = data[6] - 128

    # angles
    pitch_angle:int = data[7] - 128
    roll_angle:int = data[8] - 128

    # gforce
    gforce:int = data[9] / 10 # divide by 10 because it is stored as 10x what it is, like vbat!

    # inputs
    input_throttle:int = data[10]     # flat percentage (0-100)
    input_pitch:int = data[11] - 100  # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
    input_roll:int = data[12] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
    input_yaw:int = data[13] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives

    # motor throttles
    m1_throttle:int = data[14]
    m2_throttle:int = data[15]
    m3_throttle:int = data[16]
    m4_throttle:int = data[17]

    # last received command control pack, in ms ago
    # it is encoded in increments of 10, so multiply by 10!
    lrecv_ms:int = data[18] * 10

    return {"ticks_ms": ticks_ms, "vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "pitch_angle": pitch_angle, "roll_angle": roll_angle, "gforce": gforce, "input_throttle": input_throttle, "input_pitch": input_pitch, "input_roll": input_roll, "input_yaw": input_yaw, "m1_throttle": m1_throttle, "m2_throttle": m2_throttle, "m3_throttle": m3_throttle, "m4_throttle": m4_throttle, "lrecv_ms": lrecv_ms}