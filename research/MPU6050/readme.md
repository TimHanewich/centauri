[MPU-6050 register map](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf)

## Initialization Steps
1. Wake up the MPU-6050: Write a byte of `0` to register `0x6B`.
2. Then set the digital low pass filter to 10 Hz by writing a byte of `0x05` to register `0x1A`. This will filter out noise significanty for both the gyro and accelerometer.
3. Then set the full scale range of the gyroscope to 250 degrees per second writing a byte of `0x00` to register `0x1B` This is the most sensitive gyro setting and will be very accurate but cut off at 250 degrees per second (which Centauri will never exceed as a slow-moving platform). **IMPORTANT NOTE: if you plan for the drone to be high performing, will need to bump up this value so it doesn't clip.**
4. Set the full scale range of the accelerometer to 2g by writing a byte of `0x00` to register `0x1C`. This is the lowest range, so provides a lot of accuracy at that level. **IMPORTANT NOTE: if you plan for the drone to be high performing, will need to bump up this value so it doesn't clip.**

## Sample Code
See [example.py](./example.py) for a complete end-to-end example that shows:
1. MPU-6050 initialization
2. Reading of Gyro Data
3. Reading of Accel Data
4. Sensor Fusion via Complementary Filter

