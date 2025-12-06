import time
from inputs import DeviceManager, GamePad

# Problem flag
PROBLEM_FLAG:bool = True # start assuming we have to check for available gamepads

while True:
        

    # Select a gamepad that will be used to read from
    gamepad:GamePad = None
    while gamepad == None:
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
                gamepad = dm.gamepads[0] # plug in what gamepad we will use
                PROBLEM_FLAG = False # lower the problem flag
            else:
                print("No controllers connected")
        
        # sleep
        time.sleep(1.0)

    # Read inputs from it
    print("Now listening!")
    try:
        while True:
            events = gamepad.read()
            for event in events:
                print(str(event))
    except:
        pass
