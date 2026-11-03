# Components
Centauri is more than a quadcopter: it's a custom-built ecosystem for sending pilot commands, controlling flight, observing radio communications, and understanding what happened after landing. Explore each component below for hardware, software, and build documentation.

## [Transmitter](./transmitter/)
The pilot's connection to the aircraft. A USB-connected Xbox controller supplies the inputs, a Python program on the computer turns them into control packets, and a Pico-powered HC-12 transceiver platform exchanges data with the quadcopter over radio. Explore the hardware and software that bring this custom control interface together.

## [Quadcopter](./quadcopter/)
The aircraft itself, designed from the ground up with a 3D-printed airframe, purpose-built electronics layout, and MicroPython flight controller running on a Raspberry Pi Pico. Find the parts list, printable frame designs, flight controller source, ESC calibration script, and optional FPV setup to build and understand your own Centauri.

## [Link](./link/)
A handheld window into Centauri's radio communications. Link listens for radio traffic to help troubleshoot reception and check approximate range on foot before risking the aircraft in flight. Explore the carrier board, electronic components, 3D-printed enclosure, and wiring needed to assemble your own monitor.

The Link Carrier Board is the foundation of the build, not a complete device; components sold separately, soldering and assembly required. A ground reception check is a useful diagnostic, not a guarantee of reliable communication in flight. Leave a conservative range margin and account for changing conditions.

## [Telemetry Extraction & Analysis](./analysis/)
Turn the quadcopter's compact binary flight logs into data you can actually inspect. The Python analysis script decodes telemetry into CSV, identifies individual flights, and summarizes duration, battery voltage, G-force, throttle, and command receipt latency. Use the results to troubleshoot flights, plot sensor readings and motor outputs, or overlay telemetry on flight video with the [Centauri DashWare assets](../dashware/).

Sample flight logs are available through the analysis documentation, so you can explore the data with just a computer and Python - no aircraft required.