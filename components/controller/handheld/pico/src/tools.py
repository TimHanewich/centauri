def unpack_controls(data:bytes) -> dict:
    """Unpacks control data (from a Raspberry Pi w/ a controller connected) to normal data."""

    ToReturn:dict = {}

    # left stick pressed? (clicked down)
    if data[0] & 0b00100000 > 0:
        ToReturn["ls"] = True
    else:
        ToReturn["ls"] = False
    
    # right stick pressed? (clicked down)
    if data[0] & 0b00010000 > 0:
        ToReturn["rs"] = True
    else:
        ToReturn["rs"] = False

    # back button pressed?
    if data[0] & 0b00001000 > 0:
        ToReturn["back"] = True
    else:
        ToReturn["back"] = False

    # start button pressed?
    if data[0] & 0b00000100 > 0:
        ToReturn["start"] = True
    else:
        ToReturn["start"] = False

    # a button pressed?
    if data[0] & 0b00000010 > 0:
        ToReturn["a"] = True
    else:
        ToReturn["a"] = False

    # b button pressed?
    if data[0] & 0b00000001 > 0:
        ToReturn["b"] = True
    else:
        ToReturn["b"] = False

    # x button pressed?
    if data[1] & 0b10000000 > 0:
        ToReturn["x"] = True
    else:
        ToReturn["x"] = False

    # y button pressed?
    if data[1] & 0b01000000 > 0:
        ToReturn["y"] = True
    else:
        ToReturn["y"] = False

    # up dpad button pressed?
    if data[1] & 0b00100000 > 0:
        ToReturn["up"] = True
    else:
        ToReturn["up"] = False

    # right dpad button pressed?
    if data[1] & 0b00010000 > 0:
        ToReturn["right"] = True
    else:
        ToReturn["right"] = False

    # down dpad button pressed?
    if data[1] & 0b00001000 > 0:
        ToReturn["down"] = True
    else:
        ToReturn["down"] = False

    # left dpad button pressed?
    if data[1] & 0b00000100 > 0:
        ToReturn["left"] = True
    else:
        ToReturn["left"] = False

    # left bumper pressed?
    if data[1] & 0b00000010 > 0:
        ToReturn["lb"] = True
    else:
        ToReturn["lb"] = False

    # right bumper pressed?
    if data[1] & 0b00000001 > 0:
        ToReturn["rb"] = True
    else:
        ToReturn["rb"] = False

    # Axes (variables)
    ToReturn["left_x"] = -1 + ((data[2] << 8 | data[3]) / 65535) * 2
    ToReturn["left_y"] = -1 + ((data[4] << 8 | data[5]) / 65535) * 2
    ToReturn["right_x"] = -1 + ((data[6] << 8 | data[7]) / 65535) * 2
    ToReturn["right_y"] = -1 + ((data[8] << 8 | data[9]) / 65535) * 2
    ToReturn["lt"] = (data[10] << 8 | data[11]) / 65535
    ToReturn["rt"] = (data[12] << 8 | data[13]) / 65535

    return ToReturn