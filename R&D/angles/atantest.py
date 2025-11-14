import math
import gc
import time

answer:float = 0.0

# normal test
mem1 = gc.mem_free()
answer = math.atan(0.15)
mem2 = gc.mem_free()
print("Mem used: " + str(mem1 - mem2))

# in a function
@micropython.native
def doatan(input:float) -> float:
    return math.atan(input)

mem1 = gc.mem_free()
answer = doatan(0.15)
mem2 = gc.mem_free()
print("Mem used: " + str(mem1 - mem2))

# in a viper function
@micropython.viper
def doatanV(input:int) -> int:
    ToReturn:float = math.atan(input)
    return int(round(ToReturn, 1))

mem1 = gc.mem_free()
answer = doatanV(15)
mem2 = gc.mem_free()
print("Mem used: " + str(mem1 - mem2))

