# Centauri: Multi-MCU Quadcopter Flight Controller
The successor to my [Scout flight controller](https://github.com/TimHanewich/scout).

## Running on PC
You can run [main.py](./src/controller/PC/main.py) on your PC after connecting 1) an Xbox controller and 2) a transceiver.

The required Python packages are:
1. pygame
2. pyserial
3. rich
4. keyboard

But you can run `pip install -r requirements.txt` as well to automatically download all documented dependencies from [requirements.txt](./src/controller/PC/requirements.txt).

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)
- `ef7a0a76ea731c0cf48fcec6653566df2ed101c4` - last commit before moving to a single MCU architecture on the quadcopter and removing many of the sensors (focusing just on rate mode moving forward, abandoning plans for angle mode for now)