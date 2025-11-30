def pack_controls(left_stick:bool, right_stick:bool, back:bool, start:bool, a:bool, b:bool, x:bool, y:bool, up:bool, right:bool, down:bool, left:bool, lb:bool, rb:bool, left_x:float, left_y:float, right_x:float, right_y:float, lt:float, rt:float) -> bytes:
    """Packs control inputs into a bytearray."""

    ToReturn:bytearray = bytearray()

    # buttons (byte 0 and byte 1)
    ToReturn.append(0)
    ToReturn.append(0)
    if left_stick:
        ToReturn[0] = ToReturn[0] | 0b00100000
    if right_stick:
        ToReturn[0] = ToReturn[0] | 0b00010000
    if back:
        ToReturn[0] = ToReturn[0] | 0b00001000
    if start:
        ToReturn[0] = ToReturn[0] | 0b00000100
    if a:
        ToReturn[0] = ToReturn[0] | 0b00000010
    if b:
        ToReturn[0] = ToReturn[0] | 0b00000001
    if x:
        ToReturn[1] = ToReturn[1] | 0b10000000
    if y:
        ToReturn[1] = ToReturn[1] | 0b01000000
    if up:
        ToReturn[1] = ToReturn[1] | 0b00100000
    if right:
        ToReturn[1] = ToReturn[1] | 0b00010000
    if down:
        ToReturn[1] = ToReturn[1] | 0b00001000
    if left:
        ToReturn[1] = ToReturn[1] | 0b00000100
    if lb:
        ToReturn[1] = ToReturn[1] | 0b00000010
    if rb:
        ToReturn[1] = ToReturn[1] | 0b00000001

    # add left stick x axis (left/right)
    aspor:float = (left_x + 1.0) / 2.0 # as percent of total range
    asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add left stick y axis (up/down)
    aspor:float = (left_y + 1.0) / 2.0 # as percent of total range
    asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add right stick x axis (left/right)
    aspor:float = (right_x + 1.0) / 2.0 # as percent of total range
    asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add right stick y axis (up/down)
    aspor:float = (right_y + 1.0) / 2.0 # as percent of total range
    asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add left trigger
    asint16:int = min(max(int(round(lt * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add right trigger
    asint16:int = min(max(int(round(rt * 65535, 0)), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add terminator
    ToReturn.extend("\r\n".encode())

    return bytes(ToReturn)

#data = pack_controls(False, True, False, True, False,True, False, True, False, False, False, True, False, False, 0.50, -0.5, 0.75, -0.65, 0.12, 0.35)
#print(str(data))