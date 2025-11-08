import math
import gc
import time

# declare variables
calc:float = 0.0
mem1 = 0
mem2 = 0

# demo atan2
# uses 16 bytes memory
mem1 = gc.mem_free()
calc = math.atan2(10, 20)
mem2 = gc.mem_free()
print("Mem used in atan2: " + str(mem1 - mem2))
print("Calc: " + str(calc))

# demo atan
# atan2 is nothing more than atan(z) with z = y / x
mem1 = gc.mem_free()
math.atan(0.5) # 0.5 = 10 / 20 (y/x). But doing y / x produces another float, so 16 NEW bytes of data
mem2 = gc.mem_free()
print("Mem used in atan: " + str(mem1 - mem2))
print("Calc: " + str(calc))

# demo atan manually
def atan_approx(z:float) -> float:
    """Approximates the math.atan() formula WITHOUT using math.atan."""
    abs_z:float = abs(z)
    if abs_z <= 1.0:
        return (math.pi / 4) * z - z * (abs_z - 1.0) * (0.2447 + 0.0663 * abs_z)
    else:
        if z > 0.0:
            return (math.pi / 2) - atan_approx(1 / z)
        else:
            return (-math.pi / 2) - atan_approx(1 / z)



# demo atan INTEGER calc manually
def atan_approx_int(z:int) -> int:
    """
    Approximates the math.atan() formula WITHOUT using math.atan to avoid floating point math.
    Expects input as an integer, the 1000x scale of the floating point number you'd be working with
    Returns as an integer, 1000x the scale what would be returned
    """

    # variables
    abs_z:int = abs(z)
    pi:int = 3142 # 3.142 * 1,000
    const1:int = 245
    const2:int = 66

    # calculate term 1
    # the first part of the subtraction: (pi / 4) * z
    term1:int = (pi * z) // 4

    # calculate const2z which will be used in term2
    const2z:int = (const2 * abs_z) // 1000

    # calculate term 2
    # the second part of the subtraction
    term2:int = z * (abs_z - 1000) * (const1 + const2z)
    term2 = term2 // 1000 # divide the whole thing by 1,000 before it is used to subtract (we must de-scale before subtraction)

    return (term1 - term2) // 1000

i:int = 330
calc1 = math.atan(i / 1000)
calc2 = atan_approx_int(i)
print("Calc1: " + str(calc1))
print("Calc2: " + str(calc2))