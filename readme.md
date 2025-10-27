# Centauri: Custom Quadcopter Fight Controller
*Centauri* is a custom, MicroPython-based, quadcopter flight controller that is capable of efficiently running on a low-power microcontroller like the Raspberry Pi Pico.

Centauri is the successor to my [Scout flight controller](https://github.com/TimHanewich/scout) and is a very big upgrade.

## Design
Every aspect of Centauri - from hardware to software - was designed and developed from scratch. This repository provides everything you need to duplicate Centauri, including:
- **The Centauri quadcopter design** - 3D design files for Centauri's body.
- **The Centauri fight controller** - an efficient fight controller that runs onboard a quadcopter and maintains safe and level flight.
- **The Centauri controller** - a PC-based program that reads input data from a wired Xbox controller and transmits control input back to the quadcopter.
- **Bi-directional transceiver** - a simple platform used by the Centauri controller for facilitating bidirectional radio communications with the drone.

## Running on PC
You can run [main.py](./src/controller/PC/main.py) on your PC after connecting 1) an Xbox controller and 2) a transceiver.

The required Python packages are:
1. pygame
2. pyserial
3. rich
4. keyboard

But you can run `pip install -r requirements.txt` as well to automatically download all documented dependencies from [requirements.txt](./src/controller/PC/requirements.txt).