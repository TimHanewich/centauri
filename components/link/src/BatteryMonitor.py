"""
Simple class for estimating a battery's state of charge as a percentage, based upon the read voltage of the battery.
Author Tim Hanewich, github.com/TimHanewich
Find updates to this code: https://github.com/TimHanewich/MicroPython-Collection/tree/master/BatteryMonitor

MIT License
Copyright 2023 Tim Hanewich
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# Discharge profile for a single-cell 18650 battery
PROFILE_18650:list[tuple[float, float]] = [
    (4.2, 1.0),
    (4.1, 0.9),
    (4.0, 0.8),
    (3.9, 0.7),
    (3.8, 0.6),
    (3.7, 0.5),
    (3.6, 0.4),
    (3.5, 0.3),
    (3.4, 0.2),
    (3.0, 0.0)
]

# Discharge profile for a lead-acid battery (i.e. car/motorcycle/vehicle battery)
PROFILE_LEAD_ACID = [
    (12.7, 1.0),  # 12.7V - 100% SOC
    (12.5, 0.9),   # 12.5V - 90% SOC
    (12.3, 0.8),   # 12.3V - 80% SOC
    (12.1, 0.7),   # 12.1V - 70% SOC
    (11.9, 0.6),   # 11.9V - 60% SOC
    (11.7, 0.5),   # 11.7V - 50% SOC
    (11.5, 0.4),   # 11.5V - 40% SOC
    (11.3, 0.3),   # 11.3V - 30% SOC
    (11.1, 0.2),   # 11.1V - 20% SOC
    (10.9, 0.1),   # 10.9V - 10% SOC
    (10.5, 0.0)    # 10.5V - 0% SOC
]

# Discharge Profile for a 1S Lithium-Polymer battery (LiPo)
PROFILE_1S_LIPO = [
    (4.2, 1.0),  # 4.2V - 100% SOC
    (4.1, 0.9),   # 4.1V - 90% SOC
    (4.0, 0.8),   # 4.0V - 80% SOC
    (3.95, 0.7),  # 3.95V - 70% SOC
    (3.9, 0.6),   # 3.9V - 60% SOC
    (3.85, 0.5),  # 3.85V - 50% SOC
    (3.8, 0.4),   # 3.8V - 40% SOC
    (3.75, 0.3),  # 3.75V - 30% SOC
    (3.7, 0.2),   # 3.7V - 20% SOC
    (3.65, 0.1),  # 3.65V - 10% SOC
    (3.6, 0.0)    # 3.6V - 0% SOC
]

class BatteryMonitor:
    
    def __init__(self, discharge_profile:list[tuple[float, float]] = PROFILE_18650):
        """Creates a new BatteryMonitor with a discharge profile that maps to a known and understood discharge curve of a particular battery."""
        self._profile = discharge_profile

    def soc(self, voltage:float) -> float:
        """Estimates a battery's state of charge, as a percentage, given the known voltage."""

        # above highest?
        highest:tuple[float, float] = self._highest()
        if voltage > highest[0]:
            return highest[1]
        
        # below lowest?
        lowest:tuple[float, float] = self._lowest()
        if voltage < lowest[0]:
            return lowest[1]
        
        # So we are not above the highest or below the highest, we are somewhere in between. find the two closest!
        closest_two:list[tuple[float, float]] = self._closest(voltage, 2)
        min_v:float = min(closest_two[0][0], closest_two[1][0])
        max_v:float = max(closest_two[0][0], closest_two[1][0])
        min_soc:float = min(closest_two[0][1], closest_two[1][1])
        max_soc:float = max(closest_two[0][1], closest_two[1][1])
        pofr:float = (voltage - min_v) / (max_v - min_v)
        voltage_estimate:float = min_soc + ((max_soc - min_soc) * pofr)
        return voltage_estimate


    def _highest(self) -> tuple[float, float]:
        """Returns the highest voltage reading in the discharge profile."""
        ToReturn:tuple[float, float] = self._profile[0]
        for p in self._profile:
            if p[0] > ToReturn[0]:
                ToReturn = p
        return ToReturn
    
    def _lowest(self) -> tuple[float, float]:
        """Returns the lowest voltage reading in the discharge profile."""
        ToReturn:tuple[float, float] = self._profile[0]
        for p in self._profile:
            if p[0] < ToReturn[0]:
                ToReturn = p
        return ToReturn

    def _closest(self, voltage:float, count:int = 2) -> list[tuple[float, float]]:
        """Selects the closest known discharge readings that are closest to the voltage reading."""

        # assemble list
        ToReturn:list[tuple[float, float]] = []

        # find closest
        for _ in range(count):
            closest:tuple[float, float] = None
            for p in self._profile:
                if p not in ToReturn:
                    if closest == None: # if there isn't a closest yet (we are on the first one), just accept it as the closest for now so we can use it as a measuring stick.
                        closest = p
                    else:
                        closest_distance:float = abs(closest[0] - voltage)
                        this_distance:float = abs(voltage - p[0])
                        if this_distance < closest_distance:
                            closest = p
            ToReturn.append(closest)

        return ToReturn