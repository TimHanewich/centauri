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

from enum import Enum

class Button(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    Up = 4
    Right = 5
    Down = 6
    Left = 7
    LB = 8
    RB = 9
    LS = 10 # Left Stick Click
    RS = 11 # Right Stick Click
    Back = 12
    Start = 13

class Joystick(Enum):
    LS_X = 0    # Left stick X axis (left-right)
    LS_Y = 1    # Left stick Y axis (up-down)
    RS_X = 2    # Right stick X axis (left-right)
    RS_Y = 3    # Right stick Y axis (up-down)
    LT = 4      # Left trigger
    RT = 5      # Right trigger

def pack_button_input_event(btn:Button) -> bytes:
    data_byte:int = btn.value # start with the actual value (i.e. 0b00001101 for select)
    # If we needed to change bit 7, 6, 5, or 4 to a 1, we could do it... but we don't have to. The "correct" state for those is 0!
    ToReturn:bytearray = bytearray()
    ToReturn.append(data_byte)
    ToReturn.extend("\r\n".encode())
    return bytes(ToReturn)

def pack_joystick_input_event(js:Joystick, value:float) -> bytes:
    """
    Packs a joystick (variable input) update into a binary message. 
    
    'value' should be between -1.0 and 1.0 for left stick and right stick X/Y axis input, but between 0.0 and 1.0 for LT and RT.
    """

    ToReturn:bytearray = bytearray()

    # set header byte
    header_byte:int = js.value # start with the actual value
    header_byte = header_byte | 0b01000000 # set bit 6 to 1 to indicate this is a joystick (not a button)
    ToReturn.append(header_byte)

    # set up value bytes (as a uint16)
    if js == Joystick.LT or js == Joystick.RT: # one of the triggers (0.0 to 1.0)
        if value < 0.0 or value > 1.0:
            raise Exception("Unable to pack LT/RT input: value must be provided as between 0.0 and 1.0!")
        asint16:int = min(max(int(round(value * 65535, 0)), 0), 65535)
        ToReturn.extend(asint16.to_bytes(2, "big"))
    else: # one of the stick axis inputs
        if value < -1.0 or value > 1.0:
            raise Exception("Unable to pack joystick variable input: value must be provided as between -1.0 and 1.0!")
        aspor:float = (value + 1.0) / 2.0 # as percent of total possible range
        asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
        ToReturn.extend(asint16)

    # append \r\n
    ToReturn.extend("\r\n".encode())

    return bytes(ToReturn)