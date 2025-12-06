import time
from inputs import DeviceManager, GamePad

# Problem flag
PROBLEM_FLAG:bool = False

while True:

    # declare global DeviceManager we will use throughout this script
    dm:DeviceManager = DeviceManager()

    # Validate a controller is connected
    while len(dm.gamepads) == 0 or PROBLEM_FLAG:
        print("No gamepad connected!")
        dm = DeviceManager() # "refresh" the device manager so it gets a new read on connected devices
        if len(dm.gamepads) > 0: # if there is at least one connected gamepad (controller)...
            PROBLEM_FLAG = False # lower the problem flag
        else:
            time.sleep(1.0)

    # select the gamepad we will use
    gamepad:GamePad = dm.gamepads[0]

    # Read inputs from it
    print("Now listening!")
    try:
        while True:
            events = gamepad.read()
            for event in events:
                print(str(event))
    except:
        PROBLEM_FLAG = True
