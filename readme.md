# Centauri: Multi-MCU Quadcopter Flight Controller
The successor to my [Scout flight controller](https://github.com/TimHanewich/scout).

## To Do:
- Code:
    - LL-MCU: if a massive, breaking error happens, continuously send that error over UART to the HL-MCU in the error pattern
    - LL-MCU: Failsafe to 0% throttle if no desired rate data for X seconds
    - LL-MCU: motors should always be at 0% if throttle is at 0% (PIDs can throw it over)

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)