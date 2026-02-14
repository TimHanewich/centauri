# Question to be answered:
# What Throttle = ~99%, Roll = ~-32%, Roll = 0, Yaw = 0 happens to pass a checksum

throttle_uint16_min:int = 64_224
throttle_uint16_max:int = 65_535

pitch_int16_min:int = -10_158
pitch_int16_max:int = -10_814

for throttle in range (throttle_uint16_min, throttle_uint16_max):
    for pitch in range(pitch_int16_min, pitch_int16_max):

        # construct
        packet:bytearray = bytearray()
        packet.append(0b00000000) # header
        packet.append(throttle.to_bytes(2, "big"))
        packet.append(pitch.to_bytes(2, "big"))
        packet.extend([0, 0]) # 