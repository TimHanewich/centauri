# ==============================================================================
# CENTAURI ANALYSIS SCRIPT
# https://github.com/TimHanewich/centauri
# ==============================================================================
# Copyright (C) 2026 Tim Hanewich
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tools
import csv

# get the path of the log file
path_log:str = input("Path of log file? ")
path_log = path_log.replace("\"", "")

# unpack the log into packets
packets:tools.DataPacket = tools.unpack_log(path_log)
print(str(len(packets)) + " logs unpacked")

# perform statistics crunch
AllStats:list[tools.ArmedFlightStats] = tools.ExtractStats(packets)
print()
for i in range(len(AllStats)):
    stats:tools.ArmedFlightStats = AllStats[i]
    print("FLIGHT #" + str(i+1))
    print("\t" + "Began @ " + str(round(stats.began_at, 1)) + "s, Ended @ " + str(round(stats.ended_at, 1)) + "s")
    print("\t" + "Duration: " + str(int(round(stats.duration_seconds, 0))) + " seconds")
    print("\t" + "vbat: " + str(round(stats.vbat_min, 1)) + " - " + str(round(stats.vbat_max, 1)))
    print("\t" + "gforce: " + str(round(stats.gforce_min, 1)) + " - " + str(round(stats.gforce_max, 1)))
    print("\t" + "Avg. Throttle: " + str(round(stats.throttle_avg, 1)) + "%")
    print("\t" + "Max LRecv: " + str(stats.lrecv_max_ms) + " ms")
    print("\t" + "Avg LRecv: " + str(stats.lrecv_avg_ms) + " ms")
    print()


# get the path of the output file (csv)
path_csv:str = input("Path of output CSV file? (enter nothing to exit) ")
if path_csv == "":
    exit()
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