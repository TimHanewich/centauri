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

    # Read the raw data and update the variables we are using to track
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger

            # Xbox Controller Axes (on linux)
            # Left Stick X axis (left/right) = 0
            # Left Stick Y axis (up/down) = 1
            # Right Stick X axis (left/right) = 3
            # Right Stick Y axis (up/down) = 4
            # Right Trigger = 5
            # Left Trigger = 2

            if event.axis == 0: # Left Stick X axis (left/right)
                input_left_stick_x = event.value
            elif event.axis == 1: # Left Stick Y axis (up/down)
                input_left_stick_y = event.value
            elif event.axis == 3: # Right Stick X axis
                input_right_stick_x = event.value
            elif event.axis == 4: # Right stick Y axis
                input_right_stick_y = event.value
            elif event.axis == 2: # left trigger
                input_left_trigger = (event.value + 1.0) / 2.0 # gets it to between 0.0 and 1.0
            elif event.axis == 5: # right trigger
                input_right_trigger = (event.value + 1.0) / 2.0 # gets it to between 0.0 and 1.0

        elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed down
            
            # Button ID's below
            # A = 0
            # B = 1
            # X = 2
            # Y = 3 
            # RB = 5 
            # LB = 4

            if event.button == 0:
                input_a = True
            elif event.button == 1:
                input_b = True
            elif event.button == 2:
                input_x = True
            elif event.button == 3:
                input_y = True
            elif event.button == 4:
                input_left_bumper = True
            elif event.button == 5:
                input_right_bumper = True

        elif event.type == pygame.JOYBUTTONUP: # a button was depressed (stopped being pressed)
            if event.button == 0:
                input_a = False
            elif event.button == 1:
                input_b = False
            elif event.button == 2:
                input_x = False
            elif event.button == 3:
                input_y = False
            elif event.button == 4:
                input_left_bumper = False
            elif event.button == 5:
                input_right_bumper = False
        elif event.type == pygame.JOYHATMOTION: # D-Pad

            # "value" looks something like (-1, 1)
            # first value in the tuple represents Left/Right Dpad. -1 would mean left down, 1 mean right down, 0 mean neither down
            # second value in the tuple represents up/down Dpad. -1 would mean down is down, 1 mean up is down.
            
            # Check left/right
            if event.value[0] == -1:
                input_dpad_left = True
                input_dpad_right = False
            elif event.value[0] == 1:
                input_dpad_left = False
                input_dpad_right = True
            else: # neither are pressed (0)
                input_dpad_left = False
                input_dpad_right = False

            # Check Up/Down
            if event.value[1] == -1:
                input_dpad_down = True
                input_dpad_up = False
            elif event.value[1] == 1:
                input_dpad_down = False
                input_dpad_up = True
            else: # neither are pressed (0)
                input_dpad_down = False
                input_dpad_up = False
            
        else:
            pass
            #print("Unknown event: " + str(event))

    # print
    if True:
        ToPrint:dict = {}
        ToPrint["a"] = input_a
        ToPrint["b"] = input_b
        ToPrint["x"] = input_x
        ToPrint["y"] = input_y
        ToPrint["up"] = input_dpad_up
        ToPrint["right"] = input_dpad_right
        ToPrint["down"] = input_dpad_down
        ToPrint["left"] = input_dpad_left
        ToPrint["lb"] = input_left_bumper
        ToPrint["rb"] = input_right_bumper
        ToPrint["lt"] = input_left_trigger
        ToPrint["rt"] = input_right_trigger
        ToPrint["left_x"] = input_left_stick_x
        ToPrint["left_y"] = input_left_stick_y
        ToPrint["right_x"] = input_right_stick_x
        ToPrint["right_y"] = input_right_stick_y
        print(str(ToPrint))
    

    # wait a moment
    time.sleep(0.05)