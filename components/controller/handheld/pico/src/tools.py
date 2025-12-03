import math

### FOR RECEIVING CONTROLLER INPUT ###

def unpack_button_input(packed:bytes) -> tuple[int, bool]: # returns the int that corresponds to the Button - see the "Button" Enum in the RPi's tools.py (MicroPython doesn't support Enum), and then the status (True = pressed, False = depressed)

    if len(packed) == 0:
        return None

    # define a binary mask of the bit positions we ONLY want
    # we only want bits 0, 1, 2, and 3. Those represent the numeric value
    # bits 4, 5, 6, and 7 are bits that contain other info
    # We will isolate bits 0,1,2,3 and thus get the numeric value of the button, unaffected by those other info header bits
    mask:int = 0b00001111

    # Determine what button was pressed
    # this AND operation will only allow the bits that match up to be 1
    # since we set bit 4-7 to 0, it will be impossible for those to come out as 1
    btn_id:int = packed[0] & mask

    # Now determine the status (pressed or depressed)
    # if bit 5 is 1, it is pressed. Otherwise, it is not
    pressed:bool = packed[0] & 0b00100000 > 0

    return (btn_id, pressed)

def unpack_joystick_input(packed:bytes) -> tuple[int, float]: # unpacks as the ID of the joystick (see 'Joystick' Enum of the RPi's tools.py) and then the value as a floating point number

    # if the length is not at least 3 (one header byte, two value bytes), there is a problem
    if len(packed) < 3:
        return None
    
    # define a binary mask of the bit positions we ONLY want
    # we only want bits 0, 1, and 2. Those represent the numeric value
    # bits 3, 4, 5, 6, and 7 are bits that contain other info
    # We will isolate bits 0,1,2 and thus get the numeric value of the button, unaffected by those other info header bits
    mask:int = 0b00000111

    # Determine what joystick was moved
    # this AND operation will only allow the bits that match up to be 1
    # since we set bit 3-7 to 0, it will be impossible for those to come out as 1
    joystick_id:int = packed[0] & mask

    # Get the value
    value:float = 0.0 # start w/ 0
    if joystick_id == 4 or joystick_id == 5: # if it is the LT or RT, it is between 0.0 and 1.0
        asuint16:int = (packed[1] << 8) | packed[2]
        value = asuint16 / 65535 # just a flat % of the total range!
    else: # otherwise, it is the X/Y axis of the Left/Right stick... which can be between -1.0 and 1.0
        asuint16:int = (packed[1] << 8) | packed[2]
        aspor:float = asuint16 / 65535 # % of total range
        value = (2 * aspor) - 1.0 # restore to a -1.0 to 1.0

    return (joystick_id, value)




##################################################
### FOR PACKING/UNPACKING TELEMETRY FROM DRONE ###
### LIFTED DIRECTLY OUT OF THE PC's utils.py   ###
##################################################

def unpack_telemetry(data:bytes) -> dict:
    """Unpacks telemetry packet coming from the drone"""

    # if it is not long enough, return None to indicate it didn't work
    if len(data) < 5:
        return None

    # the first byte is a header (metadata) byte

    # battery voltage
    # the battery voltage will come in 10x what it is - so 168 would be 16.8, 60 would be 6.0
    # so just divide by 10 to get the actual value (as a float)
    vbat:float = data[1] / 10

    # rates & angles
    # we subtract 128 here to "shift back" to a signed byte from an unsigned byte (128 is added before packing it)
    pitch_rate:int = data[2] - 128
    roll_rate:int = data[3] - 128
    yaw_rate:int = data[4] - 128
    pitch_angle:int = data[5] - 128
    roll_angle:int = data[6] - 128

    # return
    ToReturn:dict = {"vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "pitch_angle": pitch_angle, "roll_angle": roll_angle}
    return ToReturn




# Lifted from the Scout Flight Controller, my previous work: https://github.com/TimHanewich/scout/blob/master/src/toolkit.py
class NonlinearTransformer:
    """Converts a linear input to a nonlinear output (dampening) using tanh and a dead zone."""
    

    def __init__(self, nonlinearity_strength:float = 2.0, dead_zone_percent:float = 0.0) -> None:
        """
        Creates a new NonlinearTransformer.
        :param nonlinearity_strength: How strong you want the nonlinearity to be. 0.0 = perfectly linear, 5.0 = strongly nonlinear. Generally, 1.5-2.5 is a good bet.
        :param dead_zone_percent: The input percent to ignore before beginning to return values (any input less than this would result in 0.0).
        """

        # calculate multiplier
        self.multiplier = nonlinearity_strength

        # set dead zone
        self.dead_zone_percent = dead_zone_percent

    def y(self, x:float) -> float:
        return math.tanh(self.multiplier * (x - 1)) + 1

    def _transform(self, percent:float) -> float:

        # account for dead zone
        x:float = (percent - self.dead_zone_percent) / (1.0 - self.dead_zone_percent) # account for dead zone
        x = max(x, 0) # cannot be less than 0.0
        x = min(x, 1.0) # cannot be more than 1.0

        # determine the range we have to work with (minimum is tanh intersect at 0.0 x)
        min_y:float = self.y(0)
        max_y:float = 1.0 # intersect will always be at exactly (1, 1) based on the tanh equation I have set up
    
        # calculate and scale to within the min and max range
        ToReturn:float = self.y(x)
        ToReturn = (ToReturn - min_y) / (max_y - min_y)
        return ToReturn
    
    def transform(self, percent:float) -> float:
        """Convert linear input to nonlinear output."""
        if percent >= 0:
            return self._transform(percent)
        else:
            return (self._transform(abs(percent)) * -1)