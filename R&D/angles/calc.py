import math
import gc
import time

accel_x:int = 22
accel_y:int = 12
accel_z:int = 940

# The old way of doing it
# uses a lot of memory
picth_angle:int = int(math.atan2(accel_x, math.sqrt(accel_y*accel_y + accel_z*accel_z)) * 180000 / math.pi) # 1,340 = 1.34 degrees
print("Pitch angle: " + str(picth_angle))


# Viper sqrt estimator (integer math)
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

# atan2 estimator (integer math)
def iatan2(y:int, x:int) -> int:
    # constants scaled by 1000
    PI     = 3141   # ~π * 1000
    PI_2   = 1571   # ~π/2 * 1000
    PI_4   = 785    # ~π/4 * 1000

    if x == 0:
        return PI_2 if y > 0 else -PI_2 if y < 0 else 0

    abs_y = abs(y)
    angle = 0

    if abs(x) >= abs_y:
        # slope = y/x
        slope = (abs_y * 1000) // abs(x)
        # polynomial approx of atan(slope)
        angle = (PI_4 * slope) // 1000
    else:
        # slope = x/y
        slope = (abs(x) * 1000) // abs_y
        angle = (PI_2 - (PI_4 * slope) // 1000)

    # adjust quadrant
    if x < 0:
        if y >= 0:
            angle = PI - angle
        else:
            angle = -PI + angle
    else:
        if y < 0:
            angle = -angle

    return angle


# Test
while True:
    
    t1 = time.ticks_us()
    accel_y_power2 = accel_y * accel_y
    accel_z_power2 = accel_z * accel_z
    sqrt_result:int = isqrt(accel_y_power2 + accel_z_power2)
    atan2_result:int = iatan2(accel_x, sqrt_result)
    final:int = atan2_result * 180000 // 3142
    t2 = time.ticks_us()
    print("Time: " + str(t2 - t1))

    time.sleep(0.25)