from inputs import get_gamepad
import threading
import time

a_btn:bool = False

def continuous_read() -> None:
    global a_btn
    while True:
        events = get_gamepad()
        for event in events:
            if event.code == "BTN_SOUTH": # A
                if event.state == 1:
                    a_btn = True
                else:
                    a_btn = False

# start read thread
threading.Thread(target=continuous_read, daemon=True).start()

# print statuses
while True:
    print("A Button: " + str(a_btn))
    time.sleep(1.0)