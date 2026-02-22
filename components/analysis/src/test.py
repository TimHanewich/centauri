import tools

path = r"C:\Users\timh\Downloads\log (3)"

packets = tools.unpack_log(path)
print(str(len(packets)) + " packets")

# stats
stats = tools.ExtractStats(packets)

for stat in stats:
    print(stat.gforce_min)