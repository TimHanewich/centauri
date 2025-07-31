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
    - Battery level as % (1 byte)
    - TF Luna reading (? bytes)
    - BMP180 reading (? bytes)
    - QMC5883L reading (? bytes)
- "\r\n" end line (2 bytes)

## Some Coding Tips
In Python, we can use `<<` to perform a bitwise left shift. For example `1` is `00000001`. If we shift it to the left one time, it would be `00000010`.

|Notation|Value|
|-|-|
|`1 << 0`|`0b00000001`|
|`1 << 1`|`0b00000010`|
|`1 << 2`|`0b00000101`|
|`1 << 3`|`0b00001000`|
|`1 << 4`|`0b00010000`|
|`1 << 5`|`0b00100000`|
|`1 << 6`|`0b01000000`|
|`1 << 7`|`0b10000000`|

### OR Operator
A `OR` operation compares each bit between two bytes you give it (compares bits of the same position). Between the two bits being compared, if **at least one** of the bits are `1`, the resulting bit vaue of that position will be `1`. But if both are `0`, the resulting bit of that position will be `0`.

For example:
```
val = 1 << 0 | 1 << 1
bin(val) # 0b00000011
```

As seen above, `0b00000001` and `0b00000010` became `0b00000011` with the OR operator (`|`).

So, we can use the OR operator to set certain bit values. 

For example, if we can to construct a single byte and set the 7th, 2nd, and 1st bit value to 1:
```
val = 0b00000000 # start with 0, a blank slate (can just do val=0 too)
val = val | 0b10000000 # set the 7th bit to 1
val = val | 0b00000010 # set the 2nd bit to 1
val = val | 0b00000001 # set the 1st it to 1
bin(val) # 0b10000011
```

The example above sets each bit one-by-one. We can also set them all at once, for example:
```
val = 0b00000000 # start with 0, a blank slate
val = val | 0b10000011
bin(val) # 0b10000011
```

### AND Operator
The AND operator is important as it gives us the ability to check if a certain bit of a byte is occupied or not. By doing an AND operation between a byte value and a byte value with the bit we are testing occupied as 1 (and all other bits set to 0), if the resulting value has at least that one bit occupied, that means that bit indeed was occupied by 1. If it comes back as 0, that bit was not occupied.

For example:
```
val = 0b11010010
tester = 0b10000000 
result = val & tester # bitwise AND operator
print(result) # 128
```

In the example above, since the result was not 0, we can indeed confirm the 7th bit was occupied. 

If we try that with a bit that is NOT occupied, `result` will be 0:
```
val = 0b11010010
tester = 0b00100000 
result = val & tester # bitwise AND operator
print(result) # 0
```

So, putting that all together, a quick way to test if a bit is occupied is this for example:
```
val = 0b11010010
if val & 0b10000000 > 0:
    print("7th bit is occupied!")
else:
    print("7th bit is not occupied.")
```