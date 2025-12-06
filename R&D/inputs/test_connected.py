import time
from inputs import get_gamepad

while True:
    
    try:
        events = get_gamepad()
        print(str(time.time()) + ": " + str(len(events)) + " received")
    except:
        print(str(time.time()) + ": Failed!")

    time.sleep(0.5)