from inputs import get_gamepad

print("Not listening for events!")
while True:
    events = get_gamepad()
    for event in events:
        print("Event Type: " + str(event.ev_type) + ", Event Code: " + str(event.code) + ", Event State: " + str(event.state))