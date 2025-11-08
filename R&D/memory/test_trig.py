import math
import time
import gc

# sample data
accel_x = 93
accel_y = 11
accel_z = 1028

# set up variables now so we are not slowed down by making them later
t1 = time.ticks_us()
t2 = time.ticks_us()
mem1 = gc.mem_free()
mem2 = gc.mem_free()
expected_pitch_angle_accel = 0
expected_roll_angle_accel = 0

# method 1
# ~520 us
# 128 bytes of memory
expected_pitch_angle_accel:int = int(math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 180000 / math.pi) # the accelerometers opinion of what the pitch angle is
expected_roll_angle_accel:int = int(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * 180000 / math.pi) # the accelerometers opinion of what the roll angle is


# imrprovement 2 - do not use **2, multiply by each other
# ~216 us
# 128 bytes of memory
expected_pitch_angle_accel:int = int(math.atan2(accel_x, math.sqrt(accel_y * accel_y + accel_z * accel_z)) * 180000 / math.pi)
expected_roll_angle_accel:int = int(math.atan2(accel_y, math.sqrt(accel_x * accel_x + accel_z * accel_z)) * 180000 / math.pi)

# imrprovement 3 - use pi as integer (rounded) and use integer division, removing the int()
pi = 3142 # rounded
# ~232 us
# 128 bytes of memory
expected_pitch_angle_accel:int = math.atan2(accel_x, math.sqrt(accel_y * accel_y + accel_z * accel_z)) * 180000 // pi
expected_roll_angle_accel:int = math.atan2(accel_y, math.sqrt(accel_x * accel_x + accel_z * accel_z)) * 180000 // pi

# improvement 4 - manual atan2
# ~215 us
mem1 = gc.mem_free()
pi = 3142
atan2_y = accel_x
atan2_x = math.sqrt(accel_y * accel_y + accel_z * accel_z)
expected_pitch_angle_accel = (pi * (atan2_x - atan2_y)) // (4 * (atan2_x + atan2_y))
mem2 = gc.mem_free()
print(str(mem1 - mem2))