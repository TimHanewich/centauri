# Centauri: Custom Quadcopter Fight Controller
*Centauri* is a custom, MicroPython-based, quadcopter flight controller that is capable of efficiently running on a low-power microcontroller like the Raspberry Pi Pico.

Centauri is the successor to my [Scout flight controller](https://github.com/TimHanewich/scout) and is a very big upgrade.

To watch *Centauri* in action, click below!
[![demo video](https://i.imgur.com/zbcKlFx.png)](https://www.youtube.com/watch?v=-Kj5vSNrLSk)

## Design
Every aspect of Centauri - from hardware to software - was designed and developed from scratch. This repository provides everything you need to duplicate Centauri, including:
- **The Centauri quadcopter design** - 3D design files for Centauri's body.
- **The Centauri fight controller** - an efficient fight controller that runs onboard a quadcopter and maintains safe and level flight.
- **The Centauri controller** - a PC-based program that reads input data from a wired Xbox controller and transmits control input back to the quadcopter.
- **Bi-directional transceiver** - a simple platform used by the Centauri controller for facilitating bidirectional radio communications with the drone.