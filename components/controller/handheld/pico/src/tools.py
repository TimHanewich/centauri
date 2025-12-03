import math

def unpack_controls(data:bytes) -> dict:
    """Unpacks control data (from a Raspberry Pi w/ a controller connected) to normal data."""

    if len(data) < 14: # while the full packet is normally 16, that is including the \r\n terminator. 14 is the actual data. So it has to be at least 14 in length.
        return None

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

def pack_control_packet(throttle:float, pitch:float, roll:float, yaw:float) -> bytes:
    """
    Packs a control packet to be sent to the drone.
    
    Expects:
    throttle between 0.0 and 1.0
    pitch between -1.0 and 1.0
    roll between -1.0 and 1.0
    yaw between -1.0 and 1.0
    """

    ToReturn:bytearray = bytearray()

    # Add header byte (metadata byte)
    # bit 7, 6, 5, 4 are reserved (unused)
    header:int = 0b00000000 # start with 0. Bit 0 must be 0 to identify as a control packet, which it already is!s
    ToReturn.append(header)

    # Add throttle bytes
    asint16 = min(max(int(round(throttle * 65535, 0)), 0), 65535) # express as number between 0 and 65535
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add pitch bytes
    aspop:float = (pitch + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # add roll bytes
    aspop:float = (roll + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # add yaw bytes
    aspop:float = (yaw + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # Add XOR-chain-based checksum
    checksum:int = 0x00 # start with 0
    for byte in ToReturn: # for each byte added so far
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    # return it
    return bytes(ToReturn)











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