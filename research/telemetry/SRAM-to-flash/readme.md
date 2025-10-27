# SRAM to Flash Method of Saving Telemetry
Writing directly to flash memory (storage) is too slow. The file writing process alone can be up to 40,000 us! (40 ms!)

So the new method: while in flight, all telemetry will be saved to memory. A large bytearray that *eventually* fills up, but has enough room for a significant flight time (like > 5 mins of flight time). Then, once a control command is received with 0% throttle (unarmed), it will momentarily "flush" the contents of the bytearray to flash storage and then clear out the bytearray.