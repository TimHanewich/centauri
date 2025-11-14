import math
import gc
import time

answer:float = 0.0

# normal test
mem1 = gc.mem_free()
answer = math.atan(0.15)
mem2 = gc.mem_free()
print("Mem used: " + str(mem1 - mem2))

# in a native function
@micropython.native
def doatan(input:float) -> float:
    return math.atan(input)

mem1 = gc.mem_free()
answer = doatan(0.15)
mem2 = gc.mem_free()
print("Mem used: " + str(mem1 - mem2))











@micropython.viper
def isqrt(x: int) -> int:
    # Integer square root using Newton's method
    if x <= 0:
        return 0
    r = x
    while True:
        new_r = (r + x // r) // 2
        if new_r >= r:
            return r
        r = new_r

val1 = 314200
mem1 = gc.mem_free()
isqrt(val1)
mem2 = gc.mem_free()
print("Memory used: " + str(mem1 - mem2))