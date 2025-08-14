import struct

def unpack_settings_update(data:bytes) -> dict:

    # validate checksum
    checksum:int = data[41] # get checksum: should be the 42nd byte in, which would be index 41
    selfchecksum:int = 0x00
    for byte in data[0:41]: # first 41 bytes (not including checksum)
        selfchecksum = selfchecksum ^ byte
    if selfchecksum != checksum: # if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return None
    
    # the first byte is a header byte, so ignore that. Assume the provided data was already validated to be a settings update packet.
    
    # unpack pitch values
    pitch_kp:float = struct.unpack("f", data[1:5])[0]
    pitch_ki:float = struct.unpack("f", data[5:9])[0]
    pitch_kd:float = struct.unpack("f", data[9:13])[0]

    # unpack roll values
    roll_kp:float = struct.unpack("f", data[13:17])[0]
    roll_ki:float = struct.unpack("f", data[17:21])[0]
    roll_kd:float = struct.unpack("f", data[21:25])[0]

    # unpack yaw values
    yaw_kp:float = struct.unpack("f", data[25:29])[0]
    yaw_ki:float = struct.unpack("f", data[29:33])[0]
    yaw_kd:float = struct.unpack("f", data[33:37])[0]

    # unpack i limit
    i_limit:float = struct.unpack("f", data[37:41])[0]

    # return
    return {"pitch_kp": pitch_kp, "pitch_ki": pitch_ki, "pitch_kd": pitch_kd, "roll_kp": roll_kp, "roll_ki": roll_ki, "roll_kd": roll_kd, "yaw_kp": yaw_kp, "yaw_ki": yaw_ki, "yaw_kd": yaw_kd, "i_limit": i_limit}


data = b'\x00\x9e\xef\xe7>\n\xd7#?\xcb\xa1\xa5>\x19\x04\xa6>\x9b\xe6]>\x8f\xc2u>^\xba\xc9>5^z?\x10Xy?{\x14\xae>\xc9'
u = unpack_settings_update(data)
print(u)