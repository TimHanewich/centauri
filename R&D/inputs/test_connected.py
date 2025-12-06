import time
from inputs import get_gamepad

while True:
    
    try:
        events = get_gamepad()
        print(str(len(events)) + " received")
    except:
        print("Failed!")

    time.sleep(0.5)