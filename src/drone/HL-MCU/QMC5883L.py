"""
QMC5883L.py - lightweight MicroPython driver for interfacing with the QMC5883L magnetometer (compass).
For any updates and instructions on how to use this, visit: https://github.com/TimHanewich/MicroPython-Collection/tree/master/QMC5883L
Author Tim Hanewich, github.com/TimHanewich

MIT License
Copyright 2025 Tim Hanewich
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import machine
import math

class QMC5883L:

    def __init__(self, i2c:machine.I2C):
        self._i2c = i2c
        self._address = 0x0D
        self.initialize()

    def initialize(self, mode:int = 1, rate:int = 10, range:int = 2, oversampling:int = 512) -> None:
        """
        Initializes the QMC5883L.
        
        Args:
            mode (int): 0 = standby, not reading. 1 = continuous reading and updating of data registers.
            rate (int): Determines how frequently the sensor performs a measurement, in Hz. Can be 10, 50, 100, or 200.
            range (int): defines max magnetic field strength the sensor can measure. 8 = 8-Gauss, full range, low sensitivity. 2 = 2-Gauss, high sensitivity, high resolution but can overflow.
            oversampling (int): defines how many internal measurements are taken and averaged before returning. Can be 64, 128, 256, or 512.
        
        Returns:
            None
        """

        # Options for Measurement mode
        # 0 = standby, sensor is idle and not actively measuring
        # 1 = continuous, sensor is constantly measuring and updating its data registers

        # Options for Rate
        # Determines how frequently the sensor performs a measurement
        # 10 = 10 times per second, low update rate, low power (00 as bits)
        # 50 = 50 times per second, moderate rate, good for general use (01 as bits)
        # 100 = 100 times per second, faster updates, better for motion tracking (10 as bits)
        # 200 = 200 times per second, highest rate, ideal for fast-moving platforms like drones (11 as bits)

        # Options for Range
        # defines the maxiumum magnetic field strength the sensor can measure.
        # 2 = +- 2 Gauss, high sensitivty and better resolution for weak magnetic fields (00 as bits)
        # 8 = +- 8 Gauss, lower sensitivity, but can handle strong magnetic fields without overflow (01 as bits)
        
        # Options for Oversampling
        # refers to how many internal measurements it takes and averages before returning
        # 64 = 64x, fastest, lowest precision (00 as bits)
        # 128 = 128x, balanced speed and accuracy (01 as bits)
        # 256 = 256x, good noise reduction (10 as bits)
        # 512 = 512x, Best precision, slowest rate (11 as bits)

        # construct what we will send to register 0x09 on the QMC5883L

        # construct oversampling ratio
        bits_oversampling:str = ""
        if oversampling == 64:
            bits_oversampling = "00"
        elif oversampling == 128:
            bits_oversampling = "01"
        elif oversampling == 256:
            bits_oversampling = "10"
        elif oversampling == 512:
            bits_oversampling = "11"
        else:
            raise Exception("Oversampling value of '" + str(oversampling) + "' invalid. Must be 64, 128, 256, or 512.")
        
        # construct range bits
        bits_range:str = ""
        if range == 2: # 2 Gauss
            bits_range = "00"
        elif range == 8: # 8 Gauss
            bits_range = "01"
        else:
            raise Exception("Value '" + str(range) + "' invalid for range. Must be 2 or 8.")
    
        # construct output data rate bits
        bits_rate:str = ""
        if rate == 10:
            bits_rate = "00"
        elif rate == 50:
            bits_rate = "01"
        elif rate == 100:
            bits_rate = "10"
        elif rate == 200:
            bits_rate = "11"
        else:
            raise Exception("Output data rate of '" + str(rate) + "' invalid. Must be 10, 50, 100, or 200.")
        
        # construct mode bits
        bits_mode: str = ""
        if mode == 0: # standby
            bits_mode = "00"
        elif mode == 1:
            bits_mode = "01"
        else:
            raise Exception("Value '" + str(mode) + "' invalid for mode. Must be 0 or 1.")
        
        # construct and send the bit-masked byte we will send with all of those
        ControlByteStr:str = bits_oversampling + bits_range + bits_rate + bits_mode # i.e. "00010001"
        ControlByte:int = int(ControlByteStr, 2) # convert "00010001" or whatever it is to a byte (int)
        self._i2c.writeto_mem(self._address, 0x09, bytes([ControlByte]))
        
        # put control register 2 in default state
        self._i2c.writeto_mem(self._address, 0x0A, bytes([0x00])) # no interrupts, no resets.

    def read(self) -> tuple[int, int, int]:
        """Read the magnetometer values in X,Y,Z format."""
        raw_data:bytes = self._i2c.readfrom_mem(self._address, 0x00, 6) # read 6 bytes
        x:int = int.from_bytes(raw_data[0:2], "little")
        y:int = int.from_bytes(raw_data[2:4], "little")
        z:int = int.from_bytes(raw_data[4:6], "little")
        return (x, y, z)
    
    def calibrate(self, x_min:int, x_max:int, y_min:int, y_max:int, z_min:int, z_max:int) -> None:
        """Stores the extrema of the observed raw XYZ readings, which will later be used in determining compass heading."""
        self._x_min:int = x_min
        self._x_max:int = x_max
        self._y_min:int = y_min
        self._y_max:int = y_max
        self._z_min:int = z_min
        self._z_max:int = z_max

    @property
    def heading(self) -> float:
        """Determines the magnetometer's current heading using the X and Y values (assuming it is laying flat)."""
        x,y,z = self.read()
        x_cal:float = x - (self._x_min + self._x_max) / 2 # subtract the average (midpoint) X value out, so the reading is "centered" at 0
        y_cal:float = y - (self._y_min + self._y_max) / 2 # subtract the average (midpoint) Y value out, so the reading is "centered" at 0
        heading_rad = math.atan2(y_cal, x_cal) # heading, in radians
        heading_deg = math.degrees(heading_rad) # heading, in degrees
        if heading_deg < 0:
            heading_deg += 360
        return heading_deg