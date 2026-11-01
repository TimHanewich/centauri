import time
import math

def cpu_benchmark() -> int:
    """
    Returns the number of iterations it did within a 1-second timespan.
    """

    # set up to prepare
    acc_int = 1
    acc_float = 0.0

    # go!
    calculations:int = 0
    t1 = time.perf_counter()
    while (time.perf_counter() - t1) < 1.0: # for one full second
        
        # Integer arithmetic (multiply, modulo, xor, shifts)
        acc_int = (acc_int * 31 + 12_345) % 1_000_003
        acc_int ^= 0x5A5A
        acc_int = ((acc_int >> 1) + ((acc_int << 2) % 65_521)) | 1

        # Floating-point math (trig, sqrt, log, power, division)
        acc_float += math.sin(0.75) * math.cos(0.25) + math.sqrt(1234.5) / math.log(42.0)
        acc_float += (1.7 ** 1.5) / (1.0 + 0.3 * 0.3)
        acc_float *= 0.999999  # keeps the accumulator bounded

        # increment calculations
        calculations = calculations + 1

    # return number of calculations
    return calculations

# if this is the script!
if __name__ == "__main__":

    print("Benchmark begins in 3...")
    time.sleep(1.0)
    print("Benchmark begins in 2...")
    time.sleep(1.0)
    print("Benchmark begins in 1...")
    time.sleep(1.0)
    print("Benchmark running!")
    calcs:int = cpu_benchmark()
    print("Benchmark complete")
    print("Calculations: " + format(calcs, ","))