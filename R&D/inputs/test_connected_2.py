import time
from inputs import DeviceManager, GamePad

# declare global DeviceManager we will use throughout this script
dm:DeviceManager = DeviceManager()

while True:
    
    # Validate a controller is connected
    while len(dm.gamepads) == 0:
        print("No gamepad connected!")
        dm = DeviceManager() # "refresh" the device manager so it gets a new read on connected devices
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
        print("ERROR!!!!!!!!")
