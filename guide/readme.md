# Building Centauri: Custom Python-based Quadcopter Flight Controller
- **Chapter 1**: Getting Started 
    - What is Centauri
    - Components needed
    - Cost estimate
    - go read about quadcopter flight dyamics
- **Chapter 2**: Print and Assemble the Drone
- **Chapter 3**: Flash the Code to the Drone's MCU
- **Chapter 4**: Transceiver Assembly
- **Chapter 5**: First boot: establish communications, spin the props!
- **Chapter 6**: PID Tuning and Tethered Testing
- **Chapter 7**: Take Flight!


## Running on PC
You can run [main.py](./src/controller/PC/main.py) on your PC after connecting 1) an Xbox controller and 2) a transceiver.

The required Python packages are:
1. pygame
2. pyserial
3. rich
4. keyboard

But you can run `pip install -r requirements.txt` as well to automatically download all documented dependencies from [requirements.txt](./src/controller/PC/requirements.txt).

Make sure to document:
- Design decisions
    - MPU-6050 is right in the middle
    - Every motor equidistant
    - Middle level for hardware
    - M3 holes for using as leg pegs
    - Mounting points for Lidar sensor on belly
    - Straps on top for battery
    - Gopro mount for mounting camera
    - Raspbery pi pico on edge so can be flashed
    - Room for a second pi for multi-MCU architectures (Centauri originally was multi MCU)
- Communication protocol
    - HC-12 is half duplex. Challenges.
    - Each packet
- Drone code
    - 