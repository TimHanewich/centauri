# Building Centauri: Custom Python-based Quadcopter Flight Controller
- Getting Started 
    - What is Centauri
    - Components needed
    - Cost estimate
    - go read about quadcopter flight dyamics
- Print and Assemble the Drone
- Flash the Code to the Drone's MCU
- Transceiver Assembly
- First boot: establish communications, spin the props!
- PID Tuning and Tethered Testing
- Take Flight!


## Running on PC
You can run [main.py](./src/controller/PC/main.py) on your PC after connecting 1) an Xbox controller and 2) a transceiver.

The required Python packages are:
1. pygame
2. pyserial
3. rich
4. keyboard

But you can run `pip install -r requirements.txt` as well to automatically download all documented dependencies from [requirements.txt](./src/controller/PC/requirements.txt).