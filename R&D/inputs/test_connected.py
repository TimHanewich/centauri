import time
import inputs

while True:
    gamepads = inputs.devices.gamepads
    if gamepads == None:
        print("No gamepads connected")
    else:
        print(str(len(gamepads)) + " gamepads connected: ")
        for gp in gamepads:
            print(gp.name)
    print()
    time.sleep(0.5)