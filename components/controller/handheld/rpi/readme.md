# Pi Code
Just a lightweight script for reading controller input and then providing that to the Pi Pico via UART.

## Pi --> Pico Control Input Communication Protocol
A total of **16 bytes**. So at 30 packets per second, that is 480 bytes per second.
- Button Byte (1 byte)
    - Bit 7: *reserved*
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



