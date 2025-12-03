# Pi Code
Just a lightweight script for reading controller input and then providing that to the Pi Pico via UART.

## Pi --> Pico Control Input Communication Protocol
A total of **16 bytes**. So at 30 packets per second, that is 480 bytes per second.
- Button Byte (1 byte)
    - Bit 7: *reserved*
    - Bit 6: **problem encountered**. 0 = all good, 1 = problem!
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

## New "Event Based" Protocol
- For button presses
    - Data byte (1 byte)
        - Bit 7: `0` (problem flag)
        - Bit 6: `0` (message type flag)
        - Bit 5: `0` = button now depressed (not pressed), `1` = button now pressed
        - Bit 4: *reserved*
        - Bit 3: **numeric with bit 3-0** (indicates what button was pressed)
        - Bit 2: **numeric with bit 3-0** (indicates what button was pressed)
        - Bit 1: **numeric with bit 3-0** (indicates what button was pressed)
        - Bit 0: **numeric with bit 3-0** (indicates what button was pressed)
    - \r\n (2 bytes)
- For variable input (i.e. joystick X/Y, triggers)
    - Header byte (1 byte)
        - Bit 7: `0` (problem flag)
        - Bit 6: `1` (message type flag)
        - Bit 5: *reserved*
        - Bit 4: *reserved*
        - Bit 3: *reserved*
        - Bit 2: **numeric with bit 2-0** (indicates what button was pressed)
        - Bit 1: **numeric with bit 2-0** (indicates what button was pressed)
        - Bit 0: **numeric with bit 2-0** (indicates what button was pressed)
    - Data Byte 1 (1 byte)
    - Data Byte 2 (1 byte)
    - \r\n (2 bytes)
- For a problem
    - Header byte (1 byte)
        - Bit 7: `1` (problem flag)
        - Bit 6: *reserved*
        - Bit 5: *reserved*
        - Bit 4: *reserved*
        - Bit 3: *reserved*
        - Bit 2: *reserved*
        - Bit 1: *reserved*
        - Bit 0: *reserved*
    - \r\n (2 bytes)
- Just to say "Hi, I'm online!", it can transmit "HELLO\n\" (72,69,76,76,79,13,10)

### Button to Corresponding ID
|Number|Binary(8-bit)|Controller Button|
|-|-|-|
|0|0b00000000|A|
|1|0b00000001|B|
|2|0b00000010|X|
|3|0b00000011|Y|
|4|0b00000100|Up|
|5|0b00000101|Right|
|6|0b00000110|Down|
|7|0b00000111|Left|
|8|0b00001000|Left Bumper|
|9|0b00001001|Right Bumper|
|10|0b00001010|Left Stick Click|
|11|0b00001011|Right Stick Click|
|12|0b00001100|Back|
|13|0b00001101|Start|

### Joystick to Corresponding ID
|Number|Binary(8-bit)|Input|
|-|-|-|
|0|0b00000000|Left Stick X|
|1|0b00000001|Left Stick Y|
|2|0b00000010|Right Stick X|
|3|0b00000011|Right Stick Y|
|4|0b00000100|Left Trigger|
|5|0b00000101|Right Trigger|