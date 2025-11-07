![banner](https://i.imgur.com/oSwhZjR.png)

# Centauri: Custom Quadcopter Fight Controller
*Centauri* is a custom, MicroPython-based, quadcopter flight controller that is capable of efficiently running on a low-power microcontroller like the Raspberry Pi Pico.

Centauri is the successor to my [Scout flight controller](https://github.com/TimHanewich/scout) and represents a major leap forward in capability and performance.

To watch *Centauri* in action, click below!
[![demo video](https://i.imgur.com/zbcKlFx.png)](https://www.youtube.com/watch?v=-Kj5vSNrLSk)

## What this Project Contains
![anatomy](https://i.imgur.com/6TYY0Nv.png)
Every aspect of Centauri - from hardware to software - was designed and developed from scratch. This repository provides *everything* you need to build your own Centauri quadcopter and get off the ground, including:
- **The Centauri Quadcopter** - 3D-printable design files, flight controller software, electric wiring diagrams
- **Pilot Controller** - a PC-based program that reads input data from a wired Xbox controller and transmits control input back to the quadcopter.
    - **Bi-directional transceiver** - a simple platform used by the Centauri controller (USB-connected) with a radio transceiver for facilitating bidirectional communication with the drone.
- **Analysis script** - lightweight Python script for unpacking encoded telemetry data (Centauri stores on the MCU's flash storage) into a CSV file.