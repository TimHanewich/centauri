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

## Speed Auditing on August 14, 2025
Something is causing the LL-MCU synchronous loop to occasionally dip in speed. it goes from having ~2,300 us (2.3 ms) in excess capacity every cycle to having -5,000 us free. And this is in tests WITHOUT processing any incoming control data from the HL-MCU!

So I am auditing the speed of each main operation to see what it could be:
- `gyro_data:bytes = i2c.readfrom_mem(0x68, 0x43, 6)` = ~450 us stable
- Converting the gyro raw data into floats just after I2C read = ~280 us stable
- Calculating all 3 axis PID values = usually ~750 us, but seeing spike to **8,827 occasionally**!
    - Does this mean this code is bad? Nope... it actually confirms the issue is garbage collection.
    - GC being the issue is pointed out by GPT-4.1: https://i.imgur.com/dVjSH3j.png
    - I confirmed this is in a test. When garbage collecting at the start of every loop (super slow, but for test), it never spiked!

I also learned that floating point math also has a memory leak. Every time a floating point math is done, a new float is made. 

For example:
```
pitch_rate = gyro_x / 131 
```

Can be expressed as:
```
pitch_rate = gyro_x * 1000 // 131 
```