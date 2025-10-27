# Getting Started with Centauri
- Getting Started (components needed, go read about quadcopter flight dyamics)
- Drone Build: Print and Assemble
- Drone Build: Flash the Code
- Controller Build: Transceiver Assembly
- Controller Build: Setup and Run
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