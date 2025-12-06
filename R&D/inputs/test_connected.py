import time
from inputs import DeviceManager

def count_connected_gamepads() -> int:
    dm:DeviceManager = DeviceManager() # creating a new one "refreshes" and updates connections
    return len(dm.gamepads)

while True:
    t1 = time.time_ns()
    concount:int = count_connected_gamepads()
    t2 = time.time_ns()
    print("Connected devices: " + str(count_connected_gamepads()) + " (took " + str(t2 - t1) + " ns to check)")
    time.sleep(1.0)