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

    # left stick x axis (left right)
    left_stick_x_axis:float = ((data[2] << data[3]) - 32768) / 32768
    ToReturn["left_x"] = left_stick_x_axis


    return ToReturn