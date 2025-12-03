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
            raise Exception("Unable to pack LT/RT input: value must be provided as between 0.0 and 1.0! You provided '" + str(value) + "'.")
        asint16:int = min(max(int(round(value * 65535, 0)), 0), 65535)
        ToReturn.extend(asint16.to_bytes(2, "big"))
    else: # one of the stick axis inputs
        if value < -1.0 or value > 1.0:
            raise Exception("Unable to pack joystick variable input: value must be provided as between -1.0 and 1.0! You provided '" + str(value) + "'.")
        aspor:float = (value + 1.0) / 2.0 # as percent of total possible range
        asint16:int = min(max(int(round(aspor * 65535, 0)), 0), 65535)
        ToReturn.extend(asint16.to_bytes(2, "big"))

    # append \r\n
    ToReturn.extend("\r\n".encode())

    return bytes(ToReturn)