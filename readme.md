# Centauri: Multi-MCU Quadcopter Flight Controller
The successor to my [Scout flight controller](https://github.com/TimHanewich/scout).

## High-Level System Design
- Radio Controller (single MCU)
    - Rasberry Pi Pico
    - 16x2 LCD
    - SD-1306 OLED
    - HC-12
    - Throttle potentiometer
    - Trigger- potentiometer (for yaw)
    - Trigger+ potentiometer (for yaw)
    - Joystick for pitch + roll
    - LiPo battery
- Quadcopter
    - HC-12 radio communication module
    - MPU-6050 IMU *(connected to LL MCU)*
    - TF-Luna lidar *(connected to HL MCU)*
    - BMP180 pressure sensor *(connected to HL MCU)*
    - QMC5883l magnetometer *(connected to HL MCU)*
    - 4 motors w/ propellers
    - 4 speed controllers (1 per motor)
    - 2-4S LiPo battery
    - Voltage divider for battery
    - 5v buck converter (if speed controllers do not have BEC)
    - "High Level" MCU: Rasperry Pi Pico
        - Read input from HC-12 (control commands from remote control)
        - Pass fight control inputs on to LL MCU via UART
        - Read incoming status packet from LL MCU
        - Read from TF-Luna and append to status packet
        - Read from BMP180 pressure sensor and append to status packet
        - Read from QMC5883L magnetometer and append to status packet
        - Read battery level (voltage divider) and append to status packet
        - Send status packet back to remote controller via HC-12
    - "Low Level" MCU: Rasperry Pi Pico
        - Read input from HL MCU via UART
        - Read gyro + accel from IMU
        - Pass through PID loop to determine M1-4 throttles
        - Use complementary fiter to estimate roll & pitch angles
        - Set M1-4 throttles

## Communication Protocol
Two HC-12 radio transceiver modules will be used to facilitate bidirectional remote communications between the remote controller and the drone. Serial UART will be used to facillitate bidirectional communication between the HL MCU and LL MCU.

Communication Timing:
- Remote controller sends control packets at 50 Hz
- HL MCU receives control packets at 50 Hz
- HL MCU provides control packets to LL MCU at 50 Hz
- LL MCU provides status updates to HL MCU at 10 Hz
- HL MCU provides sends status updates to remote controller at 10 Hz

The communication packet structures are described below:

###  PID Value Config Packet
Remote controller --> HL MCU via HC-12, HL MCU --> LL MCU via UART.

Used to update the PID gains used by the LL MCU on the go without having to manually re-flash code.

- Metadata byte (1 byte)
    - `00` as Pack identifier (2 bits)
    - *Reserved: 6 bits*
- Roll_P (4 bytes): roll P value
- Roll_I (4 bytes): roll I value
- Roll_D (4 bytes): roll D value
- Pitch_P (4 bytes): pitch P value
- Pitch_I (4 bytes): pitch I value
- Pitch_D (4 bytes): pitch D value
- Yaw_P (4 bytes): yaw P value
- Yaw_I (4 bytes): yaw I value
- Yaw_D (4 bytes): yaw D value        

###  The Standard Packet
Remote controller --> HL MCU via HC-12, HL MCU --> LL MCU via UART.

This data packet contains all necessary data for controlling normal flight characteristics of the drone.

- Metadata byte (1 byte)
    - `01` as Pack identifier (2 bits)
    - Flying (1 bit): controls whether props can spin at all or not
    - Control mode (1 bit): basic rate matching control or advanced attitude control
    - *Reserved: 4 bits*
- Throttle (2 bytes)
- Roll input (2 bytes): roll stick input, can be used to calculate desired roll rate or angle
- Pitch input (2 bytes): pitch stick input, can be used to calculate desired pitch rate or angle
- Yaw input (2 bytes): yaw input, can be used to calculate desired yaw rate
- "\r\n" end line (2 bytes)

###  Status Packet
LL MCU --> HL MCU via UART, HL MCU --> Remote Controller via HC-12.

- M1 throttle (2 bytes)
- M2 throttle (2 bytes)
- M3 throttle (2 bytes)
- M4 throttle (2 bytes)
- Actual Roll Rate (2 bytes)
- Actual Pitch Rate (2 bytes)
- Actual Yaw Rate (2 bytes)
- Roll Angle Estimate (2 bytes): from complementary filter performed on LL MCU
- Pitch Angle Estimate (2 bytes): from complementary filter performed on LL MCU
- *HL MCU will append...*
    - Battery level as voltage (2 bytes)
    - TF Luna reading (? bytes)
    - BMP180 reading (? bytes)
    - QMC5883L reading (? bytes)
- "\r\n" end line (2 bytes)