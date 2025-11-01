def unpack_packet(data:bytes) -> dict:

    # extract timestamp (in ms)
    ticks_ms:int = data[0] << 16 | data[1] << 8 | data[0]

    return {"ticks_ms": ticks_ms}