[MPU-6050 register map](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf)

Take the gyro registers for example:
![https://i.imgur.com/cHQCzo9.png]

Doing the following will allow you to stitch together the first byte and the second byte as one single, 16-bit value:

```
(high << 8) | low
```

The above shifts high out 8 bits (so the lowest 8 bits are now unoccupied), then "adds in" the low bit into the lowest 8 bits via the bitwise OR operator.


## Some Code, from Copilot, Showing how to Read
```
from machine import Pin, I2C
import time

# Initialize I2C on GP0 (SDA) and GP1 (SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
MPU6050_ADDR = 0x68

# Wake up MPU-6050 (exit sleep mode)
i2c.writeto_mem(MPU6050_ADDR, 0x6B, b'\x00')  # PWR_MGMT_1 register

def read_word(high_reg, low_reg):
    high = i2c.readfrom_mem(MPU6050_ADDR, high_reg, 1)[0]
    low = i2c.readfrom_mem(MPU6050_ADDR, low_reg, 1)[0]
    value = (high << 8) | low
    # Convert to signed 16-bit
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

while True:
    gyro_x = read_word(0x43, 0x44)
    gyro_y = read_word(0x45, 0x46)
    gyro_z = read_word(0x47, 0x48)

    # Scale factor for ±250°/s range
    scale = 131.0
    print("Gyro (°/s): X={:.2f}, Y={:.2f}, Z={:.2f}".format(
        gyro_x / scale, gyro_y / scale, gyro_z / scale
    ))

    time.sleep(0.5)

```

## Steps
Wake up the MPU-6050: Write a byte of `0` to register `0x6B`.

Then set the digital low pass filter to 10 Hz by writing a byte of `0x05` to register `0x1A`. This will filter out noise significanty for both the gyro and accelerometer.

Then set the full scale range of the gyroscope to 250 degrees per second writing a byte of `0x00` to register `0x1B` This is the most sensitive gyro setting and will be very accurate but cut off at 250 degrees per second (which Centauri will never exceed as a slow-moving platform). **IMPORTANT NOTE: if you plan for the drone to be high performing, will need to bump up this value so it doesn't clip.**

Set the full scale range of the accelerometer to 2g by writing a byte of `0x00` to register `0x1C`. This is the lowest range, so provides a lot of accuracy at that level. **IMPORTANT NOTE: if you plan for the drone to be high performing, will need to bump up this value so it doesn't clip.**