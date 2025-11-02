# Centauri: Custom Quadcopter Fight Controller
*Centauri* is a custom, MicroPython-based, quadcopter flight controller that is capable of efficiently running on a low-power microcontroller like the Raspberry Pi Pico.

Centauri is the successor to my [Scout flight controller](https://github.com/TimHanewich/scout) and is a very big upgrade.

## Design
Every aspect of Centauri - from hardware to software - was designed and developed from scratch. This repository provides everything you need to duplicate Centauri, including:
- **The Centauri quadcopter design** - 3D design files for Centauri's body.
- **The Centauri fight controller** - an efficient fight controller that runs onboard a quadcopter and maintains safe and level flight.
- **The Centauri controller** - a PC-based program that reads input data from a wired Xbox controller and transmits control input back to the quadcopter.
- **Bi-directional transceiver** - a simple platform used by the Centauri controller for facilitating bidirectional radio communications with the drone.

## Demonstration Videos
- [October 26, 2025: First Test Flight](https://x.com/TimHanewich/status/1982566777273163850) - commit `fffb3ff3d44cfcaa7561e7b6fd52661ec379cb79`
- [November 2, 2025: First Outside Test Flight](https://youtu.be/w3_uWFIpgT4) - commit `f71a90ca79df5736b8931f8cb0a1148ade9bbafd`