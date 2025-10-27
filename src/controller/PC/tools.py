### PACKING DATA TO SEND TO DRONE (through transceiver)

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

def pack_settings_update(pitch_kp:int, pitch_ki:int, pitch_kd:int, roll_kp:int, roll_ki:int, roll_kd:int, yaw_kp:int, yaw_ki:int, yaw_kd:int, i_limit:int) -> bytes:
    """Pack settings update"""

    # if any of the inputs exceed a uint16, throw an error
    if pitch_kp < 0 or pitch_ki < 0 or pitch_kd < 0 or roll_kp < 0 or roll_ki < 0 or roll_kd < 0 or yaw_kp < 0 or yaw_ki < 0 or yaw_kd < 0 or i_limit < 0:
        raise Exception("Unable to pack PID settings! Ensure all input parameters are greater than 0.")
    elif pitch_kp > 65535 or pitch_ki > 65535 or pitch_kd > 65535 or roll_kp > 65535 or roll_ki > 65535 or roll_kd > 65535 or yaw_kp > 65535 or yaw_ki > 65535 or yaw_kd > 65535 or i_limit > 65535:
        raise Exception("Unable to pack PID settings! Ensure all input parameters are less than 65535.")
    
    ToReturn:bytearray = bytearray()

    # header byte
    # bit 0 being 1 indicates it is a settings update packet
    ToReturn.append(0b00000001)

    # pack each, one by one, as 2 bytes (uint16 between 0 and 65535)
    ToReturn.extend(pitch_kp.to_bytes(2, "big"))
    ToReturn.extend(pitch_ki.to_bytes(2, "big"))
    ToReturn.extend(pitch_kd.to_bytes(2, "big"))
    ToReturn.extend(roll_kp.to_bytes(2, "big"))
    ToReturn.extend(roll_ki.to_bytes(2, "big"))
    ToReturn.extend(roll_kd.to_bytes(2, "big"))
    ToReturn.extend(yaw_kp.to_bytes(2, "big"))
    ToReturn.extend(yaw_ki.to_bytes(2, "big"))
    ToReturn.extend(yaw_kd.to_bytes(2, "big"))

    # pack i_limit, but first reduce by 1,000x
    # (it will later be re-inflated by 1,000x on the drone)
    # We do this to allow values of way more than 65,535 (uint 16 max) to be transmitted, while still keeping only 2 bytes
    # could do a full int with 4 bytes, but that level of precision for a simple i_limit clamp is not needed!
    i_limit_to_transmit:int = i_limit // 1000
    ToReturn.extend(i_limit_to_transmit.to_bytes(2, "big"))

    # Add XOR-chain-based checksum
    checksum:int = 0x00 # start with 0
    for byte in ToReturn: # for each byte added so far
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    # return
    return bytes(ToReturn)



######### UNPACKING DATA FROM THE DRONE ########

def unpack_telemetry(data:bytes) -> dict:
    """Unpacks telemetry packet coming from the drone"""

    # if it is not long enough, return None to indicate it didn't work
    if len(data) < 7:
        return None

    # the first byte is a header (metadata) byte

    # battery voltage
    vbat:float = 6.0 + ((16.8 - 6.0) * (data[1] / 255))

    # others
    # we subtract 128 here to "shift back" to a signed byte from an unsigned byte (128 is added before packing it)
    pitch_rate:int = data[2] - 128
    roll_rate:int = data[3] - 128
    yaw_rate:int = data[4] - 128
    pitch_angle:int = data[5] - 128
    roll_angle:int = data[6] - 128

    # return
    ToReturn:dict = {"vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "pitch_angle": pitch_angle, "roll_angle": roll_angle}
    return ToReturn

def unpack_special_packet(data:bytes) -> str:
    """Unpacks a special packet, containing free text"""

    # the first byte is a header, so we can ignore

    # determine how far to go in
    EndOn:int = len(data)
    if data.endswith("\r\n".encode()):
        EndOn = EndOn - 2
    
    trb:bytes = data[1:EndOn]
    ToReturn:str = trb.decode(errors="replace") # transmission errors will be replaced with "�"
    return ToReturn



##### MISC TOOLS #####

import rich.prompt
import math

def ask_integer(prompt:str) -> int:
    while True:
        ip:str = rich.prompt.Prompt.ask(prompt)
        try:
            return int(ip)
        except:
            print("Invalid input! Must be an integer.")

def ask_float(prompt:str) -> float:
    while True:
        ip:str = rich.prompt.Prompt.ask(prompt)
        try:
            return float(ip)
        except:
            print("Invalid input! Must be a floating point number.")

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