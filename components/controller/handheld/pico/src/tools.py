import math

def unpack_button_input(packed:bytes) -> int: # returns the int that corresponds to the Button - see the "Button" Enum in the RPi's tools.py (MicroPython doesn't support Enum)

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

    return btn_id


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
        
data = b'\t\r\n'
btn = unpack_button_input(data)
print(str(btn))