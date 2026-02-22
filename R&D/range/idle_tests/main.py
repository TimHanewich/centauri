import machine
import time

gpio_motor1:int = 21 # front left, clockwise
gpio_motor2:int = 20 # front right, counter clockwise
gpio_motor3:int = 19 # rear left, counter clockwise
gpio_motor4:int = 18 # rear right, clockwise
target_hz:int = 250 # the number of times to run the PID loop, per second. IMPORTANT: if you change this, you will also need to change the time-sensitive PID gains (integral and derivative). I did not build a time-scaling mechanism into those calculations.
M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1), freq=target_hz, duty_ns=1000000)
M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2), freq=target_hz, duty_ns=1000000)
M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3), freq=target_hz, duty_ns=1000000)
M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4), freq=target_hz, duty_ns=1000000)

# switch
while True:

    # turn on @ 30%
    M1.duty_ns(1_300_000)
    M2.duty_ns(1_300_000)
    M3.duty_ns(1_300_000)
    M4.duty_ns(1_300_000)

    # wait
    print("Now on. Waiting 5 seconds...")
    time.sleep(5.0)

    # turn off
    M1.duty_ns(1_000_000)
    M2.duty_ns(1_000_000)
    M3.duty_ns(1_000_000)
    M4.duty_ns(1_000_000)

    # wait
    print("Now off. Waiting 5 seconds...")
    time.sleep(5.0)