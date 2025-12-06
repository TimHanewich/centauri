import time
from inputs import DeviceManager

def count_connected_gamepads() -> int:
    dm:DeviceManager = DeviceManager() # creating a new one "refreshes" and updates connections
    return len(dm.gamepads)

while True:
    print("Connected devices: " + str(count_connected_gamepads()))
    time.sleep(1.0)