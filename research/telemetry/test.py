import time
import os
import random

# check how much space is available
stats:tuple = os.statvfs('/')
block_size:int = stats[0]
free_blocks:int = stats[3]
free_space:int = block_size * free_blocks
print("Free bytes on local storage: " + str(free_space) + " bytes")
available_bytes:int = free_space - 10 # 10 byte buffer to avoid getting too close
print("Available space to write to in local storage: " + str(available_bytes) + " bytes")

# calculate how many telemetry "frames" we can fit in storage
telemetry_frame_size:int = 16 # how many bytes each telemetry frame consists of, including the terminator (i.e. \r\n)
frames_remaining:int = available_bytes // telemetry_frame_size
print("Onboard storage is sufficient to store " + str(frames_remaining) + " telemetry frames")

# open an onboard log file for all telemetry
print("Creating onboard telemetry log...")
log = open("log", "ab") # open a file called "log" on the local storage at root level, appending binary data (bytes) - if it already exists, it will continue. if it doesn't exist, it will be created
def logtel(data:bytes) -> None: 
    """Short for 'log telemetry', logs data to the onboard telemetry log."""
    log.write(data)

# establish a bytearray to update
ToWrite:bytearray = bytearray(16)

# test writing with some sample data
for _ in range(20):
    
    # randomize values in it
    for i in range(telemetry_frame_size):
        ToWrite[i] = random.randint(0, 255)
    
    # write it, if we have space
    if frames_remaining > 0:

        # write it, timing it
        t1 = time.ticks_us()
        logtel(ToWrite)
        t2 = time.ticks_us()
        elapsed = t2 - t1 # usually 65-85 us I am finding, but occasionally peaks to like 40,000
        print("Elapsed: " + str(elapsed) + " us")

        # decrement the number of telemetry frames we have space for
        frames_remaining = frames_remaining - 1