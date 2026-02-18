import tools
import csv

# get the path of the log file
path_log:str = input("Path of log file? ")
path_log = path_log.replace("\"", "")

# unpack the log
packets:tools.DataPacket = tools.unpack_log(path_log)
print(str(len(packets)) + " logs unpacked")

# get the path of the output file (csv)
path_csv:str = input("Path of output CSV file? ")
path_csv = path_csv.replace("\"", "")

# construct into a CSV file
print("Preparing CSV...")
rows:list[list] = []
rows.append(["Seconds", "Battery Voltage", "Pitch Rate", "Roll Rate", "Yaw Rate", "Pitch Angle", "Roll Angle", "G-Force", "Input Throttle", "Input Pitch", "Input Roll", "Input Yaw", "M1 Throttle", "M2 Throttle", "M3 Throttle", "M4 Throttle", "Cmd Last Received ms"]) # append headers
for packet in packets:

    # construct this row
    newrow:list = []
    newrow.append(packet.ticks_ms/1000) # convert ticks_ms to seconds
    newrow.append(round(packet.vbat, 1))
    newrow.append(packet.pitch_rate)
    newrow.append(packet.roll_rate)
    newrow.append(packet.yaw_rate)
    newrow.append(packet.pitch_angle)
    newrow.append(packet.roll_angle)
    newrow.append(packet.gforce)
    newrow.append(packet.input_throtte)
    newrow.append(packet.input_pitch)
    newrow.append(packet.input_roll)
    newrow.append(packet.input_yaw)
    newrow.append(packet.m1_throttle)
    newrow.append(packet.m2_throttle)
    newrow.append(packet.m3_throttle)
    newrow.append(packet.m4_throttle)
    newrow.append(packet.lrecv_ms)

    # append to rows
    rows.append(newrow)

# save to output
print("Saving CSV...")
output = open(path_csv, "w", newline="")
writer = csv.writer(output)
writer.writerows(rows)
output.close()

# confirm
print("Output complete!")