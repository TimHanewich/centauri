from inputs import get_gamepad
import time
import serial
from tools import pack_controls

# Set up serial communication that will later be used to send data to the connected device via UART
serport:str = "/dev/ttyS0"
print("Opening serial port on '" + serport + "'...")
ser = serial.Serial(serport, 115200)
print("Serial port opened!")

def FOREVER_BROADCAST_PROBLEM_FLAG() -> None:
    PROBLEM_MSG:bytes = b'@\r\n' # this is 0b01000000 followed by \r\n (3 bytes). What we will transmit to indicate a problem encountered
    while True:
        print("Broadcasting problem error @ time " + str(int(time.time())) + "...")
        ser.write(PROBLEM_MSG)
        time.sleep(1.0)

# Declare control input variables
input_left_stick_click:bool = False
input_right_stick_click:bool = False
input_back:bool = False # the "back" button (or is it called "select"?)... to the left of the Xbox logo
input_start:bool = False
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

# Timestamps
snapshot_last_sent:float = 0.0 # time.time() timestamp of when a snapshot was last sent. We will use this to send it every so many seconds (or milliseconds)

# Just before starting, transmit "HELLO\r\n" to confirm we are online and ready to go
print("Transmitting 'HELLO' online message...")
ser.write(b"HELLO\r\n")

# start reading from it!
try:
    print("NOW READING FROM XBOX CONTROLLER!")
    while True:

        # Read the raw data and update the variables we are using to track
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key": # button press
                if event.code == "BTN_SOUTH": # A
                    if event.state == 1:
                        input_a = True
                    else:
                        input_a = False
                elif event.code == "BTN_EAST":  # B
                    if event.state == 1:
                        input_b = True
                    else:
                        input_b = False
                elif event.code == "BTN_NORTH": # X (Yes, it should be Y, but on the Xbox Series X/S controller I am using, North and West are swapped for some reason...)
                    if event.state == 1:
                        input_x = True
                    else:
                        input_x = False
                elif event.code == "BTN_WEST": # Y (Yes, it should be X, but on the Xbox Series X/S controller I am using, North and West are swapped for some reason...)
                    if event.state == 1:
                        input_y = True
                    else:
                        input_y = False
                elif event.code == "BTN_TL":  # Left bumper (LB)
                    if event.state == 1:
                        input_left_bumper = True
                    else:
                        input_left_bumper = False
                elif event.code == "BTN_TR":  # Right bumper (RB)
                    if event.state == 1:
                        input_right_bumper = True
                    else:
                        input_right_bumper = False
                elif event.code == "BTN_SELECT":  # Back / View
                    if event.state == 1:
                        input_back = True
                    else:
                        input_back = False
                elif event.code == "BTN_START":  # Start / Menu
                    if event.state == 1:
                        input_start = True
                    else:
                        input_start = False
                elif event.code == "BTN_THUMBL":  # Left stick click
                    if event.state == 1:
                        input_left_stick_click = True
                    else:
                        input_left_stick_click = False
                elif event.code == "BTN_THUMBR":  # Right stick click
                    if event.state == 1:
                        input_right_stick_click = True
                    else:
                        input_right_stick_click = False
            elif event.ev_type == "Absolute": # Variable input (i.e. triggers, joysticks X/Y axis) or D-Pad. See event code + value range map here: https://i.imgur.com/ql8nDnc.png
                if event.code == "ABS_X": # Left Stick X
                    value:float = min(max(event.state / 32767.0, -1.0), 1.0) # normalize to between -1.0 and 1.0. Must do min/max in case -32768 (int16 min value) is the value
                    input_left_stick_x = value
                elif event.code == "ABS_Y": # Left Stick Y
                    value:float = min(max(event.state / 32767.0, -1.0), 1.0) # normalize to between -1.0 and 1.0. Must do min/max in case -32768 (int16 min value) is the value
                    input_left_stick_y = value
                elif event.code == "ABS_RX": # Right Stick X
                    value:float = min(max(event.state / 32767.0, -1.0), 1.0) # normalize to between -1.0 and 1.0. Must do min/max in case -32768 (int16 min value) is the value
                    input_right_stick_x = value
                elif event.code == "ABS_RY": # Right Stick Y
                    value:float = min(max(event.state / 32767.0, -1.0), 1.0) # normalize to between -1.0 and 1.0. Must do min/max in case -32768 (int16 min value) is the value
                    input_right_stick_y = value
                elif event.code == "ABS_Z": # Left Trigger
                    value:float = event.state / 1023.0 # range is 0 to 1023
                    input_left_trigger = value
                elif event.code == "ABS_RZ": # Right Trigger
                    value:float = event.state / 1023.0 # range is 0 to 1023
                    input_right_trigger = value
                elif event.code == "ABS_HAT0X": # D-pad left and right
                    if event.state == -1:
                        input_dpad_left = True
                        input_dpad_right = False
                    elif event.state == 1:
                        input_dpad_left = False
                        input_dpad_right = True
                    else: # 0 means both Left/Right are up (not pressed)
                        input_dpad_left = False
                        input_dpad_right = False
                elif event.code == "ABS_HAT0Y": # D-pad up and down
                    if event.state == -1:
                        input_dpad_up = True
                        input_dpad_down = False
                    elif event.state == 1:
                        input_dpad_up = False
                        input_dpad_down = True
                    else: # 0 means both Up/Down are up (not pressed)
                        input_dpad_up = False
                        input_dpad_down = False

        print("RT: " + str(input_right_trigger))
            
        # print (change to True for debugging purposes)
        if False:
            ToPrint:dict = {}
            ToPrint["ls"] = input_left_stick_click
            ToPrint["rs"] = input_right_stick_click
            ToPrint["back"] = input_back
            ToPrint["start"] = input_start
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

        # time to send?
        time_since:float = time.time() - snapshot_last_sent
        print("Time since: " + str(time_since))
        if time_since >= 0.025: # send every 25 ms = 40 Hz
            packed:bytes = pack_controls(input_left_stick_click, input_right_stick_click, input_back, input_start, input_a, input_b, input_x, input_y, input_dpad_up, input_dpad_right, input_dpad_down, input_dpad_left, input_left_bumper, input_right_bumper, input_left_stick_x, input_left_stick_y, input_right_stick_x, input_right_stick_y, input_left_trigger, input_right_trigger)
            snapshot_last_sent = time.time()
            print(str(packed))
        
        # transmit via serial (UART)
        ser.write(packed)

        # wait a moment
        #time.sleep(0.025) # 40 hz = every 25 ms

except Exception as ex:
    print("FATAL ERROR: " + str(ex))
    FOREVER_BROADCAST_PROBLEM_FLAG()