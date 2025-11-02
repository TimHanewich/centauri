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

# prepare for CSV file
rows:list[list] = []
rows.append(["Seconds", "Battery Voltage", "Pitch Rate", "Roll Rate", "Yaw Rate", "Input Throttle", "Input Pitch", "Input Roll", "Input Yaw", "M1 Throttle", "M2 Throttle", "M3 Throttle", "M4 Throttle"]) # append headers

# unpack
packets:list[bytes] = data.split("\r\n".encode())
for p in packets:
    if len(p) > 0:
        unpacked:dict = tools.unpack_packet(p)

        # construct this row
        newrow:list = []
        newrow.append(unpacked["ticks_ms"]/1000)
        newrow.append(round(unpacked["vbat"], 1))
        newrow.append(unpacked["pitch_rate"])
        newrow.append(unpacked["roll_rate"])
        newrow.append(unpacked["yaw_rate"])
        newrow.append(unpacked["input_throttle"])
        newrow.append(unpacked["input_pitch"])
        newrow.append(unpacked["input_roll"])
        newrow.append(unpacked["input_yaw"])
        newrow.append(unpacked["m1_throttle"])
        newrow.append(unpacked["m2_throttle"])
        newrow.append(unpacked["m3_throttle"])
        newrow.append(unpacked["m4_throttle"])

        # append to rows
        rows.append(newrow)

# save to output
output = open(path_csv, "w", newline="")
writer = csv.writer(output)
writer.writerows(rows)
output.close()

# confirm
print("Output complete!")