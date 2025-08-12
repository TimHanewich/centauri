## Low-Level MCU Design
The low-level MCU will be primarily responsible for the main flight control PID loops, specifically in **rate mode** (angle mode will be built as *another* PID loop within the HL MCU that is run there). To the LL MCU, there is no angle mode, it is just rate mode.

## Operation, from boot
- Ping a single "I'm alive, booting now" message to the HL MCU via UART (not a PING/PONG response)
- Set up MPU-6050
    - Set up I2C
    - Wake it up
    - Set low pass filter
    - Set gyro scale
    - Confirm all of those settings
- Calibrate gyro (observe and record bias)
- Set up motor PWMs
- Set up setting variables (*only settings used by LL MCU*)
    - PID Pitch P
    - PID Pitch I
    - PID Pitch D
    - PID Roll P
    - PID Roll I
    - PID Roll D
    - PID Yaw P
    - PID Yaw I
    - PID Yaw D
    - PID I Limit
- Calculate constants
    - Cycle time, in microseconds

- Overclock

The LL MCU will then run the following async coroutines in parralel:
- Flight Control Loop:
    - 