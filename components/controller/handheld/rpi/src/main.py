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
    PROBLEM_MSG:bytes = b'@\r\n' # this is 0b01000000 followed by \r\n (3 bytes). What we will transmit to indicate a problem encountered
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

# declare a bytearray we will append stuff to send to and then clear
ToSend:bytearray = bytearray()

# start reading from it!
try:
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
                    value:float = min(max(event.value, -1.0), 1.0)
                    ToSend.extend(pack_joystick_input_event(Joystick.LS_X, value))
                elif event.axis == 1: # Left Stick Y axis (up/down)     IMPORTANT NOTE: y-axis all the way up is -1.0 and all the way down is 1.0. This may seem backwards, but for the sake of like pitch, pushing forward should mean negative pitch rate is wanted, so I am leaving it as is.
                    value:float = min(max(event.value, -1.0), 1.0)
                    ToSend.extend(pack_joystick_input_event(Joystick.LS_Y, value))
                elif event.axis == 3: # Right Stick X axis
                    value:float = min(max(event.value, -1.0), 1.0)
                    ToSend.extend(pack_joystick_input_event(Joystick.RS_X, value))
                elif event.axis == 4: # Right Stick Y axis (up/down)     IMPORTANT NOTE: y-axis all the way up is -1.0 and all the way down is 1.0. This may seem backwards, but for the sake of like pitch, pushing forward should mean negative pitch rate is wanted, so I am leaving it as is.
                    value:float = min(max(event.value, -1.0), 1.0)
                    ToSend.extend(pack_joystick_input_event(Joystick.RS_Y, value))
                elif event.axis == 2: # left trigger
                    value:float = min(max((event.value + 1.0) / 2.0, 0.0), 1.0) # gets it to between 0.0 and 1.0
                    ToSend.extend(pack_joystick_input_event(Joystick.LT, value))
                elif event.axis == 5: # right trigger
                    value:float = min(max((event.value + 1.0) / 2.0, 0.0), 1.0) # gets it to between 0.0 and 1.0
                    ToSend.extend(pack_joystick_input_event(Joystick.RT, value))

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
                    ToSend.extend(pack_button_input_event(Button.A, True))
                elif event.button == 1:
                    ToSend.extend(pack_button_input_event(Button.B, True))
                elif event.button == 2:
                    ToSend.extend(pack_button_input_event(Button.X, True))
                elif event.button == 3:
                    ToSend.extend(pack_button_input_event(Button.Y, True))
                elif event.button == 4:
                    ToSend.extend(pack_button_input_event(Button.LB, True))
                elif event.button == 5:
                    ToSend.extend(pack_button_input_event(Button.RB, True))
                elif event.button == 9:
                    ToSend.extend(pack_button_input_event(Button.LS, True))
                elif event.button == 10:
                    ToSend.extend(pack_button_input_event(Button.RS, True))
                elif event.button == 6:
                    ToSend.extend(pack_button_input_event(Button.Back, True))
                elif event.button == 7:
                    ToSend.extend(pack_button_input_event(Button.Start, True))

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    ToSend.extend(pack_button_input_event(Button.A, False))
                elif event.button == 1:
                    ToSend.extend(pack_button_input_event(Button.B, False))
                elif event.button == 2:
                    ToSend.extend(pack_button_input_event(Button.X, False))
                elif event.button == 3:
                    ToSend.extend(pack_button_input_event(Button.Y, False))
                elif event.button == 4:
                    ToSend.extend(pack_button_input_event(Button.LB, False))
                elif event.button == 5:
                    ToSend.extend(pack_button_input_event(Button.RB, False))
                elif event.button == 9:
                    ToSend.extend(pack_button_input_event(Button.LS, False))
                elif event.button == 10:
                    ToSend.extend(pack_button_input_event(Button.RS, False))
                elif event.button == 6:
                    ToSend.extend(pack_button_input_event(Button.Back, False))
                elif event.button == 7:
                    ToSend.extend(pack_button_input_event(Button.Start, False))

            elif event.type == pygame.JOYHATMOTION: # D-Pad

                # "value" looks something like (-1, 1)
                # first value in the tuple represents Left/Right Dpad. -1 would mean left down, 1 mean right down, 0 mean neither down
                # second value in the tuple represents up/down Dpad. -1 would mean down is down, 1 mean up is down.
                # yes, due to the way this works, D-pad is technically the most bandwidth-intensive thing... I wish it was just the normal button up/down!

                # Check left/right
                if event.value[0] == -1:
                    ToSend.extend(pack_button_input_event(Button.Left, True))
                elif event.value[0] == 1:
                    ToSend.extend(pack_button_input_event(Button.Right, True))
                else: # they are both now NOT pressed
                    ToSend.extend(pack_button_input_event(Button.Left, False))
                    ToSend.extend(pack_button_input_event(Button.Right, False))

                # Check Up/Down
                if event.value[1] == -1:
                    ToSend.extend(pack_button_input_event(Button.Down, True))
                elif event.value[1] == 1:
                    ToSend.extend(pack_button_input_event(Button.Up, True))
                else: # they are both now NOT pressed
                    ToSend.extend(pack_button_input_event(Button.Down, False))
                    ToSend.extend(pack_button_input_event(Button.Up, False))

            # Something to send?
            if len(ToSend) > 0:
                ser.write(ToSend)  # send
                ToSend.clear()     # clear

        # wait a moment
        time.sleep(0.01)

except Exception as ex:
    print("FATAL ERROR: " + str(ex))
    FOREVER_BROADCAST_PROBLEM_FLAG()