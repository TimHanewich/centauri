f = open(r"C:\Users\timh\Downloads\tah\centauri\components\quadcopter\src\log", "rb")
data = f.read()
f.close()

frames = data.split("\r\n".encode())

for frame in frames:
    if len(frame) > 0:
        print(str(frame[18] * 10) + " ms")