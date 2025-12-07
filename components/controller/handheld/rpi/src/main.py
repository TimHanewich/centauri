from inputs import DeviceManager, GamePad
import time
import serial
import tools
import threading

# Set up serial communication that will later be used to send data to the connected device via UART
serport:str = "/dev/ttyS0"
baudrate:int = 9600
print("Opening serial port on '" + serport + "' at baudrate " + str(baudrate) + "...")
ser = serial.Serial(serport, baudrate)
print("Serial port opened!")
    
# Set up method to check number of controllers (to validate controller is connected)
def count_connected_gamepads() -> int:
    dm:DeviceManager = DeviceManager() # creating a new one "refreshes" and updates connections
    return len(dm.gamepads)

# Declare control input variables
PROBLEM_FLAG:bool = False # raised by the controller input read thread if there was a critical problem while collecting Controller input
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

# define continuous reading thread
def continuous_controller_read() -> None:

    # declare global vars
    global PROBLEM_FLAG
    global input_left_stick_click
    global input_right_stick_click
    global input_back
    global input_start
    global input_a
    global input_b
    global input_y
    global input_x
    global input_dpad_up
    global input_dpad_right
    global input_dpad_down
    global input_dpad_left
    global input_right_bumper
    global input_left_bumper
    global input_left_stick_x
    global input_left_stick_y
    global input_right_stick_x
    global input_right_stick_y
    global input_right_trigger
    global input_left_trigger

    while True:

        # Select a gamepad that will be used to read from
        gamepad:GamePad = None
        while gamepad == None:
            print("Gamepad is None. Going to try to find a connected gamepad...")
            PROBLEM_FLAG = True # if there isn't a gamepad, that means there is a problem. So the input data isn't reliable. So raise the problem flag so the thread transmitting the control data via UART knows!

            # Wait a moment
            print("Waiting a moment for things to settle...")
            for i in range(0, 3):
                print("Continuing in " + str(3 - i) + "...")
                time.sleep(1.0)

            # declare DeviceManager
            # Yes, we have to do it in a Try bracket because it does fail if it is trying to initiate right after a previous DeviceManager was working just fine. Example: https://i.imgur.com/xOKxtjn.png
            # Note - I discovered that it will only throw the try exception because it can't access a inputs file/folder that exists in the OS. But that folder/file is cleaned up shortly after unplugged. So building in the wait above waits for it to leave so the DeviceManger does not try to access it. So the wait alleviates the need for the Try around DeviceManager()... but leaving it in anyway
            print("Initiating DeviceManager...")
            dm:DeviceManager = None
            try:
                dm = DeviceManager()
                print("DeviceManager initiating successfully")
            except:
                print("Initiating new DeviceManager failed.")

            # Scan for new controller?
            if dm == None:
                print("DeviceManager did not initiate correctly, so skipping checking for gamepads.")
            else:
                print("Checking for connected gamepads...")
                if len(dm.gamepads) > 0: # if there is at least one connected gamepad (controller)...
                    print("At least one gamepad is connected! Setting up and lowering problem flag!")
                    gamepad = dm.gamepads[0] # plug in what gamepad we will use
                else:
                    print("No controllers connected")

        # continuously monitor and note controller events
        PROBLEM_FLAG = False # We got to this point, so lower the Problem Flag. Note: we can't do it AFTER gamepad.read() because gamepad.read() is blocking until some input arrives on the controller, so it could be seconds before it is received.
        try:
            while True:
                events = gamepad.read()
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
        except:
            PROBLEM_FLAG = True # raise the problem flag right away so the main thread that is transmitting data via UART knows RIGHT AWAY!

# fire up the continuous read thread
threading.Thread(target=continuous_controller_read, daemon=True).start() # daemon=True means it will also be killed when the main program terminates (i.e. keyboard interupt)

# Just before starting, transmit "Now Online" message to confirm we are ready to go
print("Transmitting 'Now Online' message...")
ser.write(tools.pack_message(tools.MessageType.NowOnline))

# start sending regularly on the main thread!
print("NOW OPERATING!")
while True:
        
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

    print("RT: " + str(input_right_trigger))

    # pack based on if we are operating normally or if there is a problem
    packed:bytes = None
    if PROBLEM_FLAG:
        packed = tools.pack_message(tools.MessageType.ControllerDisconnected)
    else: # operating normally... so pack the controls snapshot
        packed = tools.pack_controls_snapshot(input_left_stick_click, input_right_stick_click, input_back, input_start, input_a, input_b, input_x, input_y, input_dpad_up, input_dpad_right, input_dpad_down, input_dpad_left, input_left_bumper, input_right_bumper, input_left_stick_x, input_left_stick_y, input_right_stick_x, input_right_stick_y, input_left_trigger, input_right_trigger)

    # transmit via serial (UART)
    ser.write(packed)

    # wait a moment
    time.sleep(0.025) # 40 hz = every 25 ms