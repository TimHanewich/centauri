import random

temp_telemetry_storage_len:int = 5000                    # how many bytes our temporary storage will be (fixed length)
temp_telemetry_storage:bytearray = bytearray(5000)       # create it
temp_telemetry_storage_used:int = 0                      # counter that keeps track of how many bytes of the predefined fixed length temp storage are used up

# declare some random sample data
sample_data:bytes = b'12345'

# simulate adding to it
for _ in range(random.randint(5, 30)):

    if (temp_telemetry_storage_len - temp_telemetry_storage_used) > 5: # if we have room for another
        
        # add it
        temp_telemetry_storage[temp_telemetry_storage_used:temp_telemetry_storage_used + 5] = sample_data

        # increment how many bytes are added
        temp_telemetry_storage_used = temp_telemetry_storage_used + 5
    

# now flush to flash storage (local storage)
log = open("./log", "ab")
for i in range(temp_telemetry_storage_used):
    log.write(bytes(temp_telemetry_storage[i]))
log.close()

# now entirely clear out bytearray (set to all 0s)
for i in range(temp_telemetry_storage_len):
    temp_telemetry_storage[i] = 0
temp_telemetry_storage_used = 0 # reset used counter

print(temp_telemetry_storage)
print(temp_telemetry_storage_used)