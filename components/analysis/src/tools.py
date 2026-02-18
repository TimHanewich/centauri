class DataPacket:
    def __init__(self):
        self.ticks_ms:int = 0
        self.vbat:float = 0.0
        self.pitch_rate:int = 0
        self.roll_rate:int = 0
        self.yaw_rate:int = 0
        self.pitch_angle:int = 0
        self.roll_angle:int = 0
        self.gforce:float = 0.0
        self.input_throtte:int = 0
        self.input_pitch:int = 0
        self.input_roll:int = 0
        self.input_yaw:int = 0
        self.m1_throttle:int = 0
        self.m2_throttle:int = 0
        self.m3_throttle:int = 0
        self.m4_throttle:int = 0
        self.lrecv_ms:int = 0

    def unpack(self, data:bytes) -> None:

        # extract timestamp (in ms)
        ticks_ms:int = data[0] << 16 | data[1] << 8 | data[2]

        # extract battery reading
        # the battery voltage will come in 10x what it is - so 168 would be 16.8, 60 would be 6.0
        # so just divide by 10 to get the actual value (as a float)
        vbat:float = data[3] / 10

        # rates
        pitch_rate:int = data[4] - 128
        roll_rate:int = data[5] - 128
        yaw_rate:int = data[6] - 128

        # angles
        pitch_angle:int = data[7] - 128
        roll_angle:int = data[8] - 128

        # gforce
        gforce:int = data[9] / 10 # divide by 10 because it is stored as 10x what it is, like vbat!

        # inputs
        input_throttle:int = data[10]     # flat percentage (0-100)
        input_pitch:int = data[11] - 100  # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
        input_roll:int = data[12] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
        input_yaw:int = data[13] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives

        # motor throttles
        m1_throttle:int = data[14]
        m2_throttle:int = data[15]
        m3_throttle:int = data[16]
        m4_throttle:int = data[17]

        # last received command control pack, in ms ago
        # it is encoded in increments of 10, so multiply by 10!
        lrecv_ms:int = data[18] * 10

        # Save all
        self.ticks_ms = ticks_ms
        self.vbat = vbat
        self.pitch_rate = pitch_rate
        self.roll_rate = roll_rate
        self.yaw_rate = yaw_rate
        self.pitch_angle = pitch_angle
        self.roll_angle = roll_angle
        self.gforce = gforce
        self.input_throtte = input_throttle
        self.input_pitch = input_pitch
        self.input_roll = input_roll
        self.input_yaw = input_yaw
        self.m1_throttle = m1_throttle
        self.m2_throttle = m2_throttle
        self.m3_throttle = m3_throttle
        self.m4_throttle = m4_throttle
        self.lrecv_ms = lrecv_ms

def unpack_log(log_path:str) -> list[DataPacket]:

    # extract data from the file
    f = open(log_path, "rb")
    data:bytes = f.read()
    f.close()

    # unpack each, one by one
    lines:list[bytes] = data.split("\r\n".encode())
    packets:list[DataPacket] = []
    for p in lines:
        if len(p) > 0:
            try:
                dp:DataPacket = DataPacket()
                dp.unpack(p)
                packets.append(dp)
            except Exception as ex:
                print("Unpacking a frame failed. Skipping. Err: " + str(ex))
    
    return packets

class ArmedFlightStats:
    def __init__(self):
        self.duration_seconds:float = 0.0        # duration that it was armed, in seconds
        self.vbat_max:float = 0.0                # max vbat during flight
        self.vbat_min:float = 0.0                # min vbat during flight
        self.gforce_max:float = 0.0              # highest g-force experienced during flight
        self.gforce_min:float = 0.0              # lowest g-force experienced during flight
        self.throttle_avg:float = 0.0            # average throttle input during flight
        self.rx_issue_ratio:float = 0.0          # what % of the packets had lrecv > 100ms (Rx issue)

def ExtractStats(packets:list[DataPacket]) -> list[ArmedFlightStats]:

    # Step 1: group the into armed groups
    ArmedFlights:list[list[DataPacket]] = []
    current:list[DataPacket] = None
    for packet in packets:
        if packet.input_throtte > 0:
            if current == None:
                current = []
            current.append(packet)
        else: # throttle = 0 (unarmed)
            if current != None:
                ArmedFlights.append(current)
                current = None

    
        


    ToReturn:list[ArmedFlightStats] = []
        