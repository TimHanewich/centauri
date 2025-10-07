# Controlling with Xbox Controller

## Mapping
- Throttle = Right Trigger
- Pitch = left stick Y axis (up/down)
- Roll = left stick X axis (left/right)
- Yaw = right stick X axis (left/right)
- A button = arm (motors on, at least idling at low RPM but no thrust)
- B button = disarm (motors off)
- LB = select rate mode
- RB = select angle (attitude) mode

## Displayed on screen
- Other info
    - Packets received
    - Packet last received (ms ago)
    - Packets sent
- Controls being sent
    - Control mode
    - Armed
    - Throttle
    - Pitch
    - Roll
    - Yaw
- Quadcopter status
    - Status
        - Quadcopter battery level
        - M1 throttle
        - M2 throttle
        - M3 throttle
        - M4 throttle
        - Actual roll rate
        - Actual pitch rate
        - Actual yaw rate
        - Pitch angle estimate
        - Roll angle estime
        - TF Luna reading (on belly)
        - BMP180 reading
        - QMC5883L
    - Messages (unstructured data, in text)
        - Time it came in and message (in text)