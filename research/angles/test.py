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

i:float = 1.34
calc1 = math.atan(i)
calc2 = atan_approx(i)
print(calc1)
print(calc2)