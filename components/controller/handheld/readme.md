# Mobile System
The mobile system has two source code repos:
1. A lightweight script that runs on a Raspberry Pi w/ a full OS installed (i.e. RPi 3B or RPi Zero) that is *solely* intended for reading game controller inputs and providing those to a Pico microcontroller.
2. Microcontroller code that runs on a Raspberry Pi Pico, accepts the controller input from the RPi, displays data on a SSD1306, and handles communication with the drone.

## Pi --> Pico Control Input Communication Protocol
- "Normal operations" packet (working correctly) - A total of **16 bytes**. So at 30 packets per second, that is 480 bytes per second.
    - Button Byte (1 byte)
        - Bit 7: `0` (packet identifier)
        - Bit 6: *reserved*
        - Bit 5: Left Stick Click
        - Bit 4: Right Stick Click
        - Bit 3: Back ("select"?) Button
        - Bit 2: Start Button
        - Bit 1: A
        - Bit 0: B
    - Button Byte (1 byte)
        - Bit 7: X
        - Bit 6: Y
        - Bit 5: D-Pad Up
        - Bit 4: D-Pad Right
        - Bit 3: D-Pad Down
        - Bit 2: D-Pad Left
        - Bit 1: Left Bumper
        - Bit 0: Right Bumper
    - Left Stick X (2 bytes)
    - Left Stick Y (2 bytes)
    - Right Stick X (2 bytes)
    - Right Stick Y (2 bytes)
    - Left Trigger (2 bytes)
    - Right Trigger (2 bytes)
    - "\r\n" terminator (2 bytes)
- Message Packet
    - Header byte (1 byte)
        - Bit 7: `1` = identifies as info packet
        - Bit 6: *reserved*
        - Bit 5: *reserved*
        - Bit 4: *reserved*
        - Bit 3: *reserved*
        - Bit 2: *reserved*
        - Bit 1: Controller Disconnected Flag (indicates problem with controller input)
        - Bit 0: "now online" flag - just sent once at boot to confirm the script is running
    - "\r\n" terminator (2 bytes)