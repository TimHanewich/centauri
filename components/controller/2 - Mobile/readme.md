# Mobile System
The mobile system has two source code repos:
1. A lightweight script that runs on a Raspberry Pi w/ a full OS installed (i.e. RPi 3B or RPi Zero) that is *solely* intended for reading game controller inputs and providing those to a Pico microcontroller.
2. Microcontroller code that runs on a Raspberry Pi Pico, accepts the controller input from the RPi, displays data on a SSD1306, and handles communication with the drone.