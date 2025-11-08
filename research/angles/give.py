import math

def atan_approx(z):
    abs_z = abs(z)
    if abs_z < 1:
        return (math.pi / 4) * z - z * (abs_z - 1) * (0.2447 + 0.0663 * abs_z)
    else:
        return math.pi / 2 - atan_approx(1 / abs_z) if z > 0 else -math.pi / 2 + atan_approx(1 / abs_z)
    
i:float = 44.0
calc1 = math.atan(i)
calc2 = atan_approx(i)
print(calc1)
print(calc2)