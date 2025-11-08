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
    abs_z:int = abs(z)
    pi:int = 3142 # 3.142 * 1,000
    if abs_z <= 1000: # less than 1
        term1:int = (pi * z) // 4
        term2:int = z * (abs_z - 1000) * (245 + ((66 * abs_z) // 1000)) // 1000
        return term1 - term2
    else:
        if z > 0: # if positive
            return (pi // 2000) - atan_approx_int(1000 // z)
        else: # if negative
            return (-pi // 2000) - atan_approx_int(1000 // z)
        
i:int = 333
calc1 = math.atan(i / 1000)
calc2 = atan_approx_int(i)
print("Calc1: " + str(calc1))
print("Calc2: " + str(calc2))
print("Calc2f: " + str(calc2 / 1000000))