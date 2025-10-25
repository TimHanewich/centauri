# SET VALUES
pitch_rate = -50000
roll_rate = 0
yaw_rate = 0
input_throttle_uint16 = 32768

pitch_kp = 5000
pitch_ki = 5000
pitch_kd = 5000
roll_kp = 0
roll_ki = 0
roll_kd = 0
yaw_kp = 0
yaw_ki = 0
yaw_kd = 0
i_limit = 25000

PID_SCALING_FACTOR = 10000

pitch_last_i = 0
roll_last_i = 0
yaw_last_i = 0
pitch_last_error = 0
roll_last_error = 0
yaw_last_error = 0

# convert the desired pitch, roll, and yaw from (-32,768 to 32,767) into (-90 to +90) degrees per second
# Multiply by 90,000 because we will interpret each as -90 d/s to +90 d/s
# We are multplying by 90,000 instead of 90,000 here so we can keep it in units of 1,000 and do integer math instead of floating point math
desired_pitch_rate:int = 50000
desired_roll_rate:int = 0
desired_yaw_rate:int = 0

# now compare those ACTUAL rates with the DESIRED rates (calculate error)
# error = desired - actual
error_pitch_rate:int = desired_pitch_rate - pitch_rate
error_roll_rate:int = desired_roll_rate - roll_rate
error_yaw_rate:int = desired_yaw_rate - yaw_rate
#print("ErrPitch: " + str(error_pitch_rate) + ", ErrRoll: " + str(error_roll_rate) + ", ErrYaw: " + str(error_yaw_rate))

# Pitch PID calculation
pitch_p:int = (error_pitch_rate * pitch_kp) // PID_SCALING_FACTOR
pitch_i:int = pitch_last_i + ((error_pitch_rate * pitch_ki) // PID_SCALING_FACTOR)
pitch_i = min(max(pitch_i, -i_limit), i_limit) # constrain within I limit
pitch_d = (pitch_kd * (error_pitch_rate - pitch_last_error)) // PID_SCALING_FACTOR
pitch_pid = pitch_p + pitch_i + pitch_d

# Roll PID calculation
roll_p:int = (error_roll_rate * roll_kp) // PID_SCALING_FACTOR
roll_i:int = roll_last_i + ((error_roll_rate * roll_ki) // PID_SCALING_FACTOR)
roll_i = min(max(roll_i, -i_limit), i_limit) # constrain within I limit
roll_d = (roll_kd * (error_roll_rate - roll_last_error)) // PID_SCALING_FACTOR
roll_pid = roll_p + roll_i + roll_d

# Yaw PID calculation
yaw_p:int = (error_yaw_rate * yaw_kp) // PID_SCALING_FACTOR
yaw_i:int = yaw_last_i + ((error_yaw_rate * yaw_ki) // PID_SCALING_FACTOR)
yaw_i = min(max(yaw_i, -i_limit), i_limit) # constrain within I limit
yaw_d = (yaw_kd * (error_yaw_rate - yaw_last_error)) // PID_SCALING_FACTOR
yaw_pid = yaw_p + yaw_i + yaw_d

# save state values for next loop
pitch_last_error = error_pitch_rate
roll_last_error = error_roll_rate
yaw_last_error = error_yaw_rate
pitch_last_i = pitch_i
roll_last_i = roll_i
yaw_last_i = yaw_i

# Calculate the mean pulse width the PWM signals will use
# each motor will then offset this a bit based on the PID values for each axis
# "pwm_pw" short for "Pulse Width Modulation Pulse Width"
mean_pwm_pw:int = 1000000 + (input_throttle_uint16 * 1000000) // 65535

# calculate throttle values for each motor using those PID influences
#print("Pitch PID: " + str(pitch_pid) + ", Roll PID: " + str(roll_pid) + ", Yaw Pid: " + str(yaw_pid))
m1_pwm_pw = mean_pwm_pw + pitch_pid + roll_pid - yaw_pid
m2_pwm_pw = mean_pwm_pw + pitch_pid - roll_pid + yaw_pid
m3_pwm_pw = mean_pwm_pw - pitch_pid + roll_pid + yaw_pid
m4_pwm_pw = mean_pwm_pw - pitch_pid - roll_pid - yaw_pid

print("M1: " + str(m1_pwm_pw))
print("M2: " + str(m2_pwm_pw))
print("M3: " + str(m3_pwm_pw))
print("M4: " + str(m4_pwm_pw))