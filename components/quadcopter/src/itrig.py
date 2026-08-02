"""
Integer-only trig approximations for the flight controller.

Everything here is fixed point at a scale of 1000:
    an angle of 0.7892 radians is passed in as 789
    a result of 0.7089 comes back as 709

No floats, no math module. Only integer + - * // >> and abs().

Accuracy: sin and cos are within +/- 3 parts in 1000 worst case (0.3%).
tan is within about 2% relative. Both are well inside the roughly 2%
cross axis error of the MPU-6050 itself.

Based on Bhaskara I's sine approximation (7th century, still excellent):

    sin(x) ~= 16x(pi - x) / (5*pi^2 - 4x(pi - x))      for 0 <= x <= pi

cos and tan are both derived from that same sine.
"""

# sin approximation
# Made by Opus 5 on August 1, 2026
# Uses 0 bytes of new memory
# takes 90-50 us calling it
@micropython.viper
def isin(x_scaled:int) -> int:
    """
    Sine, integer only.

    Input:  angle in radians * 1000. Any value, positive or negative.
            e.g. pi/2 radians -> 1571
    Output: sin(angle) * 1000, so an integer from -1000 to 1000.
            e.g. 1571 -> 1000
    """

    _PI = 3142
    _TWO_PI = 6283
    _FIVE_PI_SQ = 49360820

    # Reduce to [-pi, pi].
    # CPython's % always returns a non negative result for a positive divisor,
    # but viper uses C semantics and truncates toward zero, so a negative input
    # stays negative here. The extra add makes it non negative either way, which
    # is what the rest of the reduction assumes.
    x:int = x_scaled % _TWO_PI
    if x < 0:
        x = x + _TWO_PI
    if x > _PI:
        x = x - _TWO_PI

    # Bhaskara is defined over 0..pi, so work on the magnitude and put the
    # sign back at the end. sin(-x) == -sin(x).
    # Tracked as an int, not a bool: viper has no bool type to operate on.
    negative:int = 0
    if x < 0:
        negative = 1
        x = -x

    # prod = x(pi - x), the term that appears in both halves of the formula.
    # Peak value is at x = pi/2: 1571 * 1571 = 2468041.
    prod:int = x * (_PI - x)

    # The formula is (16*prod * 1000) // (5pi^2 - 4*prod).
    #
    # Done literally that numerator reaches 3.9e10, which blows past
    # MicroPython's 30 bit small integer limit on the RP2040 and forces a slow
    # heap allocated big integer. So shift both halves right by 6 first. The
    # ratio is unchanged and everything stays comfortably under 2^30.
    #
    #   16 * prod >> 6  is the same as  prod >> 2
    num:int = prod >> 2                         # max 617010
    den:int = (_FIVE_PI_SQ - 4 * prod) >> 6     # 617010 .. 771263

    # den is never 0: its minimum is 617010 at x = pi/2.
    # Adding den>>1 before the floor divide rounds to nearest instead of down.
    result:int = (1000 * num + (den >> 1)) // den    # max 617010000, fits

    if result > 1000:       # rounding guard, should not trigger
        result = 1000

    if negative == 1:
        return -result
    return result

# cos approximation
# Made by Opus 5 on August 1, 2026
# Uses 0 bytes of new memory
# takes 90-50 us calling it
@micropython.viper
def icos(x_scaled:int) -> int:
    """
    Cosine, integer only. Same scaling as isin().

    cos(x) == sin(x + pi/2), so this just shifts and reuses the sine.
    """
    _HALF_PI = 1571     # pi/2 * 1000, rounded
    return int(isin(x_scaled + _HALF_PI))


# tan approximation
# Made by Opus 5 on August 1, 2026
# takes ~220 us. Calls isin twice (once via icos), so roughly 2x its runtime
# uses 0 bytes of new memory
@micropython.viper
def itan(x_scaled:int) -> int:
    """
    Tangent, integer only. Same scaling as isin().

    tan(x) == sin(x) / cos(x), so this is a ratio of the two above.

    Input:  angle in radians * 1000
    Output: tan(angle) * 1000, clamped to +/- 5000

    The clamp is not optional housekeeping, it is the whole point. As the
    angle approaches +/- pi/2 the true tangent runs away to infinity, and
    icos() lands exactly on 0 at 1571, which would be a divide by
    zero. Clamping caps the result and makes that case harmless. Because it
    lives in here, the caller does not need its own clamp on the result.

    The limit of 5000 means tan 5.0, which is an angle of about
    +/- 78.7 degrees, far beyond any sane flight attitude. It is hardcoded
    rather than an argument: viper does not support default argument values,
    and nothing needs a different cap.

    Accuracy note (measured against math.tan across +/- 1.5 rad):
    worst case is about 2% relative. That worst case is at SMALL angles,
    where the +/-3 absolute error of the sine is a big share of a small
    answer, so in absolute terms the error there is only 2/1000. Going the
    other way, toward the clamp, the absolute error grows (about 45/1000
    near 77 degrees) but stays around 1% relative. Either way it is well
    inside the roughly 2% cross axis error of the MPU-6050 itself.
    """

    s:int = int(isin(x_scaled))
    c:int = int(icos(x_scaled))

    # Work on magnitudes so the rounding stays symmetric. Viper's // truncates
    # toward zero rather than flooring, so mixing signs in here would bias the
    # result. The sign flag is an int because viper has no bool it can operate
    # on: "(s < 0) != (c < 0)" is a binary op between two bools and will not
    # compile. Flipping the flag twice is the same exclusive or.
    negative:int = 0
    if s < 0:
        negative = 1
        s = -s
    if c < 0:
        negative = 1 - negative
        c = -c

    result:int = 0
    if c == 0:
        # Exactly at +/- pi/2. The true value is infinite, so return the cap.
        result = 5000
    else:
        result = (1000 * s + (c >> 1)) // c      # max 1000000, tiny
        if result > 5000:
            result = 5000

    if negative == 1:
        return -result
    return result

# Integer Square Root (exact, not an estimate - returns floor(sqrt(x)))
# uses Newton's method
# Originally written by GPT-5 via Copilot
# Seeding enhanced by Claude Opus 5 on July 30, 2026
@micropython.viper
def isqrt(x: int) -> int:
    if x <= 0:
        return 0

    # Seed with the smallest power of two >= sqrt(x).
    # Starting at r = x makes Newton spend ~half of log2(x) iterations just halving before
    # the quadratic convergence begins - that was ~14 divisions at 1g and 18 worst case.
    # Since x < 2**bits implies sqrt(x) < 2**ceil(bits/2), this seed is always >= sqrt(x),
    # which is what keeps the descent monotonic and the "new_r >= r" stop condition valid.
    # Four compares replace ~11 divisions; the Pico's Cortex-M0+ has no divide instruction.
    r = 1
    t = x
    if t >= 0x10000:
        t = t >> 16
        r = r << 8
    if t >= 0x100:
        t = t >> 8
        r = r << 4
    if t >= 0x10:
        t = t >> 4
        r = r << 2
    if t >= 0x4:
        t = t >> 2
        r = r << 1
    r = r << 1

    # All operands stay non-negative, so >> 1 is safe under viper (unlike // on negatives).
    while True:
        new_r = (r + x // r) >> 1
        if new_r >= r:
            return r
        r = new_r

# atan2 estimator (integer math)
# Originally written by GPT-5 via Copilot
# Enhanced by Claude Opus 5 on July 30, 2026
@micropython.viper
def iatan2(y:int, x:int) -> int:
    # constants scaled by 1000
    PI     = 3141   # ~π * 1000
    PI_2   = 1571   # ~π/2 * 1000
    PI_4   = 785    # ~π/4 * 1000

    if x == 0:
        return PI_2 if y > 0 else -PI_2 if y < 0 else 0

    # calculate abs y
    abs_y = y
    if abs_y < 0:
        abs_y = abs_y * -1

    # calculate abs x
    abs_x = x
    if abs_x < 0:
        abs_x = abs_x * -1

    angle = 0

    # polynomial approx of atan(slope), where slope is 0-1000 representing 0.0-1.0:
    #   atan(s) ~= (pi/4)*s + s*(1-s)*(0.2447 + 0.0663*s)
    # This is the refined form. A plain (pi/4)*s is only exact at s=0 and s=1 and undershoots by
    # ~21% in between, which biases the accelerometer's angle low across normal flight attitudes.
    # Written so every operand stays non-negative: viper's // on negative values is not guaranteed
    # to floor the same way CPython does, and this form sidesteps that entirely.
    # Largest intermediate is 785,000, well inside viper's 32-bit signed int range.
    if abs_x >= abs_y:
        # slope = y/x
        slope = (abs_y * 1000) // abs_x
        angle = (PI_4 * slope) // 1000 + (slope * (1000 - slope) // 1000) * (2447 + 663 * slope // 1000) // 10000
    else:
        # slope = x/y
        slope = (abs_x * 1000) // abs_y
        angle = PI_2 - ((PI_4 * slope) // 1000 + (slope * (1000 - slope) // 1000) * (2447 + 663 * slope // 1000) // 10000)

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