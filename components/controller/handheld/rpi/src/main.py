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
input_a:bool = False
input_b:bool = False
input_y:bool = False
input_x:bool = False
input_dpad_up:bool = False
input_dpad_right:bool = False
input_dpad_down:bool = False
input_dpad_left:bool = False
input_right_bumper:bool = False
input_left_bumper:bool = False
input_left_stick_x:float = 0.0      # -1.0 to 1.0 for left stick right/left
input_left_stick_y:float = 0.0      # -1.0 to 1.0 for left stick up/down
input_right_stick_x:float = 0.0     # -1.0 to 1.0 for right stick right/left
input_right_stick_y:float = 0.0     # -1.0 to 1.0 for right stick up/down
input_right_trigger:float = 0.0     # 0.0 to 1.0 for right trigger
input_left_trigger:float = 0.0      # 0.0 to 1.0 for left trigger

# start reading from it!
print("NOW READING FROM XBOX CONTROLLER!")
while True:

    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger
            print(str(event.axis))
            # if event.axis == 5: # right trigger
            #     input_right_trigger = (event.value + 1.0) / 2.0 # gets it to between 0.0 and 1.0
            # elif event.axis == 0: # left stick X axis (left/right)
            #     input_left_stick_x = event.value
            # elif event.axis == 1: # left stick Y axis (up/down)
            #     # pushing the left stick forward will result in a NEGATIVE value. While this may seem incorrect at first, it is actually correct... pushing the left stick forward should prompt the quadcopter to pitch down (forward), hence it should be negative!
            #     input_left_stick_y = event.value
            # elif event.axis == 3: # right stick X axis (left/right) - will be 3 on linux devices, but another ID number on windows.
            #     yaw = event.value
        elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed or depressed
            print(str(event.button))
            print(str(event))
            
            # Button ID's below
            # A = 0
            # B = 1
            # X = 2
            # Y = 3 
            # RB = 5 
            # LB = 4 
        else:
            print("Unknown event: " + str(event))

            
    
    

    # wait a moment
    time.sleep(0.05)