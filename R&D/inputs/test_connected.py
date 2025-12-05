import inputs

def get_gamepads():
    return inputs.devices.gamepads

while True:
    gamepads = get_gamepads()
    if not gamepads:
        print("No gamepad connected.")
    else:
        print(f"{len(gamepads)} gamepad(s) connected.")
