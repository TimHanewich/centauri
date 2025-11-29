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

# start reading from it!
print("NOW READING FROM XBOX CONTROLLER!")
while True:

    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger
            if event.axis == 5: # right trigger
                print("RT: " + str(event.value))
        elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed or depressed
            pass
    
    # wait a moment
    time.sleep(0.05)