import pygame
import time
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")) # Add parent directory to path so we can import utils.py (shared module)
from utils import pack_control_packet, pack_settings_update, unpack_telemetry, unpack_special_packet, NonlinearTransformer

# Set up controller
print("Initializing pygame module...")
pygame.init()
pygame.joystick.init()

# count number of connected joysticks (gamepads)
num_joysticks:int = pygame.joystick.get_count()
print("Number of connected controllers: " + str(num_joysticks))
if num_joysticks == 0:
    print("No controller connected! Must connect a controller.")
    exit()

# loop through each connected controller
for i in range(num_joysticks):
    tjs = pygame.joystick.Joystick(i)
    tjs.init()
    print("Joystick " + str(i) + ": " + tjs.get_name())

# select the controller that will be used (default to first, and probably only, one)
controller = pygame.joystick.Joystick(0)
controller.init()
print("Controller #0, '" + controller.get_name() + "' will be used.")

# Declare control input variables
throttle:float = 0.0       # between 0.0 and 1.0
pitch:float = 0.0          # between -1.0 and 1.0
roll:float = 0.0           # between -1.0 and 1.0
yaw:float = 0.0            # between -1.0 and 1.0

def continuous_read_xbox() -> None:

    # Establish nonlinear transformers for each input axis
    # These do two things:
    # 1 - implements a deadzone
    # 2 - dampens early inputs (smooth gradually increasing curve, not linear)
    nlt_pitch:NonlinearTransformer = NonlinearTransformer(2.0, 0.05)
    nlt_roll:NonlinearTransformer = NonlinearTransformer(2.0, 0.05)
    nlt_yaw:NonlinearTransformer = NonlinearTransformer(2.0, 0.10) # my deadzone is higher than the others because I have a broken right stick on my controller that often rests at around 8% in either direction

    # start reading from it!
    print("NOW READING FROM XBOX CONTROLLER!")
    while True:

        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger
                if event.axis == 5: # right trigger
                    throttle = (event.value + 1.0) / 2.0 # gets it to between 0.0 and 1.0
                elif event.axis == 0: # left stick X axis (left/right)
                    roll = nlt_roll.transform(event.value)
                elif event.axis == 1: # left stick Y axis (up/down)
                    # pushing the left stick forward will result in a NEGATIVE value. While this may seem incorrect at first, it is actually correct... pushing the left stick forward should prompt the quadcopter to pitch down (forward), hence it should be negative!
                    pitch = nlt_pitch.transform(event.value)
                elif event.axis == 3: # right stick X axis (left/right) - will be 3 on linux devices, but another ID number on windows.
                    yaw = nlt_yaw.transform(event.value)
            elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed or depressed
                pass
        
        print("Throttle: " + str(throttle) + ", Pitch: " + str(pitch) + ", Roll: " + str(roll) + ", Yaw: " + str(yaw))

        # wait a moment
        time.sleep(0.05)