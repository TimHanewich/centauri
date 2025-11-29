import pygame
import time

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
armed:bool = False         # Controlled by Xbox A & B buttons
throttle:float = 0.0       # between 0.0 and 1.0
pitch:float = 0.0          # between -1.0 and 1.0
roll:float = 0.0           # between -1.0 and 1.0
yaw:float = 0.0            # between -1.0 and 1.0

while True:

    # start reading from it!
    print("NOW READING FROM XBOX CONTROLLER!")
    while True:

        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger
                if event.axis == 5: # right trigger
                    throttle = (event.value + 1.0) / 2.0 # gets it to between 0.0 and 1.0
                elif event.axis == 0: # left stick X axis (left/right)
                    roll = event.roll
                elif event.axis == 1: # left stick Y axis (up/down)
                    # pushing the left stick forward will result in a NEGATIVE value. While this may seem incorrect at first, it is actually correct... pushing the left stick forward should prompt the quadcopter to pitch down (forward), hence it should be negative!
                    pitch = event.value
                elif event.axis == 3: # right stick X axis (left/right) - will be 3 on linux devices, but another ID number on windows.
                    yaw = event.value
            elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed or depressed
                if event.button == 0: # A
                    armed = True
                elif event.button == 1: # B
                    armed = False
        
        print("ARMED:" + str(armed) + ", Throttle: " + str(throttle) + ", Pitch: " + str(pitch) + ", Roll: " + str(roll) + ", Yaw: " + str(yaw))

        # wait a moment
        time.sleep(0.05)