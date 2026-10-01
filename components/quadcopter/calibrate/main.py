# ==============================================================================
# CENTAURI CALIBRATION SCRIPT
# https://github.com/TimHanewich/centauri
# ==============================================================================
# Copyright (C) 2026 Tim Hanewich
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# this is a lightweight script to re-calibrate all of the motors on the quadcopter.
# WARNING: DO THIS WITH PROPS OFF!

import machine
import time

# set up led
led = machine.Pin("LED", machine.Pin.OUT)

# Set up var
gpio_motor:int = 20

# Set up on 100% throttle
print("Arming @ 100% throttle...")
target_hz:int = 250
motor:machine.PWM = machine.PWM(machine.Pin(gpio_motor), freq=target_hz, duty_ns=2000000)
led.on()

# Wait 5 seconds
print("Waiting 5 seconds...")
time.sleep(5.0)

# go to 0% throttle
print("Dropping to minimum throttle for calibration low point...")
motor.duty_ns(1_000_000)
led.off()

print("Calibration complete!")
