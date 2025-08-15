# Centauri: Multi-MCU Quadcopter Flight Controller
The successor to my [Scout flight controller](https://github.com/TimHanewich/scout).

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)