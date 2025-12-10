from inputs import get_gamepad

print("Not listening for events!")
while True:
    events = get_gamepad()
    for event in events:
        #print("Event Type: " + str(event.ev_type) + ", Event Code: " + str(event.code) + ", Event State: " + str(event.state))
        if event.ev_type == "Absolute":
            if event.code == "ABS_RZ":
                print(str(event.state))