import time

buffer:bytearray = bytearray(50)
data:bytes = b'\x9a\x1f\x03\x8c\x7f\x12'

# example 1
t1 = time.ticks_us()
buffer[10:10+len(data)] = data
t2 = time.ticks_us()
print("Example 1: " + str(t2 - t1) + " ticks us")

# example 2
t1 = time.ticks_us()
start_pos:int = 10
for i in range(len(data)):
    buffer[start_pos + i] = data[i]
t2 = time.ticks_us()
print("Example 2: " + str(t2 - t1) + " ticks us")

# example 3
mv = memoryview(buffer)
t1 = time.ticks_us()
mv[10:10+len(data)] = data
t2 = time.ticks_us()
print("Example 3: " + str(t2 - t1) + " ticks us")

print(buffer)