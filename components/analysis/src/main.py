import tools
import csv

# get the path of the log file
path_log:str = input("Path of log file? ")

# get the path of the output file (csv)
path_csv:str = input("Path of output CSV file? ")

# extract data from the file
f = open(path_log, "rb")
data:bytes = f.read()
f.close()

# unpack each, one by one
lines:list[bytes] = data.split("\r\n".encode())
print(str(len(lines)) + " frames in log file.")
packets:list[dict] = []
for p in lines:
    if len(p) > 0:
        unpacked:dict = tools.unpack_packet(p)
        packets.append(unpacked)
print(str(len(packets)) + " packets unpacked")  

# construct into a CSV file
print("Preparing CSV...")
rows:list[list] = []
rows.append(["Seconds", "Battery Voltage", "Pitch Rate", "Roll Rate", "Yaw Rate", "Input Throttle", "Input Pitch", "Input Roll", "Input Yaw", "M1 Throttle", "M2 Throttle", "M3 Throttle", "M4 Throttle"]) # append headers
for packet in packets:

    # construct this row
    newrow:list = []
    newrow.append(packet["ticks_ms"]/1000)
    newrow.append(round(packet["vbat"], 1))
    newrow.append(packet["pitch_rate"])
    newrow.append(packet["roll_rate"])
    newrow.append(packet["yaw_rate"])
    newrow.append(packet["input_throttle"])
    newrow.append(packet["input_pitch"])
    newrow.append(packet["input_roll"])
    newrow.append(packet["input_yaw"])
    newrow.append(packet["m1_throttle"])
    newrow.append(packet["m2_throttle"])
    newrow.append(packet["m3_throttle"])
    newrow.append(packet["m4_throttle"])

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