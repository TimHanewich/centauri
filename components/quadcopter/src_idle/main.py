# THIS IS A SIMPLE TEST SCRIPT TO RUN THE MOTORS AT 30%!
# ONLY ONLY ONLY USE THIS WITH THE PROPS OFF FOR SAFETY!

import machine
import time

# First thing is first: set up onboard LED, turn it on while loading
print("Turning LED on...")
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# right away, set up motor PWMs with frequency of 250 Hz and start at 0% throttle (yes, 1,000,000 ns is 0% throttle)
# why do this right away? Some ESCs have a timeout that will refuse to turn on if the PWM signal is not received within a certain number of seconds of powering on
gpio_motor1:int = 21 # front left, clockwise
gpio_motor2:int = 20 # front right, counter clockwise
gpio_motor3:int = 19 # rear left, counter clockwise
gpio_motor4:int = 18 # rear right, clockwise
target_hz:int = 250 # the number of times to run the PID loop, per second. IMPORTANT: if you change this, you will also need to change the time-sensitive PID gains (integral and derivative). I did not build a time-scaling mechanism into those calculations.
M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1), freq=target_hz, duty_ns=1000000)
M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2), freq=target_hz, duty_ns=1000000)
M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3), freq=target_hz, duty_ns=1000000)
M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4), freq=target_hz, duty_ns=1000000)

# pulse as a warning!
for _ in range(15):
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)

# idle motors
M1.duty_ns(1_300_000)
M2.duty_ns(1_300_000)
M3.duty_ns(1_300_000)
M4.duty_ns(1_300_000)