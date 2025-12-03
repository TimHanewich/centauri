import pygame
import time
import serial
from tools import Joystick, pack_button_input_event, pack_joystick_input_event, Button

# Set up serial communication that will later be used to send data to the connected device via UART
serport:str = "/dev/ttyS0"
print("Opening serial port on '" + serport + "'...")
ser = serial.Serial(serport, 9600)
print("Serial port opened!")

def FOREVER_BROADCAST_PROBLEM_FLAG() -> None:
    PROBLEM_MSG:bytes = b'@\r\n' # this is 0b010000 followed by \r\n (3 bytes). What we will transmit to indicate a problem encountered
    while True:
        print("Broadcasting problem error @ time " + str(int(time.time())) + "...")
        ser.write(PROBLEM_MSG)
        time.sleep(1.0)

# Set up controller
print("Initializing pygame module...")
pygame.init()
pygame.joystick.init()

# count number of connected joysticks (gamepads)
num_joysticks:int = pygame.joystick.get_count()
print("Number of connected controllers: " + str(num_joysticks))
if num_joysticks == 0:
    print("No controller connected! Must connect a controller.")
    FOREVER_BROADCAST_PROBLEM_FLAG()

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
try:
    print("NOW READING FROM XBOX CONTROLLER!")
    while True:

        # Read the raw data and update the variables we are using to track
        for event in pygame.event.get():

            print(str(event))

            # declare a binary message we will encode and then send to the attached pico via UART
            EventEncoded:bytes = None

            if event.type == pygame.JOYAXISMOTION: # it has to do with a variable input, like a joystick or trigger

                # Xbox Controller Axes (on linux)
                # Left Stick X axis (left/right) = 0
                # Left Stick Y axis (up/down) = 1
                # Right Stick X axis (left/right) = 3
                # Right Stick Y axis (up/down) = 4
                # Right Trigger = 5
                # Left Trigger = 2

                if event.axis == 0: # Left Stick X axis (left/right)
                    value:float = min(max(event.value, -1.0), 1.0)
                    EventEncoded = pack_joystick_input_event(Joystick.LS_X, value)
                elif event.axis == 1: # Left Stick Y axis (up/down)     IMPORTANT NOTE: y-axis all the way up is -1.0 and all the way down is 1.0. This may seem backwards, but for the sake of like pitch, pushing forward should mean negative pitch rate is wanted, so I am leaving it as is.
                    value:float = min(max(event.value, -1.0), 1.0)
                    EventEncoded = pack_joystick_input_event(Joystick.LS_Y, value)
                elif event.axis == 3: # Right Stick X axis
                    value:float = min(max(event.value, -1.0), 1.0)
                    EventEncoded = pack_joystick_input_event(Joystick.RS_X, value)
                elif event.axis == 4: # Right Stick Y axis (up/down)     IMPORTANT NOTE: y-axis all the way up is -1.0 and all the way down is 1.0. This may seem backwards, but for the sake of like pitch, pushing forward should mean negative pitch rate is wanted, so I am leaving it as is.
                    value:float = min(max(event.value, -1.0), 1.0)
                    EventEncoded = pack_joystick_input_event(Joystick.RS_Y, value)
                elif event.axis == 2: # left trigger
                    value:float = min(max((event.value + 1.0) / 2.0, 0.0), 1.0) # gets it to between 0.0 and 1.0
                    EventEncoded = pack_joystick_input_event(Joystick.LT, value)
                elif event.axis == 5: # right trigger
                    value:float = min(max((event.value + 1.0) / 2.0, 0.0), 1.0) # gets it to between 0.0 and 1.0
                    EventEncoded = pack_joystick_input_event(Joystick.RT, value)

            elif event.type == pygame.JOYBUTTONDOWN: # a button was pressed down
                
                # PyGame's Button ID's below
                # A = 0
                # B = 1
                # X = 2
                # Y = 3 
                # RB = 5 
                # LB = 4
                # Left Stick clicked down = 9
                # Right stick clicked down = 10
                # "Back" button ("select"?) = 6
                # Start button = 7
                # Share button (on Xbox Series S/X controllers only) = 11

                if event.button == 0:
                    EventEncoded = pack_button_input_event(Button.A)
                    print("Got an A press event!")
                elif event.button == 1:
                    EventEncoded = pack_button_input_event(Button.B)
                elif event.button == 2:
                    iEventEncoded = pack_button_input_event(Button.X)
                elif event.button == 3:
                    EventEncoded = pack_button_input_event(Button.Y)
                elif event.button == 4:
                    EventEncoded = pack_button_input_event(Button.LB)
                elif event.button == 5:
                    EventEncoded = pack_button_input_event(Button.RB)
                elif event.button == 9:
                    EventEncoded = pack_button_input_event(Button.LS)
                elif event.button == 10:
                    EventEncoded = pack_button_input_event(Button.RS)
                elif event.button == 6:
                    EventEncoded = pack_button_input_event(Button.Back)
                elif event.button == 7:
                    EventEncoded = pack_button_input_event(Button.Start)

            elif event.type == pygame.JOYHATMOTION: # D-Pad

                # "value" looks something like (-1, 1)
                # first value in the tuple represents Left/Right Dpad. -1 would mean left down, 1 mean right down, 0 mean neither down
                # second value in the tuple represents up/down Dpad. -1 would mean down is down, 1 mean up is down.
                
                # Check left/right
                if event.value[0] == -1:
                    EventEncoded = pack_button_input_event(Button.Left)
                elif event.value[0] == 1:
                    EventEncoded = pack_button_input_event(Button.Right)

                # Check Up/Down
                if event.value[1] == -1:
                    EventEncoded = pack_button_input_event(Button.Down)
                elif event.value[1] == 1:
                    EventEncoded = pack_button_input_event(Button.Up)

            # Something to send?
            if EventEncoded != None:
                ser.write(EventEncoded) # yes, it will already contain \r\n
                print(str(EventEncoded))

        # wait a moment
        time.sleep(0.01)
        
except Exception as ex:
    print("FATAL ERROR: " + str(ex))
    raise ex
    FOREVER_BROADCAST_PROBLEM_FLAG()