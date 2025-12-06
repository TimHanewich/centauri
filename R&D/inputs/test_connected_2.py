import time
from inputs import DeviceManager, GamePad
from typing import List

PROBLEM_FLAG:bool = True # Start assuming we need to check for a connection

while True:
    
    # 1. Connection Monitoring Loop
    dm:DeviceManager = DeviceManager()
    gamepads:List[GamePad] = dm.gamepads

    while len(gamepads) == 0:
        print("No gamepad connected. Retrying in 1s...")
        time.sleep(1.0)
        # Re-instantiate the DeviceManager to refresh the connection list
        dm = DeviceManager() 
        gamepads = dm.gamepads
        
    # If we exit the inner loop, a gamepad is connected.
    PROBLEM_FLAG = False
    gamepad:GamePad = gamepads[0]

    # 2. Input Reading Loop
    print("Gamepad connected! Now listening...")
    try:
        while True:
            # This read is blocking until an event occurs
            events = gamepad.read()
            for event in events:
                print(str(event))
    
    except Exception as e:
        # Catch any exception (like controller unplugged)
        print(f"Reading error caught: {e}. Reverting to connection check.")
        PROBLEM_FLAG = True # Set flag to force the outer loop to re-scan