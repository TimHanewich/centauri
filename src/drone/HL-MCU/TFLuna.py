"""
TFLuna.py
MicroPython driver for the TF-Luna LiDAR range sensor by Benewake - https://en.benewake.com/TFLuna/index.html
Author Tim Hanewich, github.com/TimHanewich
Find updates to this code: https://github.com/TimHanewich/MicroPython-Collection/blob/master/TF-Luna/

MIT License
Copyright 2025 Tim Hanewich
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import machine

class TFLuna:
    """Lightweight class for interfacing with the TF-Luna LiDAR range sensor."""

    def __init__(self, i2c:machine.I2C, address:int = 0x10):
        self._i2c = i2c
        self._addr = address

    @property
    def distance(self) -> int:
        """Returns the distance in cm."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x00, 2) # read 2 bytes, 0x00 and 0x01
        distance:int = data[1] << 8 | data[0] # shift high byte 8 over, then splice low byte into it with OR operation
        return distance
    
    @property
    def strength(self) -> int:
        """Returns the strength, or amplitude, of the current distance reading. Higher values indicate stronger signal while low indicates a low-confidence reading."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x02, 2) # read 2 bytes, 0x02 and 0x03
        strength:int = data[1] << 8 | data[0] # shift high byte 8 over, then splice low byte into it with OR operation
        return strength
    
    @property
    def temperature(self) -> float:
        """Returns the temperature, in Celsius, from the onboard temperature sensor."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x04, 2) # read 2 bytes, 0x04 and 0x05
        raw:int = data[1] << 8 | data[0]
        temperatureC:float = (raw / 8) - 256 # formula provided in datasheet.
        return temperatureC / 10 # official guide says it is in 0.01 C units. I don't think that is the case, I think it meant to say 0.1 c and it was a typo. So dividing by 10 here, not 100.

    @property
    def status(self) -> dict:
        """Reads all sensor values from the TF Luna: distance, strength, and temperature."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x00, 6) # read 6 bytes, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05.
        distance:int = data[1] << 8 | data[0]
        strength:int = data[3] << 8 | data[2]
        temperature:float = (((data[5] << 8 | data[4]) / 8) - 256) / 10
        return {"distance": distance, "strength": strength, "temperature": temperature}

    @property
    def rate(self) -> int:
        """Returns the refresh rate, also known as the framerate, which is how many times per second the TF Luna will read and update its registers. Default is 100 Hz."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x26, 2) # read 2 bytes, 0x26 and 0x27
        rate:int = data[1] << 8 | data[0]
        return rate
    
    @rate.setter
    def rate(self, value:int) -> None:
        """Sets the refresh rate to any value between 1 and 250 Hz."""
        if value < 1 or value > 250:
            raise Exception("Unable to set framerate (refresh rate) to " + str(int(value)) + ". The TF Luna supports 1-250 Hz.")
        data:bytes = value.to_bytes(2, "little") # convert to 2 bytes, so the low byte comes before the high byte, which is what the TF luna uses
        self._i2c.writeto_mem(self._addr, 0x26, data) # write the two bytes to register 0x26 and 0x27

    @property
    def signature(self) -> bool:
        """Confirms if the TF Luna is connected via I2C by checking its 'signature' registers."""
        data:bytes = self._i2c.readfrom_mem(self._addr, 0x3C, 4) # read 4 bytes, 0x3C, 0x3D, 0x3E, 0x3F
        return data == "LUNA".encode() # the expected result is "LUNA" encoded as bytes
    
    def reboot(self) -> None:
        """Reboot the TF-Luna."""
        self._i2c.writeto_mem(self._addr, 0x21, bytes([0x02])) # reboot command

    def reset(self) -> None:
        """Restore TF-Luna to factory defaults."""
        self._i2c.writeto_mem(self._addr, 0x29, bytes([0x01]))