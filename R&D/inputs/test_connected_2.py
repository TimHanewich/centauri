import time
from inputs import DeviceManager, GamePad

# Problem flag
PROBLEM_FLAG:bool = True # start assuming we have to check for available controllers

# declare global DeviceManager up front
dm:DeviceManager = None

while True:
        

    # Validate a controller is connected
    while PROBLEM_FLAG:
        print("Problem Flag Raised")

        # declare DeviceManager
        print("Declaring DeviceManager...")
        try:
            dm = DeviceManager()
            print("DeviceManager declared successfully")
        except:
            print("Declaring DeviceManager failed.")

        # Scan for new controller?
        if dm != None:
            if len(dm.gamepads) > 0: # if there is at least one connected gamepad (controller)...
                print("Controller connected!")
                PROBLEM_FLAG = False # lower the problem flag
            else:
                print("No controllers connected")
        
        # sleep
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
