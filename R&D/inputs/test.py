from inputs import get_gamepad

while True:
    events = get_gamepad()
    for event in events:
        print("Event Type: " + str(event.ev_type) + ", Event Code: " + str(event.code) + ", Event State: " + str(event.state))
        if event.ev_type == "Key": # button press
            if event.code == "BTN_SOUTH": # A
                if event.state == 1:
                    print("A Button Down")
                else:
                    print("A Button Up")
            elif event.code == "BTN_EAST":  # B
                if event.state == 1:
                    print("B Button Down")
                else:
                    print("B Button Up")
            elif event.code == "BTN_NORTH": # X (Yes, it should be Y, but on the Xbox Series X/S controller I am using, North and West are swapped for some reason...)
                if event.state == 1:
                    print("X Button Down")
                else:
                    print("X Button Up")
            elif event.code == "BTN_WEST": # Y (Yes, it should be X, but on the Xbox Series X/S controller I am using, North and West are swapped for some reason...)
                if event.state == 1:
                    print("Y Button Down")
                else:
                    print("Y Button Up")
            elif event.code == "BTN_TL":  # Left bumper (LB)
                if event.state == 1:
                    print("Left Bumper Down")
                else:
                    print("Left Bumper Up")
            elif event.code == "BTN_TR":  # Right bumper (RB)
                if event.state == 1:
                    print("Right Bumper Down")
                else:
                    print("Right Bumper Up")
            elif event.code == "BTN_SELECT":  # Back / View
                if event.state == 1:
                    print("Back Button Down")
                else:
                    print("Back Button Up")
            elif event.code == "BTN_START":  # Start / Menu
                if event.state == 1:
                    print("Start Button Down")
                else:
                    print("Start Button Up")
            elif event.code == "BTN_THUMBL":  # Left stick click
                if event.state == 1:
                    print("Left Stick Button Down")
                else:
                    print("Left Stick Button Up")
            elif event.code == "BTN_THUMBR":  # Right stick click
                if event.state == 1:
                    print("Right Stick Button Down")
                else:
                    print("Right Stick Button Up")
            elif event.code == "BTN_MODE":  # Xbox Guide button
                if event.state == 1:
                    print("Guide Button Down")
                else:
                    print("Guide Button Up")

        elif event.ev_type == "Absolute": # Variable input (i.e. triggers, joysticks X/Y axis) or D-Pad
            pass