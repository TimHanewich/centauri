from inputs import devices
import time

# Get list of gamepads
gamepads = devices.gamepads

# select the controller we will use
my_controller = gamepads[0]

while True:
    events = my_controller.read()
    print("Events: " + str(events))
    time.sleep(0.25)