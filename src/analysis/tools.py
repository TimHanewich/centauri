def unpack_packet(data:bytes) -> dict:

    # extract timestamp (in ms)
    ticks_ms:int = data[0] << 16 | data[1] << 8 | data[2]

    # extract battery reading
    vbat:float = 6.0 + ((16.8 - 6.0) * (data[3] / 255))

    # rates
    pitch_rate:int = data[4] - 128
    roll_rate:int = data[5] - 128
    yaw_rate:int = data[6] - 128

    return {"ticks_ms": ticks_ms, "vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate}