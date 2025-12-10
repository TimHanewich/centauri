import pygame
import time

# Initialize pygame and joystick module
print("Initializing pygame for controller reads...")
pygame.init()
pygame.joystick.init()

# count how many controllers (joysticks) are connected
num_joysticks = pygame.joystick.get_count()
print("Number of connected controllers: " + str(num_joysticks))
if num_joysticks == 0:
    print("No controllers connected! You must connect one before proceeding.")
    exit()

# loop through each controller
for i in range(num_joysticks):
    tjs = pygame.joystick.Joystick(i)
    tjs.init()
    print("Joystick " + str(i) + ": " + tjs.get_name())

# select the controller that will be used
controller = pygame.joystick.Joystick(0)
controller.init()
print("Controller #0, '" + controller.get_name() + "' will be used.")

# set up control input variables we will send to the drone (and display in the console!)
armed:bool = False
mode:bool = False
throttle:float = 0.0 # 0.0 to 1.0
pitch:float = 0.0
roll:float = 0.0
yaw:float = 0.0

# infinite loop of reading
while True:

    # handle changes in input state on the Xbox controller
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 5: # right trigger
                throttle = (event.value + 1) / 2
            elif event.axis == 0: # left stick X axis (left/right)
                roll = event.value
            elif event.axis == 1: # left stick Y axis (up/down)
                pitch = event.value # pushing the left stick forward will result in a NEGATIVE value. While this may seem incorrect at first, it is actually correct... pushing the left stick forward should prompt the quadcopter to pitch down (forward), hence it should be negative!
            elif event.axis == 2: # right stick X axis (left/right)
                yaw = event.value
            else:
                print("Axis '" + str(event.axis) + "': " + str(event.value))
                pass
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0: # A
                armed = True
            elif event.button == 1: # B
                armed = False
            elif event.button == 4: # LB
                mode = False # rate mode
            elif event.button == 5: # RB
                mode = True # angle mode
            else:
                #print("Button pressed: " + str(event.button))
                pass
    
    # print
    #print("Armed: " + str(armed) + ", mode: " + str(mode) + ", throttle: " + str(throttle) + ", pitch: " + str(pitch) + ", roll: " + str(roll) + ", yaw: " + str(yaw)) 

    # wait
    time.sleep(0.01)