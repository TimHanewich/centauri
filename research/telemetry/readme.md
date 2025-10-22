# Telemetry Logging
Considering logging telemetry to the local storage on the Pico during flight - more telemetry and a higher frequency during flight. For it to be recovered afterwards.

## Example Telemetry Logging Test:
```
import time

TELLOG = open("log", "ab")

def log(data:bytes) -> None:
    TELLOG.write(data)
   
datatowrite = b'\x01\x02\x03\x04'

for _ in range(30):
    t1 = time.ticks_us()
    log(datatowrite)
    t2 = time.ticks_us()
    elapsed = t2 - t1 # usually 65-85 us I am finding, but occasionally peaks to like 40,000
    print("Elapsed: " + str(elapsed) + " us")
```

## Example Checking Space Available
```
import os

# Get filesystem statistics for the root directory
stats = os.statvfs('/')

# Calculate total, free, and used space in bytes
block_size = stats[0]
total_blocks = stats[2]
free_blocks  = stats[3]

total_space = block_size * total_blocks
free_space  = block_size * free_blocks
used_space  = total_space - free_space

print("Total space:", total_space, "bytes")
print("Used space:", used_space, "bytes")
print("Free space:", free_space, "bytes")
```

## Storing in RAM, writing after flight
As described in [this Copilot chat](https://copilot.microsoft.com/shares/JzxN3dbfughS6k3pUbycm), the best thing to explore is probably saving all telemetry just to RAM during flight and THEN once flight is over, writing to storage. I should do the math with the available remaining RAM to see how much flight time (i.e. 60 seconds?) I can store in RAM alone. And if I exceed this or go beyond a pre-defined buffer length, just overwrite the old data. so it only keeps the last 60 seconds or whatever maybe.