## Low-Level MCU Design
The low-level MCU will be primarily responsible for the main flight control PID loops, specifically in **rate mode** (angle mode will be built as *another* PID loop within the HL MCU that is run there). To the LL MCU, there is no angle mode, it is just rate mode.

## Operation, from boot
First, set up:
- Ping a single "I'm alive, booting now" message to the HL MCU via UART
- Set up MPU-6050
    - Set up I2C
    - Wake it up
    - Set low pass filter
    - Set gyro scale
    - Confirm all of those settings
- Calibrate gyro (observe and record bias)
- Set up universal variables that may need to be referenced accross all coroutines
- Overclock

The LL MCU will then run the following async coroutines in parralel:
- Flight Control Loop:
    - Set up motor PWMs
    - Infinite loop
        - Capture raw IMU data
        - Calculate errors to desired pitch rate, roll rate, yaw rate
        - Perform Pitch PID Calc
        - Perform Roll PID Calc
        - Perform Yaw PID Calc
        - Calculate M1-4 throttles using desired throttle + PID outputs
        - Set M1-4 throttles
- Rx Loop: handle incoming data from HL-MCU (via UART)
    - **Pings**: respond with "PONG"
    - Settings updates (PID gains, etc.)
    - Desired rates
- Tx Loop: routinely send data to HL-MCU (via UART)
    - Status