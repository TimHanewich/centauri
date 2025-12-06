import time
from inputs import DeviceManager, GamePad

# Problem flag
PROBLEM_FLAG:bool = True # start assuming we have to check for available gamepads

while True:
        

    # Select a gamepad that will be used to read from
    gamepad:GamePad = None
    while gamepad == None:
        print("Problem Flag Raised")

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
        print("Error encountered while reading inputs from gamepad!")
