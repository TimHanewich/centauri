# Centauri Design
- Radio Controller:
    - PC (windows/linux)
    - Xbox controller plugged in via USB
    - Transceiver plugged in via USB
        - Raspberry Pi Pico
        - HC-12
- Quadcopter
    - 3D printed body
        - Diagonal Propeller Distance: 225mm
    - 4 motors
        - [Readytosky 2300KV brushless motors](https://a.co/d/6Pua6ZV)
        - 5mm center
        - 19x16mm mounting holes on bottom
    - Propellers: [5-inch, 3-blade, 4-inch pitch propellers](https://a.co/d/6pNksCt)
    - 4 ESCs: [20A 2-4S BLHeli ESCs](https://a.co/d/6Rvq71s)
    - HC-12 radio communication module, **5v**
    - MPU-6050 IMU *(connected to LL MCU)*, **3.3v**
    - TF-Luna lidar *(connected to HL MCU)*, **5v**
    - BMP180 pressure sensor *(connected to HL MCU)* **3.3v**
    - QMC5883l magnetometer *(connected to HL MCU)*, **3.3v**
    - [4S LiPo battery](https://a.co/d/5QyLvZG)
        - 135mm x 42mm x 30mm
    - Voltage divider for battery
    - LM2596 buck converter set to +5V
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

## Body Design Inspiration
![exaple](https://3dprinting.com/wp-content/uploads/2015/05/hframe-3d-printed-quadcopter.jpg)

![example](https://axelsdiy.brinkeby.se/wp-content/uploads/2017/07/1200_DSC_6927.jpg)

![example](https://kingroon.com/cdn/shop/articles/3D_Printed_Drone.jpg?v=1725266590)

![example](https://www.robots.co.uk/wp-content/uploads/2015/10/drone5.png)

![example](https://fbi.cults3d.com/uploaders/25297494/illustration-file/e9fb86ac-7ee3-4442-9882-9c307f14eb75/Testing.jpg)

![example](https://blog.quadmeup.com/assets/2017/12/3d-printed-racing-drone--1024x590.jpg)

## Quadcopter Frame: Blender Design Dumps
- [August 10, 2025 - complete design](https://github.com/TimHanewich/centauri/releases/download/1/design.zip)

## Transceiver Platform
I designed and 3D-printed a small platform a Raspberry Pi Pico and HC-12 can be mounted to in one platform, used for the transceiver. Download it [here](https://github.com/TimHanewich/centauri/releases/download/2/transceiver_platform.stl).

![transceiver platform](https://i.imgur.com/zod1oGl.png)

## Misc Notes
- If a UART multiplexer is needed, the CD4053 may be a good option. Check out a video on it [here](https://youtu.be/Up68IgKUZy4?si=PsPbn5xtIKbIRIJK).

## Credit to Designs Used
- I slightly modified (see my version [here](https://www.thingiverse.com/thing:7112439)) an [MPU-6050 basic case by MaximvonAZ](https://www.thingiverse.com/thing:2800169)
- TF Luna Dummy: https://www.thingiverse.com/thing:4356740