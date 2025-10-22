pitch_kp = 437
pitch_ki = 100
pitch_kd = 100

# I and D relevant terms for testing
pitch_last_i = 9
pitch_last_error = 2

error_pitch_rate = 30
PID_SCALING_FACTOR = 1000
i_limit = 65000
cycle_time_us = 4000


# Pitch PID calculation
pitch_p:int = (error_pitch_rate * pitch_kp) // PID_SCALING_FACTOR
pitch_i:int = pitch_last_i + ((error_pitch_rate * pitch_ki) // PID_SCALING_FACTOR)
pitch_i = min(max(pitch_i, -i_limit), i_limit) # constrain within I limit
pitch_d = (pitch_kd * (error_pitch_rate - pitch_last_error)) // (PID_SCALING_FACTOR) # would make more visual sense to divide the entire thing by the scaling factor, but for precision purposes, better to only integer divide ONCE by one big number than do it twice.
pitch_pid = pitch_p + pitch_i + pitch_d

print("P: " + str(pitch_p))
print("I: " + str(pitch_i))
print("D: " + str(pitch_d))
print("Pitch PID: " + str(pitch_pid))